# syntaxmatrix/agents.py
from __future__ import annotations
import os, re, json, textwrap, requests
import pandas as pd
import uuid
import io
from typing import Optional, List, Any, Dict

from syntaxmatrix import utils
from syntaxmatrix.settings.model_map import GPT_MODELS_LATEST
from .. import profiles as _prof
from ..gpt_models_latest import set_args as _set_args, extract_output_text as _out
from google.genai import types 
import tiktoken
from google.genai.errors import APIError

from io import BytesIO
from PIL import Image

from dataclasses import dataclass
import hashlib
from PIL import Image
from syntaxmatrix.page_layout_contract import normalise_layout, validate_layout


def token_calculator(total_input_content, llm_profile):

    _client = llm_profile["client"]
    _model = llm_profile["model"]
    _provider = llm_profile["provider"].lower()
    
    if _provider == "google":
        tok = _client.models.count_tokens(
            model=_model,
            contents=total_input_content
        )
        input_prompt_tokens = tok.total_tokens
        return input_prompt_tokens
    
    elif _provider == "anthropic":
        tok = _client.beta.messages.count_tokens(
            model=_model,
            system="calculate the total token for the given prompt",
            messages=[{"role": "user", "content": total_input_content}]
        )
        input_prompt_tokens = tok.input_tokens
        return input_prompt_tokens

    else:
        enc = tiktoken.encoding_for_model(_model)
        input_prompt_tokens = len(enc.encode(total_input_content))
        return input_prompt_tokens    

def mlearning_agent(user_prompt, system_prompt, coder_profile):
    """
    Returns:
        (text, usage_dict)

    usage_dict schema (best-effort, depending on provider):
        {
            "provider": str,
            "model": str,
            "input_tokens": int|None,
            "output_tokens": int|None,
            "total_tokens": int|None,
            "error": str|None
        }
    """

    _coder_profile = _prof.get_profile('coder')
    _coder_profile['client'] = _prof.get_client(_coder_profile)
    _client = _coder_profile['client']
    _provider = _coder_profile["provider"].lower()
    _model = _coder_profile["model"]

    usage = {
        "provider": _provider,
        "model": _model,
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }

    def _clean_text(t):
        if t is None:
            return ""
        if not isinstance(t, str):
            t = str(t)
        return t.strip()

    def _get_usage_val(u, keys):
        """Read usage fields from dicts or objects, resiliently."""
        if u is None:
            return None
        for k in keys:
            try:
                if isinstance(u, dict) and k in u:
                    return u[k]
                if hasattr(u, k):
                    return getattr(u, k)
            except Exception:
                continue
        return None

    # Google
    def google_generate_code():
        nonlocal usage
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            # Optional: Force the model to generate a Python code block as JSON
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "code": types.Schema(type=types.Type.STRING, description="The runnable Python code."),
                    "explanation": types.Schema(type=types.Type.STRING, description="A brief explanation of the code."),
                },
                required=["code"]
            ),
        )

        try:
            response = _client.models.generate_content(
                model=_model,
                contents=user_prompt,
                config=config,
            )
        except Exception as e:
            return f"An error occurred during API call: {e}"

        # 3. Token Usage Capture and Context Overhead Calculation
        um = response.usage_metadata
        usage["input_tokens"] = um.prompt_token_count
        usage["output_tokens"] = um.candidates_token_count + um.thoughts_token_count
        usage["total_tokens"] = um.total_token_count

        try:
            # The response text will be a JSON string due to the config.
            response_json = json.loads(response.text)
            return response_json.get("code", "Error: Code field not found in response.")
        except Exception as e:
            return f"Error parsing response as JSON: {e}\nRaw Response: {response.text}"

    # OpenAI Responses API
    def gpt_models_latest_generate_code():
        nonlocal usage

        def reasoning_and_verbosity():
            reasoning_effort, verbosity = "medium", "medium" 
            if _model == "gpt-5-nano":
                reasoning_effort, verbosity = "low", "low"
            elif _model in ["gpt-5-mini", "gpt-5-mini-codex"]:
                reasoning_effort, verbosity = "medium", "medium"
            elif _model in ["gpt-5", "gpt-5-codex", "gpt-5-pro"]:
                reasoning_effort, verbosity = "high", "high"
            return (reasoning_effort, verbosity)
        try:
            args = _set_args(
                model=_model,
                instructions=system_prompt,
                input=user_prompt,
                previous_id=None,
                store=False,
                reasoning_effort=reasoning_and_verbosity()[0],
                verbosity=reasoning_and_verbosity()[1],
            )
            resp = _client.responses.create(**args)
            
            um = resp.usage
            usage["input_tokens"] = um.input_tokens
            usage["output_tokens"] = um.output_tokens
            usage["total_tokens"] = um.total_tokens

            code = _out(resp).strip()
            if code: 
                return code  

        except APIError as e:
            # IMPORTANT: return VALID PYTHON so the dashboard can show the error
            msg = f"I smxAI have instructed {e}"
            return (
                f"# {msg}\n"
                "from syntaxmatrix.display import show\n"
                f"show({msg!r})\n"
            )
        
        except Exception as e:
            # IMPORTANT: return VALID PYTHON so the dashboard can show the error
            msg = f"I smxAI have instructed {e}"
            return (
                f"# {msg}\n"
                "from syntaxmatrix.display import show\n"
                f"show({msg!r})\n"
            )

    # Anthropic
    def anthropic_generate_code():  
            
        try:        
            resp = _client.messages.create(
                model=_model,
                temperature=0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            um = resp.usage
            usage["input_tokens"] = um.input_tokens
            usage["output_tokens"] = um.output_tokens
            usage["total_tokens"] = um.input_tokens + um.output_tokens
                
            # Extract plain text from Claude-style content blocks
            text_blocks = []
            content = getattr(resp, "content", None) or []
            for block in content:
                t = getattr(block, "text", None)
                if not t and isinstance(block, dict):
                    t = (block.get("text") or "").strip()
                if t:
                    text_blocks.append(str(t))

            text = "\n".join(text_blocks).strip()
            if text:
                return text

            stop_reason = getattr(resp, "stop_reason", None)
            if stop_reason and stop_reason != "end_turn":
                raise RuntimeError(f"{_model} stopped with reason: {stop_reason}")
            raise RuntimeError(f"{_model} returned an empty response in this section due to insufficient data.")
        
        except Exception as e:
            msg = f"I smxAI have instructed {e}\n"
            return (
                f"# {msg}\n"
                "from syntaxmatrix.display import show\n"
                f"show({msg!r})\n"
            )

    # OpenAI Chat Completions
    def openai_sdk_generate_code():
        nonlocal usage
        try:
            response = None
            if _model == "deepseek-reasoner":
                response = _client.chat.completions.create(
                    model=_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    extra_body={"thinking": {"type": "enabled"}},
                    temperature=0,
                    stream=False
                )
            else:
                response = _client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                stream=False
            )
            content = response.choices[0].message.content
            
            um = response.usage
            usage["input_tokens"] = um.prompt_tokens
            usage["output_tokens"] = um.completion_tokens
            usage["total_tokens"] = um.total_tokens

            code_match = re.search(r"```(?:python)?\n(.*?)```", content, re.DOTALL)
        
            if code_match:
                return code_match.group(1).strip()
            else:
                # If no markdown blocks are found, return the raw content
                # (assuming the model obeyed instructions to output only code)
                return content.strip()
        
        except Exception as e:
            # IMPORTANT: return VALID PYTHON so the dashboard can show the error
            msg = f"I smxAI have instructed {e}"
            return (
                f"# {msg}\n"
                "from syntaxmatrix.display import show\n"
                f"show({msg!r})\n"
            ) 

    if _provider == "google":
        code = google_generate_code()
    elif _provider == "openai" and _model in GPT_MODELS_LATEST:
        code = gpt_models_latest_generate_code()
    elif _provider == "anthropic":
        code = anthropic_generate_code()
    else:
        code = openai_sdk_generate_code()

    code = str(code or "")
    return code, usage
    

