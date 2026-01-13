from typing import Any, Dict
import pandas as pd
import numpy as np
from openai import APIError, OpenAI
from google import genai
import io
import re
import tiktoken
from google.genai import types
from syntaxmatrix import profiles as _prof
from ..gpt_models_latest import set_args as _set_args, extract_output_text as _out

class OrchestrateMLSystem:
    def __init__(self, user_question, dataset_path):
        self.user_query = user_question
        self.dataset_path = dataset_path
        self.df = None
        self.cot_history = {}  # To store chain-of-thought history for each agents
       

    def _generate_ml_response(self, profile, sys_prompt, user_prompt, max_output_tokens = 4000, reasoning_summary="auto"):
        """Helper to specifically extract text from Gemini 3 and ignore thought parts."""
        
        profile['client'] = _prof.get_client(profile)
        client = profile["client"]
        model = profile["model"]
        provider = profile["provider"].lower()

        usage = {
            "provider": provider,
            "model": model,
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
        }

        def openai_sdk_response():
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
            )

            full_text = response.choices[0].message.content

            # Simple heuristic to split thought and text if formatted as such
            thought_match = re.search(r'THOUGHT:(.*)TEXT:', full_text, re.DOTALL)
            if thought_match:
                thought = thought_match.group(1).strip()
                text = full_text[thought_match.end():].strip()
            else:
                thought = ""
                text = full_text.strip()

            usage["input_tokens"] = response.usage.prompt_tokens
            usage["output_tokens"] = response.usage.completion_tokens
            usage["total_tokens"] = response.usage.total_tokens

            return thought, text, usage


        if provider == "google":            
            response = client.models.generate_content(
                model=model,
                contents=f"{sys_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    temperature=0.1 
                )
            )
            # Gemini 3 returns multiple parts (thought + text). 
            # Extract ONLY the text parts to prevent 'thought_signature' warnings.
            parts = response.candidates[0].content.parts

            thought = "".join([part.thought for part in response.candidates[0].content.parts if hasattr(part, 'thought') and part.thought])

            text = "".join([part.text for part in parts if part.text is not None])

            um = response.usage_metadata
            usage["input_tokens"] = um.prompt_token_count
            usage["output_tokens"] = um.candidates_token_count + (um.thoughts_token_count if um.thoughts_token_count is not None else 0)
            usage["total_tokens"] = um.total_token_count

            return thought, text, usage
        

        if provider == "openai":
            if int(model.split("gpt-")[1][0])>=5:

                def reasoning_and_verbosity():
                    reasoning_effort, verbosity = "medium", "medium" 
                    if "mini" not in model:
                        if model == "gpt-5-nano":
                            reasoning_effort = "low"
                        else: reasoning_effort, verbosity = "high", "high" 
                                        
                    return reasoning_effort, verbosity

                reasoning, verbosity = reasoning_and_verbosity()
                if reasoning in ["medium", "high"]:
                    if (max_output_tokens or 0) < 6000:
                        max_output_tokens = 6000

                
                # Build request kwargs (NO reasoning.effort — gpt-5-mini rejects it)
                req = dict(
                    model=model,
                    input=user_prompt,
                    instructions=sys_prompt,
                    max_output_tokens=max_output_tokens,
                    reasoning={
                        "effort": reasoning,
                        "summary": "auto"
                    },
                    text={"verbosity": verbosity},
                )

                # Ask for reasoning summary only if requested; some org/model combos may reject it,
                # so retry without reasoning if that happens.
                if reasoning_summary:
                    req["reasoning"] = {"summary": reasoning_summary}

                try:
                    response = client.responses.create(**req)
                except Exception as e:
                    msg = str(e)
                    # If summaries aren't supported in your setup, retry without reasoning altogether.
                    if ("reasoning.summary" in msg) or ("reasoning" in msg and "Unsupported parameter" in msg):
                        req.pop("reasoning", None)
                        response = client.responses.create(**req)
                    else:
                        raise

                # --- Extract raw output text (don't .strip()) ---
                raw_text = getattr(response, "output_text", None) or ""
                if not raw_text:
                    # Fallback: walk the output items (covers SDK edge cases)
                    chunks = []
                    for item in (getattr(response, "output", None) or []):
                        if getattr(item, "type", None) == "message":
                            for c in (getattr(item, "content", None) or []):
                                if getattr(c, "type", None) in ("output_text", "text"):
                                    chunks.append(getattr(c, "text", "") or "")
                    raw_text = "".join(chunks)

                # --- Reasoning summary (if present) ---
                reasoning = None
                for item in (getattr(response, "output", None) or []):
                    if getattr(item, "type", None) == "reasoning":
                        summ = getattr(item, "summary", None) or []
                        if summ:
                            reasoning = getattr(summ[0], "text", None)
                        break

                # --- Return raw code as-is; if model disobeys and wraps ```...```, unwrap once ---
                code = raw_text
                m = re.search(r"```(?:python)?\s*\n(.*?)```", raw_text, flags=re.DOTALL | re.IGNORECASE)
                if m:
                    code = m.group(1)  # keep inner code exactly (no strip)

                # --- Usage ---
                if getattr(response, "usage", None):
                    um = response.usage
                    usage["input_tokens"] = getattr(um, "input_tokens", None)
                    usage["output_tokens"] = getattr(um, "output_tokens", None)
                    usage["total_tokens"] = getattr(um, "total_tokens", None)

                return reasoning, code, usage
            else:
                return openai_sdk_response()


        if provider == "anthropic":
            msg = client.messages.create(
                model=model,
                max_tokens=max_output_tokens,
                system=sys_prompt,   # top-level system param (Messages API)
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.1,
            )

            # Claude returns content blocks; join only text blocks.
            # IMPORTANT: return raw code exactly as provided (no .strip()).
            code_parts = []
            for block in (getattr(msg, "content", None) or []):
                btype = getattr(block, "type", None)
                if btype == "text":
                    code_parts.append(getattr(block, "text", "") or "")
            raw_code = "".join(code_parts)

            # Usage
            um = getattr(msg, "usage", None)
            if um is not None:
                usage["input_tokens"] = getattr(um, "input_tokens", None)
                usage["output_tokens"] = getattr(um, "output_tokens", None)
                if usage["input_tokens"] is not None and usage["output_tokens"] is not None:
                    usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]

            # No separate reasoning returned in this minimal mode
            return None, raw_code, usage
        
        return openai_sdk_response()
         
                
    def operator_agent(self) -> str:
        """The main entry point. Returns a pure string of runnable code."""
        # 1. Initialize DataFrame
        df = pd.read_csv(self.dataset_path)
        
        # 2. Dynamic Context Generation
        buffer = io.StringIO()
        df.info(buf=buffer)
        df_context = f"""
        SCHEMA: {buffer.getvalue()}
        NULLS: {df.isnull().sum().to_string()}
        STATS: {df.describe(include='all').to_string()}"
        SAMPLE: {df.head(3).to_string()}
        """

        # 2. Refiner Agent (Generates Task Specs + CoT)
        ref_thought, ref_tasks, ref_usage = self.refiner_agent(df_context, self.user_query)
        self.cot_history["Refiner"] = {"thought": ref_thought, "tasks": ref_tasks, "usage": ref_usage}
    
        # 3. Coder Agent (Generates Runnable Code + CoT)
        thought, text, usage = self.coder_agent(df_context, ref_tasks)
        self.cot_history["Coder"] = {"thought": thought, "code": text, "usage": usage}
        # Return structured result
        return {
            "specs_cot": ref_tasks,
            "python_code": text,
            "token_usage": self.cot_history,
        }

    
    def refiner_agent(self, context, query):
        """Categorizes the ML job and selects the specific Viz Template."""
        
        # refined_profile = _prof.get_profile("imagetexter") or _prof.get_profile("admin") 
        # refined_profile["client"] = _prof.get_client(refined_profile) 
        
        sys_prompt = f"""
        You are the 'Refiner Agent'. Your role is to transform a natural language query into a strict ML technical specification.
        """
        user_prompt = f"""
        DATASET CONTEXT:
        {context}
        
        USER QUERY:
        {query}

        STEP 1: Identify the ML Job Category from this master list:
        - Supervised: Classification, Regression.
        - Unsupervised: Clustering, Dimensionality Reduction, Anomaly Detection, Density Estimation.
        - Hybrid/Other: RL, Recommendation, Ranking, Time Series Forecasting, Seq2Seq, Generative Modeling, Similarity Learning.
        - Advanced: Meta-Learning, Causal Inference, Survival Analysis, Multi-Task Learning, Imitation Learning.

        STEP 2: Map the logic. 
        - Identify X (features) and y (target).
        - If the user asks for a derived column (e.g., 'If A > B then 1'), provide the specific NumPy/Pandas logic.

        STEP 3: Select the Visualization Template. Provide the coder with the specific plotting code structure for that category:
        - CLASSIFICATION: Confusion Matrix Heatmap, ROC Curve, Feature Importance Bar.
        - REGRESSION: Pred vs. Actual Scatter, Residuals Plot, Error Distribution.
        - CLUSTERING: PCA-based Cluster Scatter, Elbow/Silhouette Plot.
        - TIME SERIES: Line plot (Train/Test/Forecast), Seasonal Decomposition.
        - ANOMALY: Scatter with Outlier Highlighting.
        - RECSYS/RANKING: Precision@K or Recall@K Curves.

        STEP 4: Chain-of-Thought (CoT) for Coder:
        1. Mandatory Cleaning: Check for Nulls. Impute numbers with median, strings with mode.
        2. Encoding: Convert objects to categories/numbers.
        3. Scaling: Apply StandardScaler for distance-based tasks.
        4. Modeling: Select the best algorithm for the task (e.g., XGBoost, K-Means, ARIMA).
        5. Evaluation: Calculate appropriate metrics (F1, RMSE, R2, etc.).
        
        Pre-empt loop-holds: If the query is vague, assume reasonable defaults based on the column types. 
        Return ONLY the refined technical specification.
        """
        refiner_profile = _prof.get_profile("classifier") or _prof.get_profile("chat") or _prof.get_profile("admin")
        if not refiner_profile:
            return "Error: Set an appropriate classifier profile"
        
        thought, text, usage = self._generate_ml_response(refiner_profile, sys_prompt, user_prompt)
        return thought, text, usage
     

    def coder_agent(self, context, refined_tasks):
        """Generates the code using the spec. Task-agnostic."""
        
        system_prompt = f"""
        You are the 'Coder Agent'. Generate a robust, production-ready Python script.
        """
        user_prompt = f"""
        DATASET CONTEXT:
        {context}
        
        REFINED ML TASKS & SPECS:
        {refined_tasks}

        CONSTRAINTS:
        - Assume 'df' is already loaded in the namespace. Do not use pd.read_csv.
        - Include all up-to-dateimports (pandas, numpy, sklearn, matplotlib, seaborn, etc.). 
        - Avoid any deprecated mehods, imports, statements.
        - FIRST: Implement the 'Cold Start' cleaning and preprocessing logic (Check for nulls and impute based on column types in context).
        - SECOND: (Modeling) Implement the ML pipeline (Split, Scale, Train, Predict).
        - THIRD: Implement the visualizations using the specific templates requested.
        - Return ONLY the executable Python code. NO MARKDOWN (```), NO EXPLANATION.

        PLOTS:
        - Ensure that you display all the figures that you plotted nicely using plt.show.

        TABLES:
        - Use html tables for tabular data. 
        """
        coder_profile = _prof.get_profile("coder")
        if not coder_profile:
            return "Error!: Set an appropriate coder profile"

        thought, raw_code, usage = self._generate_ml_response(coder_profile ,system_prompt, user_prompt)

        # Robustly strip any potential markdown formatting
        code = re.sub(r'```python|```', '', raw_code).strip()
        return thought, code, usage
    