def context_compatibility(question: str, dataset_context: str | None = None) -> str:

    _profile = _prof.get_profile('classifier') or _prof.get_profile('admin')
    _profile['client'] = _prof.get_client(_profile)
    _client = _profile['client']
    _provider = _profile.get("provider").lower()
    _model = _profile.get("model")

    def compatibility_response(user_prompt, system_prompt, temp=0.0, max_tokens=128):
                        
        # Google GenAI
        if _provider == "google":
            resp = _client.models.generate_content(
                model=_model,
                contents=system_prompt + "\n\n" + user_prompt,
            )
            text = resp.text
            return text.strip()       

        # OpenAI 
        elif _provider == "openai" and _model in GPT_MODELS_LATEST: 
            
            def reasoning_and_verbosity():
                reasoning_effort, verbosity = "medium", "medium" 
                if _model == "gpt-5-nano":
                    if max_tokens <= 256:
                        reasoning_effort = "minimal"
                    else: reasoning_effort = "low"
                elif _model in ["gpt-5-mini", "gpt-5-codex-mini"]:
                    verbosity = "medium"
                elif _model in ["gpt-5", "gpt-5-codex", "gpt-5-pro"]:
                    reasoning_effort = "high" 
                    verbosity = "high"
                return (reasoning_effort, verbosity)
        
            args = _set_args(
                model=_model,
                instructions=system_prompt,
                input=user_prompt,
                previous_id=None,
                store=False,
                reasoning_effort=reasoning_and_verbosity()[0],
                verbosity=reasoning_and_verbosity()[1],
            )
            resp = _client.responses.create(**args)
            txt = _out(resp)
            return txt
        
        # Anthropic
        elif _provider == "anthropic":
            try:
                resp = _client.messages.create(
                    model=_model,
                    system=system_prompt,                 
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.2,
                    max_tokens= max_tokens,
                )

                # Extract plain text from Claude's content blocks
                text = ""
                content = getattr(resp, "content", None)
                if content and isinstance(content, list):
                    parts = []
                    for block in content:
                        # blocks typically like {"type": "text", "text": "..."}
                        t = getattr(block, "text", None)
                        if not t and isinstance(block, dict):
                            t = block.get("text")
                        if t:
                            parts.append(t)
                    text = " ".join(parts)
                    return text
            except Exception:
                pass

        # OpenAI SDK Compartible (Chat Completions)
        else:
            resp = _client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temp,
                max_tokens=max_tokens,
            )
            text = resp.choices[0].message.content
            return text

        return "Configure LLM Profiles or contact your administrator."

    system_prompt = ("""
        - You are a Machine Learning (ML) and Data Science (DS) expert who detects incompatibilities between user questions and dataset summaries.
        - Your goal is to analyze the question and the provided dataset summary to determine if they are compatible. 
        - If and only if the dataset summary columns are not relevant to your desired columns that you have deduced, by analysing the question, and you suspect that the wrong dataset was used in the dataset summary, you MUST STOP just say: 'incompatible'.      
        - If they are compatible, just 'compatible'.
        - DO NOT include any prelude or preamble. Just the response: 'incompatible' or 'compatible'.
    """)

    user_prompt = f"User question:\n{question}\n\n"
    if dataset_context:
        user_prompt += f"Dataset summary:\n{dataset_context}\n"

    compatibility = compatibility_response(user_prompt, system_prompt, temp=0.0, max_tokens=120)
    return compatibility
  

def classify_ml_job_agent(refined_question, dataset_profile):   
    import ast
    
    _profile = _prof.get_profile('classifier') or _prof.get_profile('summarizer') or _prof.get_profile('chat') or _prof.get_profile('admin')
    
    _profile['client'] = _prof.get_client(_profile)
    _client = _profile['client']
    _provider = _profile["provider"].lower()
    _model = _profile["model"]

    def ml_response(user_prompt, system_prompt): 
        
        prompt = user_prompt + "\n\n" + system_prompt
        
        # Google GenAI
        if _provider == "google":  
            from google.genai.errors import APIError

            config=dict(
                        temperature=0.0,
                        response_mime_type="application/json",
                        # Enforcing a JSON array of strings structure for reliable parsing
                        response_schema={
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    )
            try:
                response = _client.models.generate_content(
                    model=_model,
                    contents=prompt,
                    config=config,
                )         
                json_string = response.text.strip()
                ml_jobs = json.loads(json_string)
                
                if not isinstance(ml_jobs, list) or not all(isinstance(job, str) for job in ml_jobs):
                    return []                  
                return ml_jobs

            except APIError as e:
                return [f"An API error occurred: {e}"]
            except json.JSONDecodeError as e:
                if 'response' in locals():
                    return [f"Raw response text: {response.text}"]
            except Exception as e:
                return [f"An unexpected error occurred: {e}"]
    
        elif _provider == "openai" and _model in GPT_MODELS_LATEST:
            
            def reasoning_and_verbosity():
                reasoning_effort, verbosity = "medium", "medium" 
                if _model == "gpt-5-nano":
                    reasoning_effort = "low"
                elif _model in ["gpt-5-mini", "gpt-5-codex-mini"]:
                    verbosity = "medium"
                elif _model in ["gpt-5", "gpt-5-codex", "gpt-5-pro"]:
                    reasoning_effort = "high" 
                    verbosity = "high"
                return (reasoning_effort, verbosity)
        
            args = _set_args(
                model=_model,
                instructions=system_prompt,
                input=user_prompt,
                previous_id=None,
                store=False,
                reasoning_effort=reasoning_and_verbosity()[0],
                verbosity=reasoning_and_verbosity()[1],
            )
            resp = _client.responses.create(**args)
            txt = _out(resp)
            return txt

        elif _provider == "anthropic":
            try:
                resp = _client.messages.create(
                    model=_model,
                    system=system_prompt,                 
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=0.0,
                    max_tokens= 128,
                )

                # Extract plain text from Claude's content blocks
                text = ""
                content = getattr(resp, "content", None)
                if content and isinstance(content, list):
                    parts = []
                    for block in content:
                        # blocks typically like {"type": "text", "text": "..."}
                        t = getattr(block, "text", None)
                        if not t and isinstance(block, dict):
                            t = block.get("text")
                        if t:
                            parts.append(t)
                    text = " ".join(parts)
                    return text
            except Exception:
                pass

        else:
            resp = _client.chat.completions.create(
                model=_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=128,
            )
            text = resp.choices[0].message.content
            return text

        return "Configure LLM Profiles or contact your administrator."

    system_prompt = ("""
        "You are an expert ML task extractor. Your job is to analyze the user's task description and extract every implied or explicit machine learning (ML) task that would be necessary to accomplish the user's goals. Use the provided list of ML tasks as your reference for classification.
        Core Instruction:
        Extract every implied or explicit ML task. Format the response solely as a simple, flat list of tasks. Use concise, imperative verbs. Do not include explanations, examples, preludes, conclusions, or any non-task text.

        Extraction Rules:
        Ignore all context-setting, descriptions, goals, and commentary.
        Convert every actionable step, data operation, and visualization generation into a discrete task.
        Generalize any dataset-specific terms (e.g., column names) to their functional purpose.
        Treat "CoT" or reasoning steps as a source for data preparation tasks.
        Do not include steps like "No Scaling required" or "No Modeling required" as tasks.
        Output only the list. No titles, headers, numbering or bullet points.
    """)

    # --- 1. Define the Master List of ML Tasks (Generalized) ---
    ml_task_list = [
        # Supervised Learning
        "classification", "regression", "ranking", "object_detection", "image_segmentation",
        
        # Unsupervised Learning
        "clustering", "dimensionality_reduction", "anomaly_detection", "association_rule_mining",
        
        # Sequential/Time Data
        "time_series_forecasting", "sequence_labeling", "survival_analysis",
        
        # Specialized Domains
        "natural_language_processing", "computer_vision", "reinforcement_learning", 
        "generative_modeling", "causal_inference", "risk_modeling", "graph_analysis",
        
        # Foundational/Pipeline Steps
        "data_preprocessing", "feature_engineering", "statistical_inference", "clustering", "hyperparameter_tuning"
    ]
    
    # --- 2. Construct the Generalized Prompt for the LLM ---
    task_description = refined_question

    user_prompt = f"""
    Analyze and classify the following task description:
    ---
    {task_description}
    ---
    
    If the Dataset Profile is provided, use its info, together with the task description, to make your job types
    Identify and select ALL job types from the provided, extensive list that are directly 
    relevant to achieving the goals outlined in the task description (either as the 
    core goal, prerequisites, or essential steps).
    
    ML Jobs List: {', '.join(ml_task_list)}

    Respond ONLY with a valid JSON array of strings containing the selected ML job names.
    Example Response: ["data_preprocessing", "regression", "classification", "feature_engineering"]
    """

    if dataset_profile:
        user_prompt += f"\nDataset profile:\n{dataset_profile}\n"
        

    tasks = ml_response(user_prompt, system_prompt)
    try:
        return ast.literal_eval(tasks)
    except Exception:
        return tasks


# ─────────────────────────────────────────────────────────
# Agentic Page Generation (plan JSON → validate → Pixabay → compile HTML)
# ─────────────────────────────────────────────────────────
def agentic_generate_page(*,
    page_slug: str,
    website_description: str,
    client_dir: str,
    pixabay_api_key: str = "",
    llm_profile: dict | None = None,
    max_retries: int = 2,
    max_images: int = 9,
) -> dict:
    """
    Returns:
      {
        "slug": "<slug>",
        "plan": <dict>,
        "html": "<compiled html>",
        "notes": [..]
      }
    """

    _ICON_SVGS = {
        "spark": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M12 2l1.2 6.2L20 12l-6.8 3.8L12 22l-1.2-6.2L4 12l6.8-3.8L12 2z"/></svg>',
        "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M12 2l7 4v6c0 5-3.5 9-7 10-3.5-1-7-5-7-10V6l7-4z"/></svg>',
        "stack": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M12 2l9 5-9 5-9-5 9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 17l9 5 9-5"/></svg>',
        "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M3 3v18h18"/><path d="M7 14v4"/><path d="M12 10v8"/><path d="M17 6v12"/></svg>',
        "rocket": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M5 13l4 6 6-4c6-4 5-12 5-12S13 2 9 8l-4 5z"/><path d="M9 8l7 7"/>'
                '<path d="M5 13l-2 2"/><path d="M11 19l-2 2"/></svg>',
        "plug": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M9 2v6"/><path d="M15 2v6"/><path d="M7 8h10"/>'
                '<path d="M12 8v7a4 4 0 0 1-4 4H7"/><path d="M12 8v7a4 4 0 0 0 4 4h1"/></svg>',
        "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M5 12h12"/><path d="M13 6l6 6-6 6"/></svg>',
        "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
                '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
                '<circle cx="9" cy="7" r="4"/>'
                '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
                '<path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    }

    _PLACEHOLDER_PATTERNS = [
        r"\blorem\b",
        r"\bplaceholder\b",
        r"coming soon",
        r"add (?:a|your|an)\b",
        r"replace this",
        r"insert (?:your|a)\b",
        r"dummy text",
        r"example (?:text|copy)\b",
    ]

    _PX_BANNED_TAGS = {
        "shoe", "shoes", "sneaker", "sneakers", "footwear", "fashion",
        "lingerie", "bikini", "underwear", "swimwear",
    }


    def _strip(s: str) -> str:
        return (s or "").strip()

    def _slugify(s: str) -> str:
        s = _strip(s).lower()
        s = re.sub(r"[^a-z0-9\s\-]", "", s)
        s = re.sub(r"\s+", "-", s).strip("-")
        s = re.sub(r"-{2,}", "-", s)
        return s or "page"

    def _title_from_slug(slug: str) -> str:
        t = _strip(slug).replace("-", " ").replace("_", " ")
        t = re.sub(r"\s+", " ", t)
        return (t[:1].upper() + t[1:]) if t else "New page"

    def _contains_placeholders(text: str) -> bool:
        t = (text or "").lower()
        for pat in _PLACEHOLDER_PATTERNS:
            if re.search(pat, t):
                return True
        return False

    def _extract_domain_keywords(website_description: str, max_terms: int = 6) -> list[str]:
        """
        Very lightweight keyword extraction to keep Pixabay queries on-topic.
        No ML needed: just pick frequent meaningful tokens.
        """
        wd = (website_description or "").lower()
        wd = re.sub(r"[^a-z0-9\s\-]", " ", wd)
        toks = [t for t in re.split(r"\s+", wd) if 3 <= len(t) <= 18]
        stop = {
            "this", "that", "with", "from", "into", "your", "their", "have", "will",
            "also", "more", "than", "them", "such", "only", "when", "where", "which",
            "what", "about", "page", "website", "company", "product", "service",
            "syntaxmatrix", "framework", "system", "platform",
        }
        freq = {}
        for t in toks:
            if t in stop:
                continue
            freq[t] = freq.get(t, 0) + 1
        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        out = [k for k, _ in ranked[:max_terms]]
        # Always anchor to software/AI semantics if present
        anchors = []
        for a in ["ai", "assistant", "dashboard", "retrieval", "vector", "ml", "analytics", "deployment"]:
            if a in wd and a not in out:
                anchors.append(a)
        return (anchors + out)[:max_terms]

    def _get_json_call(system_prompt: str, user_prompt: str) -> dict:
        
        llm_profile = _prof.get_profile('coder')
        llm_profile['client'] = _prof.get_client(llm_profile)
        client = llm_profile["client"]
        model = llm_profile["model"]
        provider = llm_profile["provider"].lower()

        
        def openai_sdk_response():
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
            
            # Access the text via choices[0].message.content
            txt = resp.choices[0].message.content.strip()
            
            try:
                return json.loads(txt)
            except Exception:
                # try to salvage first JSON object (consistent with your other providers)
                m = re.search(r"\{.*\}", txt, re.S)
                if not m:
                    raise RuntimeError(f"Model did not return JSON. Output was:\n{txt[:800]}")
                return json.loads(m.group(0))
    

        if provider == "google":
            cfg = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            )
            resp = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=cfg,
            )
            txt = (resp.text or "").strip()
            try:
                return json.loads(txt)
            except Exception:
                # try to salvage first JSON object
                m = re.search(r"\{.*\}", txt, re.S)
                if not m:
                    raise RuntimeError(f"Model did not return JSON. Output was:\n{txt[:800]}")
                return json.loads(m.group(0))
        

        if provider == "openai":
            if int(model.split("gpt-")[1][0])>=5:
                
                response = client.responses.create(
                    model=model,
                    instructions=system_prompt,
                    input=[
                        {"role": "user", "content": user_prompt}
                    ],
                    reasoning={"effort": "medium"},
                    # IMPORTANT: 'text' must be an object (not a list)
                    text={"format": {"type": "json_object"}},
                )

                txt = (response.output_text or "")
                try:
                    return json.loads(txt)
                except Exception:
                    # try to salvage first JSON object
                    m = re.search(r"\{.*\}", txt, re.S)
                    if not m:
                        raise RuntimeError(f"Model did not return JSON. Output was:\n{txt[:800]}")
                    return json.loads(m.group(0))

            else:
                return openai_sdk_response()


        if provider == "anthropic":
            # Anthropic requires a max_tokens parameter
            resp = client.messages.create(
                model=model,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4096, 
            )
            
            # Anthropic returns a list of content blocks
            txt = resp.content[0].text.strip()
            
            try:
                return json.loads(txt)
            except Exception:
                # try to salvage first JSON object (same logic as your Google snippet)
                m = re.search(r"\{.*\}", txt, re.S)
                if not m:
                    raise RuntimeError(f"Model did not return JSON. Output was:\n{txt[:800]}")
                return json.loads(m.group(0))
        
        return openai_sdk_response()


    def _page_plan_system_prompt(spec: dict) -> str:
        allowed_sections = spec.get("allowed_section_types") or ["hero", "features", "gallery", "testimonials", "faq", "cta", "richtext"]
        req = spec.get("required_sections") or []

        req_lines = ""
        if req:
            req_lines = "REQUIRED SECTIONS (must appear in this exact order):\n" + "\n".join(
                [f"- {r['id']} (type: {r['type']})" for r in req]
            )

        return f"""
        You are a senior UX designer + product copywriter for modern software websites.

        TASK:
        Create a complete page plan (content + structure) for a page builder.

        RULES (strict):
        - No placeholders, no “add your…”, no “replace this…”, no “lorem ipsum”, no “coming soon”.
        - All copy must be final, meaningful, and grounded in the provided WEBSITE_DESCRIPTION.
        - Produce a page that looks like a finished, publish-ready website page.
        - Choose section types and item types from the allowed lists.
        - Choose icon names only from the allowed icon list.
        - Provide image search queries for items that need images. Keep queries on-topic (software/AI/tech).

        {req_lines}

        OUTPUT:
        Return ONLY valid JSON.

        ALLOWED SECTION TYPES:
        {chr(10).join([f"- {t}" for t in allowed_sections])}

        ALLOWED ITEM TYPES:
        - card
        - quote
        - faq

        ALLOWED ICONS:
        - spark, shield, stack, chart, rocket, plug, arrow, users

        JSON SCHEMA:
        {{
          "page": "<slug>",
          "category": "<string>",
          "template": {{ "id": "<string>", "version": "<string>" }},
          "meta": {{
            "pageTitle": "<string>",
            "summary": "<string>"
          }},
          "sections": [
            {{
              "id": "<string>",
              "type": "<sectionType>",
              "title": "<string>",
              "text": "<string>",
              "cols": 1-5,
              "items": [
                {{
                  "id": "<string>",
                  "type": "<itemType>",
                  "title": "<string>",
                  "text": "<string>",
                  "icon": "<iconName or empty>",
                  "imgQuery": "<search query or empty>",
                  "needsImage": true|false
                }}
              ]
            }}
          ]
        }}

        GUIDANCE:
        - Keep sections between {spec.get("min_sections", 4)} and {spec.get("max_sections", 7)}.
        - Keep total images between {spec.get("min_images", 6)} and {spec.get("max_images", 9)}.
        """.strip()


    def _make_page_plan(*, page_slug: str, website_description: str, template_spec: dict) -> dict:
        slug = _slugify(page_slug)
        wd = _strip(website_description)
        if not wd:
            raise ValueError("website_description is empty. Pass smx.website_description if the form field is blank.")

        domain_terms = _extract_domain_keywords(wd)
        user_prompt = json.dumps({
            "PAGE_SLUG": slug,
            "PAGE_TITLE": _title_from_slug(slug),
            "WEBSITE_DESCRIPTION": wd,
            "DOMAIN_KEYWORDS": domain_terms,
            "HARD_REQUIREMENTS": {
                "no_placeholders": True,
                "uk_english": True,
                "min_sections": 4,
                "max_sections": 7,
                "min_images": 6,
                "max_images": 9
            }
        }, indent=2)

        plan = _get_json_call(
            system_prompt=_page_plan_system_prompt(template_spec),
            user_prompt=user_prompt
        )

        plan["page"] = slug
        plan["category"] = template_spec["category"]
        plan["template"] = template_spec["template"]

        # Normalise a few fields
        plan["page"] = slug
        if "sections" not in plan or not isinstance(plan["sections"], list):
            raise RuntimeError("Invalid plan: missing sections[]")

        return plan


    def _validate_plan_or_raise(plan: dict) -> None:
        if not isinstance(plan, dict):
            raise ValueError("Plan is not a dict.")

        if not plan.get("page"):
            raise ValueError("Plan missing 'page'.")

        secs = plan.get("sections")
        if not isinstance(secs, list) or len(secs) < 3:
            raise ValueError("Plan must have at least 3 sections.")

        total_imgs = 0
        for s in secs:
            if not isinstance(s, dict):
                raise ValueError("Section is not an object.")
            if _contains_placeholders(s.get("title", "")) or _contains_placeholders(s.get("text", "")):
                raise ValueError("Plan contains placeholder text in section title/text.")

            items = s.get("items") or []
            if not isinstance(items, list):
                raise ValueError("Section items must be a list.")
            for it in items:
                if not isinstance(it, dict):
                    raise ValueError("Item is not an object.")
                if _contains_placeholders(it.get("title", "")) or _contains_placeholders(it.get("text", "")):
                    raise ValueError("Plan contains placeholder text in item title/text.")
                if it.get("needsImage"):
                    total_imgs += 1

        if total_imgs < 4:
            raise ValueError("Plan is too light on imagery; needs at least 4 items marked needsImage=true.")


    def _repair_plan(*, plan: dict, error_msg: str, website_description: str) -> dict:
        # Ask Gemini to repair the plan, not recreate randomly.
        system_prompt = _page_plan_system_prompt() + "\n\nYou are repairing an existing plan. Keep it consistent and improve only what is needed."
        user_prompt = json.dumps({
            "ERROR": error_msg,
            "WEBSITE_DESCRIPTION": website_description,
            "PLAN": plan
        }, indent=2)

        fixed = _get_json_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        fixed["page"] = plan.get("page") or fixed.get("page")
        return fixed
    
    def _ensure_hero_image(plan: dict, default_url: str = "/static/assets/hero-default.svg") -> None:
        """Guarantee hero.imageUrl exists so contract validation never fails."""
        sections = plan.get("sections") if isinstance(plan.get("sections"), list) else []
        hero = next((s for s in sections if isinstance(s, dict) and (s.get("type") or "").lower() == "hero"), None)
        if not hero:
            return

        def _first_image_in_items(items):
            if not isinstance(items, list):
                return ""
            for it in items:
                if not isinstance(it, dict):
                    continue
                u = (it.get("imageUrl") or "").strip()
                if u:
                    return u
            return ""

        # 1) Use hero.imageUrl if present
        img = (hero.get("imageUrl") or "").strip()

        # 2) Else use hero.items[*].imageUrl
        if not img:
            img = _first_image_in_items(hero.get("items"))

        # 3) Else use first image anywhere else in the plan
        if not img:
            for s in sections:
                if not isinstance(s, dict):
                    continue
                img = _first_image_in_items(s.get("items"))
                if img:
                    break

        # 4) Final fallback
        if not img:
            img = default_url

        hero["imageUrl"] = img

        # Back-compat: ensure hero.items[0].imageUrl exists too (your normaliser also does this)
        items = hero.get("items") if isinstance(hero.get("items"), list) else []
        if items:
            if not (items[0].get("imageUrl") or "").strip():
                items[0]["imageUrl"] = img
        else:
            hero["items"] = [{"id": "hero_media", "type": "card", "title": "Hero image", "text": "", "imageUrl": img}]

    TEMPLATE_SPECS = {
        "generic_v1": {
            "category": "landing",
            "template": {"id": "generic_v1", "version": "1.0.0"},
            "allowed_section_types": ["hero", "features", "gallery", "testimonials", "faq", "cta", "richtext"],
            "required_sections": [],
            "min_sections": 4,
            "max_sections": 7,
            "min_images": 6,
            "max_images": 9,
        },
        "services_grid_v1": {
            "category": "services",
            "template": {"id": "services_grid_v1", "version": "1.0.0"},
            "allowed_section_types": ["hero", "services", "process", "proof", "faq", "cta", "richtext"],
            "required_sections": [
                {"id": "sec_hero", "type": "hero"},
                {"id": "sec_services", "type": "services"},
                {"id": "sec_process", "type": "process"},
                {"id": "sec_proof", "type": "proof"},
                {"id": "sec_faq", "type": "faq"},
                {"id": "sec_cta", "type": "cta"},
            ],
            "min_sections": 6,
            "max_sections": 6,
            "min_images": 6,
            "max_images": 9,
        },
        "services_detail_v1": {
            "category": "services",
            "template": {"id": "services_detail_v1", "version": "1.0.0"},
            "allowed_section_types": ["hero", "offers", "comparison", "process", "case_studies", "faq", "cta", "richtext"],
            "required_sections": [
                {"id": "sec_hero", "type": "hero"},
                {"id": "sec_offers", "type": "offers"},
                {"id": "sec_comparison", "type": "comparison"},
                {"id": "sec_process", "type": "process"},
                {"id": "sec_case_studies", "type": "case_studies"},
                {"id": "sec_faq", "type": "faq"},
                {"id": "sec_cta", "type": "cta"},
            ],
            "min_sections": 7,
            "max_sections": 7,
            "min_images": 6,
            "max_images": 9,
        },
        "about_glass_hero_v1": {
            "category": "about",
            "template": {"id": "about_glass_hero_v1", "version": "1.0.0"},
            "allowed_section_types": ["hero", "story", "values", "logos", "team", "testimonials", "faq", "cta", "richtext"],
            "required_sections": [
                {"id": "sec_hero", "type": "hero"},
                {"id": "sec_story", "type": "story"},
                {"id": "sec_values", "type": "values"},
                {"id": "sec_cta", "type": "cta"},
            ],
            "min_sections": 4,
            "max_sections": 7,
            "min_images": 6,
            "max_images": 9,
        },
    }

    def _select_template_spec(slug: str) -> dict:
        s = _slugify(slug)
        if "service" in s:
            if any(k in s for k in ("pricing", "plan", "plans", "package", "packages", "tier", "tiers")):
                return TEMPLATE_SPECS["services_detail_v1"]
            return TEMPLATE_SPECS["services_grid_v1"]
        if "about" in s:
            return TEMPLATE_SPECS["about_glass_hero_v1"]
        return TEMPLATE_SPECS["generic_v1"]


    PIXABAY_API_URL = "https://pixabay.com/api/"

    def _pixabay_search(api_key: str, query: str, *, category: str = "AI", per_page: int = 20, timeout: int = 15) -> list[dict]:
        q = _strip(query)
        if not api_key or not q:
            return []
        params = {
            "key": api_key,
            "q": q,
            "image_type": "photo",
            "orientation": "horizontal",
            "safesearch": "true",
            "editors_choice": "false",
            "order": "popular",
            "category": category or "AI" or "Artificial Intelligence" or "computer",
            "per_page": max(3, min(200, int(per_page or 20))),
            "page": 1,
        }
        r = requests.get(PIXABAY_API_URL, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json() or {}
        return data.get("hits") or []


    def _is_pixabay_url(url: str) -> bool:
        u = _strip(url).lower()
        return u.startswith("https://") and ("pixabay.com" in u)


    def _fetch_bytes(url: str, timeout: int = 20) -> bytes:
        if not _is_pixabay_url(url):
            raise ValueError("Only Pixabay URLs are allowed")
        r = requests.get(url, stream=True, timeout=timeout)
        r.raise_for_status()
        return r.content


    def _save_image(img_bytes: bytes, out_path_no_ext: str, *, max_width: int = 1920) -> str:
        img = Image.open(io.BytesIO(img_bytes))
        img.load()

        if img.width > int(max_width or 1920):
            ratio = (int(max_width) / float(img.width))
            new_h = max(1, int(round(img.height * ratio)))
            img = img.resize((int(max_width), new_h), Image.LANCZOS)

        has_alpha = ("A" in img.getbands())
        ext = ".png" if has_alpha else ".jpg"
        out_path = out_path_no_ext + ext
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        if ext == ".jpg":
            rgb = img.convert("RGB") if img.mode != "RGB" else img
            rgb.save(out_path, "JPEG", quality=85, optimize=True, progressive=True)
        else:
            img.save(out_path, "PNG", optimize=True)

        return out_path


    def _pick_pixabay_hit(hits: list[dict], *, min_width: int) -> dict | None:
        for h in hits:
            tags = (h.get("tags") or "").lower()
            if any(b in tags for b in _PX_BANNED_TAGS):
                continue
            w = int(h.get("imageWidth") or 0)
            if w >= int(min_width or 0):
                return h
        # fallback: first non-banned
        for h in hits:
            tags = (h.get("tags") or "").lower()
            if any(b in tags for b in _PX_BANNED_TAGS):
                continue
            return h
        return None


    def fill_plan_images_from_pixabay(plan: dict, *, api_key: str, client_dir: str, max_width: int = 1920, max_downloads: int = 9) -> dict:
        if not api_key:
            return plan

        media_dir = os.path.join(client_dir, "uploads", "media")
        imported_dir = os.path.join(media_dir, "images", "imported")
        os.makedirs(imported_dir, exist_ok=True)

        used_ids = set()
        downloads = 0

        domain_terms = []
        try:
            meta = plan.get("meta") or {}
            domain_terms = _extract_domain_keywords(meta.get("summary") or "", max_terms=5)
        except Exception:
            domain_terms = []

        for s in (plan.get("sections") or []):
            items = s.get("items") or []
            for it in items:
                if downloads >= max_downloads:
                    return plan
                if not it.get("needsImage"):
                    continue
                if _strip(it.get("imageUrl")):
                    continue

                q = _strip(it.get("imgQuery"))
                if not q:
                    # if model forgot: make something safe and on-topic
                    q = f"{_strip(it.get('title'))} software ai dashboard"

                # keep the query on-domain
                if domain_terms:
                    q = f"{q} " + " ".join(domain_terms[:3])

                min_w = 1920 if (s.get("type") == "hero") else 1100

                hits = _pixabay_search(api_key, q, category="computer")
                if not hits:
                    continue

                chosen = _pick_pixabay_hit(hits, min_width=min_w)
                if not chosen:
                    continue

                pid = int(chosen.get("id") or 0)
                if not pid or pid in used_ids:
                    continue
                used_ids.add(pid)

                web_u = _strip(chosen.get("webformatURL") or "")
                large_u = _strip(chosen.get("largeImageURL") or "")

                base = os.path.join(imported_dir, f"pixabay-{pid}")
                existing = None
                for ext in (".jpg", ".png"):
                    if os.path.exists(base + ext):
                        existing = base + ext
                        break

                if existing:
                    rel = os.path.relpath(existing, media_dir).replace("\\", "/")
                    it["imageUrl"] = f"/uploads/media/{rel}"
                    continue

                try:
                    b1 = _fetch_bytes(web_u)
                    img1 = Image.open(io.BytesIO(b1)); img1.load()

                    chosen_bytes = b1
                    if img1.width < min_w and large_u:
                        try:
                            b2 = _fetch_bytes(large_u)
                            img2 = Image.open(io.BytesIO(b2)); img2.load()
                            if img2.width > img1.width:
                                chosen_bytes = b2
                        except Exception:
                            pass

                    saved = _save_image(chosen_bytes, base, max_width=max_width)
                    rel = os.path.relpath(saved, media_dir).replace("\\", "/")
                    it["imageUrl"] = f"/uploads/media/{rel}"
                    downloads += 1
                except Exception:
                    continue

        return plan


    # ─────────────────────────────────────────────────────────
    # Compile plan JSON → modern HTML (responsive + animations)
    # ─────────────────────────────────────────────────────────
    def compile_plan_to_html(plan: dict) -> str:
        page_slug = _slugify(plan.get("page") or "page")
        page_id = f"smx-page-{page_slug}"

        sections = list(plan.get("sections") or [])
        meta = plan.get("meta") or {}

        # Useful anchor targets for CTAs
        sec_id_by_type = {}
        for s in sections:
            st = (s.get("type") or "").lower()
            sid = _strip(s.get("id"))
            if st and sid and st not in sec_id_by_type:
                sec_id_by_type[st] = sid

        def esc(s: str) -> str:
            s = s or ""
            s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            s = s.replace('"', "&quot;").replace("'", "&#39;")
            return s

        def _btn(label: str, href: str, *, primary: bool = False) -> str:
            label = _strip(label)
            href = _strip(href)
            if not label or not href:
                return ""
            cls = "btn btn-primary" if primary else "btn"
            return f'<a class="{cls}" href="{esc(href)}">{esc(label)}</a>'

        def icon(name: str) -> str:
            svg = _ICON_SVGS.get((name or "").strip().lower())
            if not svg:
                return ""
            return f'<span class="smx-ic">{svg}</span>'

        css = f"""
        <style>
            #{page_id} {{
            --r: 18px;
            --bd: rgba(148,163,184,.25);
            --fg: #0f172a;
            --mut: #475569;
            --card: rgba(255,255,255,.78);
            --bg: #f8fafc;
            font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
            background: var(--bg);
            color: var(--fg);
            overflow-x: clip;
            }}
            @media (prefers-color-scheme: dark){{
            #{page_id} {{
                --fg: #e2e8f0;
                --mut: #a7b3c6;
                --card: rgba(2,6,23,.45);
                --bg: radial-gradient(circle at 20% 10%, rgba(30,64,175,.25), rgba(2,6,23,.95) 55%);
                --bd: rgba(148,163,184,.18);
            }}
            }}
            #{page_id} .wrap{{ max-width:1120px; margin:0 auto; padding:0 18px; }}
            #{page_id} .sec{{ padding:56px 0; }}
            #{page_id} .kicker{{ color:var(--mut); font-size:.92rem; margin:0 0 8px; }}
            #{page_id} h1{{ font-size:clamp(2rem,3.4vw,3.1rem); line-height:1.08; margin:0 0 12px; }}
            #{page_id} h2{{ font-size:clamp(1.35rem,2.2vw,1.95rem); margin:0 0 10px; }}
            #{page_id} p{{ margin:0; color:var(--mut); line-height:1.65; }}
            #{page_id} .hero{{ padding:0; }}
            #{page_id} .card{{ border:1px solid var(--bd); border-radius:var(--r); background:var(--card); padding:14px; }}
            #{page_id} .btnRow, #{page_id} .btnrow{{ display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; }}
            #{page_id} .btn{{ display:inline-flex; gap:8px; align-items:center; border-radius:999px; padding:10px 14px;
            border:1px solid var(--bd); text-decoration:none; background: rgba(99,102,241,.12); color:inherit; }}
            #{page_id} .btn-primary{{ background: rgba(99,102,241,.22); border-color: rgba(99,102,241,.35); }}
            #{page_id} .btn:hover{{ transform: translateY(-1px); }}
            #{page_id} .grid{{ display:grid; gap:12px; }}
            #{page_id} img{{ width:100%; height:auto; border-radius: calc(var(--r) - 6px); display:block; }}
            #{page_id} .smx-ic{{ width:20px; height:20px; display:inline-block; opacity:.9; }}
            #{page_id} .smx-ic svg{{ width:20px; height:20px; }}

            /* HERO BANNER */
            #{page_id} .hero-banner{{
                position:relative;
                width:100%;
                min-height:clamp(380px, 60vh, 680px);
                display:flex;
                align-items:flex-end;
                overflow:hidden;
            }}
            #{page_id} .hero-bg{{
                position:absolute; inset:0;
                background-position:center;
                background-size:cover;
                background-repeat:no-repeat;
                transform:scale(1.02);
                filter:saturate(1.02);
            }}
            #{page_id} .hero-overlay{{
                position:absolute; inset:0;
                background:linear-gradient(90deg,
                    rgba(2,6,23,.62) 0%,
                    rgba(2,6,23,.40) 42%,
                    rgba(2,6,23,.14) 72%,
                    rgba(2,6,23,.02) 100%
                );
            }}
            @media (max-width: 860px){{
                #{page_id} .hero-overlay{{
                    background:linear-gradient(180deg,
                        rgba(2,6,23,.16) 0%,
                        rgba(2,6,23,.55) 70%,
                        rgba(2,6,23,.70) 100%
                    );
                }}
            }}
            #{page_id} .hero-content{{ position:relative; width:100%; padding:72px 18px 48px; }}
            #{page_id} .hero-panel{{
                max-width:700px;
                border:1px solid rgba(148,163,184,.30);
                background:rgba(2,6,23,.24);
                border-radius:var(--r);
                padding:18px;
                backdrop-filter: blur(4px);
                -webkit-backdrop-filter: blur(4px);
                box-shadow: 0 18px 40px rgba(2,6,23,.18);
                color:#e2e8f0;
            }}
            #{page_id} .hero-panel p{{ color:rgba(226,232,240,.84); }}
            #{page_id} .hero-panel h1{{ text-shadow:0 10px 30px rgba(2,6,23,.45); }}
            #{page_id} .hero-panel .kicker{{
                margin:0 0 8px;
                font-size:.9rem;
                color:#a5b4fc;
                text-transform:uppercase;
                letter-spacing:.18em;
                opacity:.95;
            }}
            #{page_id} .hero-panel .btn{{
                background:rgba(15,23,42,.55);
                border-color:rgba(148,163,184,.45);
                color:#e2e8f0;
            }}
            #{page_id} .hero-panel .btn-primary{{
                background:rgba(79,70,229,.92);
                border-color:rgba(129,140,248,.70);
            }}
            #{page_id} .lead{{ margin-top:10px; font-size:1.05rem; line-height:1.65; }}

            /* FAQ */
            #{page_id} .faq details{{ border:1px solid var(--bd); border-radius:14px; background:var(--card); padding:12px 14px; }}
            #{page_id} .faq summary{{ cursor:pointer; font-weight:600; }}
            #{page_id} .faq details + details{{ margin-top:10px; }}

            #{page_id} .quote{{ font-size:1.02rem; line-height:1.6; color:inherit; }}
            #{page_id} .mut{{ color:var(--mut); }}

            #{page_id} .reveal{{ opacity:0; transform:translateY(14px); transition:opacity .55s ease, transform .55s ease; }}
            #{page_id} .reveal.in{{ opacity:1; transform:none; }}
            @media (prefers-reduced-motion: reduce){{ #{page_id} .reveal{{ transition:none; transform:none; opacity:1; }} }}
        </style>
        """.strip()

        js = f"""
        <script>
            (function(){{
            const root = document.getElementById("{page_id}");
            if(!root) return;
            const els = root.querySelectorAll(".reveal");
            const io = new IntersectionObserver((entries)=>{{
                entries.forEach(e=>{{ if(e.isIntersecting) e.target.classList.add("in"); }});
            }}, {{ threshold: 0.12 }});
            els.forEach(el=>io.observe(el));
            }})();
        </script>
        """.strip()

        parts = [f'<div id="{page_id}">', css]

        for s in sections:
            st = (s.get("type") or "section").lower()
            title = esc(s.get("title") or "")
            text = esc(s.get("text") or "")
            cols = int(s.get("cols") or 3)
            cols = max(1, min(5, cols))
            items = s.get("items") or []
            sec_dom_id = _strip(s.get("id"))
            sec_id_attr = f' id="{esc(sec_dom_id)}"' if sec_dom_id else ""

            # HERO BANNER (NO automatic CTAs - user controls hero buttons via the editor)
            if st == "hero":
                hero_img = _strip(s.get("imageUrl"))

                if not hero_img:
                    for it in items:
                        u = _strip(it.get("imageUrl"))
                        if u:
                            hero_img = u
                            break

                bg_style = f"style=\"background-image:url('{esc(hero_img)}')\"" if hero_img else ""

                parts.append(f"""
                    <section class="hero hero-banner"{sec_id_attr}>
                        <div class="hero-bg" {bg_style}></div>
                        <div class="hero-overlay"></div>
                        <div class="wrap hero-content">
                            <div class="hero-panel reveal">
                                <p class="kicker">{esc(meta.get("pageTitle") or title)}</p>
                                <h1>{title}</h1>
                                <p class="lead">{text}</p>
                            </div>
                        </div>
                    </section>
                """.strip())
                continue

            # FAQ as accordion
            if st == "faq":
                qa = []
                for it in items:
                    q = esc(it.get("title") or "")
                    a = esc(it.get("text") or "")
                    if not q and not a:
                        continue
                    qa.append(
                        f"<details class=\"reveal\"><summary>{q}</summary>"
                        f"<div class=\"mut\" style=\"margin-top:8px;\">{a}</div></details>"
                    )

                parts.append(f"""
                <section class="sec faq"{sec_id_attr}>
                    <div class="wrap">
                        <h2 class="reveal">{title}</h2>
                        {"<p class='reveal' style='margin-bottom:14px;'>" + text + "</p>" if text else ""}
                        {"".join(qa)}
                    </div>
                </section>
                """.strip())
                continue

            # Testimonials styled differently
            if st == "testimonials":
                cards = []
                for it in items:
                    quote = esc(it.get("text") or "")
                    who = esc(it.get("title") or "")
                    if not quote:
                        continue
                    cards.append(
                        f"<div class='card reveal'><div class='quote'>“{quote}”</div>"
                        f"<div class='mut' style='margin-top:10px;font-weight:600;'>{who}</div></div>"
                    )

                grid_html = (
                    f'<div class="grid" style="grid-template-columns:repeat({max(1, min(cols, 3))}, minmax(0,1fr));">'
                    + "\n".join(cards) + "</div>"
                ) if cards else ""

                parts.append(f"""
                <section class="sec"{sec_id_attr}>
                    <div class="wrap">
                        <h2 class="reveal">{title}</h2>
                        {"<p class='reveal' style='margin-bottom:14px;'>" + text + "</p>" if text else ""}
                        {grid_html}
                    </div>
                </section>
                """.strip())
                continue

            # Stats + Logos break rhythm so pages look different
            if st in ("stats", "logos"):
                cards = []
                for it in items:
                    it_title = esc(it.get("title") or "")
                    it_text = esc(it.get("text") or "")
                    img = _strip(it.get("imageUrl"))
                    if st == "logos" and img:
                        cards.append(
                            f"<div class='card reveal' style='padding:12px;display:flex;align-items:center;justify-content:center;'>"
                            f"<img loading='lazy' decoding='async' src='{esc(img)}' alt='{it_title}' style='max-height:46px;width:auto;border-radius:0;'>"
                            f"</div>"
                        )
                    else:
                        cards.append(
                            f"<div class='card reveal'><div style='font-size:1.35rem;font-weight:800;line-height:1.1;'>{it_title}</div>"
                            f"<div class='mut' style='margin-top:8px;'>{it_text}</div></div>"
                        )

                use_cols = max(2, min(cols, 5))
                grid_html = (
                    f'<div class="grid" style="grid-template-columns:repeat({use_cols}, minmax(0,1fr));">'
                    + "\n".join(cards) + "</div>"
                ) if cards else ""

                parts.append(f"""
                <section class="sec"{sec_id_attr}>
                    <div class="wrap">
                        {"<h2 class='reveal'>" + title + "</h2>" if title else ""}
                        {"<p class='reveal' style='margin-bottom:14px;'>" + text + "</p>" if text else ""}
                        {grid_html}
                    </div>
                </section>
                """.strip())
                continue

            # Default cards grid (features, gallery, process, integrations, team, timeline, richtext, cta etc.)
            cards = []
            for it in items:
                it_title = esc(it.get("title") or "")
                it_text = esc(it.get("text") or "")
                it_icon = icon(it.get("icon") or "")
                img = _strip(it.get("imageUrl"))
                img_html = f'<img loading="lazy" decoding="async" src="{esc(img)}" alt="{it_title}">' if img else ""
                cards.append(f"""
                <div class="card reveal">
                    {img_html}
                    <div style="display:flex; gap:10px; align-items:center; margin-top:{'10px' if img_html else '0'};">
                        {it_icon}
                        <h3 style="margin:0; font-size:1.05rem;">{it_title}</h3>
                    </div>
                    <p style="margin-top:8px;">{it_text}</p>
                </div>
                """.strip())

            grid_html = (
                f'<div class="grid" style="grid-template-columns:repeat({cols}, minmax(0,1fr));">'
                + "\n".join(cards) + "</div>"
            ) if cards else ""

            parts.append(f"""
            <section class="sec"{sec_id_attr}>
                <div class="wrap">
                    <h2 class="reveal">{title}</h2>
                    {"<p class='reveal' style='margin-bottom:14px;'>" + text + "</p>" if text else ""}
                    {grid_html}
                </div>
            </section>
            """.strip())

        parts.append(js)
        parts.append("</div>")
        return "\n\n".join(parts)

    notes = []

    tpl_spec = _select_template_spec(page_slug)
    plan = _make_page_plan(page_slug=page_slug, website_description=website_description, template_spec=tpl_spec)


    for attempt in range(max_retries + 1):
        try:
            _validate_plan_or_raise(plan)
            break
        except Exception as e:
            notes.append(f"plan_validation_failed: {e}")
            if attempt >= max_retries:
                raise
            plan = _repair_plan(plan=plan, error_msg=str(e), website_description=website_description)

    # Fill images locally (Pixabay) to avoid broken links
    if pixabay_api_key:
        try:
            plan = fill_plan_images_from_pixabay(
                plan,
                api_key=pixabay_api_key,
                client_dir=client_dir,
                max_width=1920,
                max_downloads=max_images
            )
        except Exception as e:
            notes.append(f"pixabay_fill_failed: {e}")
    
    # Normalise and validate against the layout contract (after images exist)
    plan = normalise_layout(
        plan,
        default_category=(plan.get("category") or "landing"),
        default_template_id=((plan.get("template") or {}).get("id") or "generic_v1"),
        default_template_version=((plan.get("template") or {}).get("version") or "1.0.0"),
        mode="prod",
    )

    _ensure_hero_image(plan)

    issues = validate_layout(plan)
    errors = [i for i in issues if i.level == "error"]
    if errors:
        msg = "layout_contract_validation_failed:\n" + "\n".join([f"{e.path}: {e.message}" for e in errors])
        notes.append(msg)
        raise RuntimeError(msg)

    # Final sanity check: no placeholders left
    blob = json.dumps(plan, ensure_ascii=False)
    if _contains_placeholders(blob):
        raise RuntimeError("Refusing to publish: plan still contains placeholder-style text.")

    html = compile_plan_to_html(plan)
    return {
        "slug": _slugify(plan.get("page") or page_slug),
        "plan": plan,
        "html": html,
        "notes": notes,
    }



def text_formatter_agent(text):
    """
    Parses an ML job description using the Gemini API with Structured JSON Output.
    """
    
    def generate_formatted_report(data):
        """
        Generates a formatted string of the structured data in a clean, 
        document-like format mimicking the requested list structure.
        
        Returns:
            str: The complete formatted report as a string.
        """
        if not data:
            return "No data to display."

        output_lines = []

        # --- Helper Functions ---
        def clean_md(text):
            """Removes markdown bold syntax."""
            return text.replace("**", "")

        def format_smart_list_item(prefix, item_text, width=80):
            """
            Content-agnostic list formatter.
            Detects 'Header: Description' patterns and formats them inline.
            Returns the formatted string.
            """
            cleaned = clean_md(item_text)
            
            # Check for "Header: Description" pattern
            # We look for a colon appearing early in the string (e.g., within first 60 chars)
            colon_match = re.match(r"^([^:]{1,60}):\s*(.*)", cleaned, re.DOTALL)
            
            if colon_match:
                header = colon_match.group(1).strip()
                description = colon_match.group(2).strip()
                
                # Format: PREFIX HEADER: Description
                full_line = f"{prefix} {header.upper()}: {description}\n"
            else:
                # Format: PREFIX Content
                full_line = f"{prefix} {cleaned}\n"

            # Calculate hanging indent (aligning with the start of the text after the prefix)
            # Length of prefix + 1 space
            indent_width = len(prefix) + 1
            hanging_indent = " " * indent_width
            
            return textwrap.fill(
                full_line, 
                width=width, 
                subsequent_indent=hanging_indent
            )

        # --- Report Construction ---

        # 1. Title
        title = clean_md(data.get("project_title", "Project Report"))
        output_lines.append("\n" + "=" * 80)
        output_lines.append(f"{title.center(80)}")
        output_lines.append("=" * 80 + "\n")

        # 2. Project Goal
        output_lines.append("PROJECT GOAL\n")
        output_lines.append("-" * 12)
        goal = clean_md(data.get("project_goal", ""))
        output_lines.append(textwrap.fill(goal, width=80))
        output_lines.append("") # Adds a blank line

        # 3. Key Objectives
        if data.get("key_objectives"):
            output_lines.append("KEY OBJECTIVES & STRATEGIC INSIGHTS")
            output_lines.append("-" * 35)
            for item in data["key_objectives"]:
                output_lines.append(format_smart_list_item("•", item))
            output_lines.append("")

        # 4. ML Tasks (Numbered List)
        if data.get("ml_tasks"):
            output_lines.append("ML EXECUTION TASKS")
            output_lines.append("-" * 18)
            for i, task in enumerate(data["ml_tasks"], 1):
                # Using i. as prefix
                output_lines.append(format_smart_list_item(f"{i}.", task))
            output_lines.append("")

        # 5. Deliverables
        if data.get("expected_deliverables"):
            output_lines.append("EXPECTED DELIVERABLES")
            output_lines.append("-" * 21)
            for item in data["expected_deliverables"]:
                output_lines.append(format_smart_list_item("•", item))
        output_lines.append("")

        # Join all lines with newlines
        return "\n".join(output_lines)

    formatter_profile = _prof.get_profile("classification") or _prof.get_profile("classification")
    _api_key = formatter_profile["api_key"]
    _provider = formatter_profile["provider"]
    _model = formatter_profile["model"]
    
    # 1. Define the Schema for strict JSON enforcement
    schema = {
        "type": "OBJECT",
        "properties": {
            "project_title": {"type": "STRING"},
            "project_goal": {"type": "STRING"},
            "key_objectives": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "data_inputs": {
                "type": "OBJECT",
                "properties": {
                    "description_items": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"}
                    },
                    "extracted_features": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"},
                        "description": "List of specific column names or features mentioned (e.g. Age, BMI)"
                    }
                }
            },
            "ml_tasks": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            },
            "expected_deliverables": {
                "type": "ARRAY",
                "items": {"type": "STRING"}
            }
        },
        "required": ["project_title", "project_goal", "key_objectives", "data_inputs", "ml_tasks"]
    }

    # 2. Construct the API Request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{_model}:generateContent?key={_api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Extract the structured data from the following ML Job Description:\n\n{text}"
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result_json = response.json()
        
        # 4. Extract and Parse Content
        raw_text_response = result_json["candidates"][0]["content"]["parts"][0]["text"]
        parsed_data = json.loads(raw_text_response)

        report = generate_formatted_report(parsed_data)
        return parsed_data

    except requests.exceptions.RequestException as e:
        if 'response' in locals() and response is not None:
             return (f"API Request Failed: {e}\n\nResponse info: {response.text}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Parsing Failed: {e}"


