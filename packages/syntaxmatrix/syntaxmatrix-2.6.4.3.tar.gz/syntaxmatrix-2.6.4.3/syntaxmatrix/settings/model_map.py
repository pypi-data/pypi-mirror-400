import json
import os


PROVIDERS_MODELS = {
    #1
    "OpenAI": [ 
        "gpt-5.2",                      
        "gpt-5.2-chat-latest",         
        "gpt-5.2-pro",                  
        "gpt-5.1",                      
        "gpt-5.1-chat-latest",          
        "gpt-5.1-codex-mini",           
        "gpt-5.1-codex-max",            
        "gpt-5",                        
        "gpt-5-nano",                  
        "gpt-5-mini",                   
        "gpt-5-pro",                   
        "gpt-4.1",                      
        "gpt-4.1-nano",                 
        "gpt-4.1-mini",                
        "gpt-4o",                       
        "gpt-4o-mini",                  
        # "gpt-4o-mini-search-preview",  
    ],
    #2
    "Google": [    
        "gemini-3-pro-preview",  
        "gemini-3-flash-preview", 
        "gemini-2.5-pro",      
        "gemini-2.5-flash",       
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        # Image models
        # "gemini-3-pro-image-preview",
        # "gemini-2.5-flash-image",
        # "imagen-4.0-generate-001",
        # "imagen-4.0-ultra-generate-001",
        # "imagen-4.0-fast-generate-001",
    ],
    #3
    "xAI": [                       
        "grok-4-1-fast-reasoning",
        "grok-4-1-fast-non-reasoning",
        "grok-4", 
        "grok-code-fast",     
    ],
    #4
    "Anthropic": [
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-4-5-haiku",
    ],
    #5
    "DeepSeek": [  
        "deepseek-reasoner",          
        "deepseek-chat",
    ],
    #6
    "Alibaba": [   
        "qwen3-max",
        "qwen3-coder-plus",
        "qwen3-coder-flash",
        "qwen-plus", 
        "qwen-flash",  
                       
    ],
    
    #7
    "MoonShot": [
        "kimi-k2-0905-preview",
        "kimi-k2-turbo-preview",
        "kimi-k2-thinking",
        "kimi-k2-thinking-turbo",
    ],
}


#   #8
#     "ZAI": [                                 # coding ==> https://api.z.ai/api/coding/paas/v4
#         "glm-4.7",  
#         "glm-4.6",                            # general ==> https://api.z.ai/api/paas/v4
#         "glm-4.6v",
#         "glm-4.6v-flash",
#         "glm-4.6v-flashx",
#         "glm-4.5v",
#         "glm-4-32b-0414-128k",
#         "cogView-4-250304",
#         "cogvideox-3",
#     ]


# Read-only model descriptions for LLM-profile builder
# -----------------------------------------------------------------------------
MODEL_DESCRIPTIONS = {
    #1.1 OpenAI
    "gpt-4o":"""
        Model: GPT 4o
            Cost: 
            Input = $2.50 <= 1M tokens
            Output = $10.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 128,000 tokens
            Output = 16,384 tokens

            Speed, Intelligence, and Training: 
            3x Fast
            3x Clever 
            Cut-off: 01/10/2023

            Agency: 
            - Admin
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
    """,
    
    #1.2 OpenAI                       
    "gpt-4o-mini":"""
        Model: GPT 4o Mini
            Cost: 
            Input = $0.15 <= 1M tokens
            Output = $0.60 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 128,000 tokens
            Output = 16,384 tokens

            Speed, Intelligence, and Training: 
            4x Fast
            2x Clever 
            Cut-off: 01/10/2023
            
            Agency: 
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
        """,
    
    # #1.3 OpenAI                       
    # "gpt-4o-mini-search-preview":"""
    #     Model: GPT 4o Mini
    #         Cost: 
    #         Input = $0.15 <= 1M tokens
    #         Output = $0.60 <= 1M tokens

    #         Data Type:
    #         Input = Text 
    #         Output = Text

    #         Context Length:
    #         Input  = 128,000 tokens
    #         Output = 16,384 tokens

    #         Speed, Intelligence, and Training: 
    #         4x Fast
    #         2x Clever 
    #         Cut-off: 01/10/2023
            
    #         Agency: 
    #         - Chat
    #         - Classifier
    #         - Summarizer
    #     """,
    
    #1.3 OpenAI
    "gpt-4.1":"""
        Model: GPT 4.1
            Cost: 
            Input = $2.00 <= 1M tokens
            Output = $8.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 1M tokens
            Output = 32,768 tokens

            Speed, Intelligence, and Training: 
            3x Fast
            4x Clever 
            Knowledge: 01/06/2024

            Agency: 
            - Coder
    """,

    #1.4 OpenAI
    "gpt-4.1-nano":"""
        Model: GPT 4.1 Nano
            Cost: 
            Input = $0.10 <= 1M tokens
            Output = $0.40 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 1M tokens
            Output = 32,768 tokens

            Speed, Intelligence, and Training: 
            5x Fast
            2x Clever 
            Knowledge: 01/06/2024

            Agency: 
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
    """,

    #1.5 OpenAI
    "gpt-4.1-mini":"""
        Model: GPT 4.1 Mini
            Cost: 
            Input = $0.40 <= 1M tokens
            Output = $1.60 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 1M tokens
            Output = 32,768 tokens

            Speed, Intelligence, and Training: 
            4x Fast
            3x Clever 
            Knowledge: 01/06/2024

            Agency: 
            - Admin
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
    """,

    #1.6 OpenAI
    "gpt-5":"""
        Model: GPT 5
            Cost: 
            Input = $1.25 <= 1M tokens
            Output = $10.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            3x Fast
            4x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Coder
    """,

    #1.7 OpenAI 
    "gpt-5-nano":"""
        Model: GPT 5 Nano
            Cost: 
            Input = $0.05 <= 1M tokens
            Output = $0.40 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            5x Fast
            2x Clever 
            Thinking: Yes
            Knowledge: 31/05/2024 

            Agency: 
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
    """,
    
    #1.8 OpenAI 
    "gpt-5-mini":"""
        Model: GPT 5 Mini
            Cost: 
            Input = $0.25 <= 1M tokens
            Output = $2.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            4x Fast
            3x Clever 
            Thinking: Yes
            Knowledge: 31/05/2024 

            Agency: 
            - Admin
            - Chat
            - Classifier
            - Summarizer
            - ImageTexter
    """,

     #1.7 OpenAI 
   
     #1.8 OpenAI 
   
      #1.8 OpenAI 
    
    #1.9 OpenAI 
    "gpt-5-pro":"""
        Model: GPT 5 Pro
            Cost: 
            Input = $15.00 <= 1M tokens
            Output = $120.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 272,000 tokens

            Misc: 
            1x Fast
            5x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Coder
    """,

    #1.10 OpenAI 
    "gpt-5.1":"""
        Model: GPT 5.1
            Cost: 
            Input = $1.25 <= 1M tokens
            Output = $10.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            3x Fast
            4x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Admin
            - Coder
    """,

    #1.11 OpenAI 
    "gpt-5.1-chat-latest":"""
        Model: GPT 5.1 Chat
            Cost: 
            Input = $1.25 <= 1M tokens
            Output = $10.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 128,000 tokens
            Output = 16,384 tokens

            Misc: 
            3x Fast
            3x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Admin
            - Chat
    """,

    #1.12 OpenAI 
    "gpt-5.1-codex-mini":"""
        Model: GPT 5.1 Codex Mini
            Cost: 
            Input = $0.25 <= 1M tokens
            Output = $2.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            3x Fast
            4x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Coder
    """,

    #1.13 OpenAI 
    "gpt-5.1-codex-max":"""
        Model: GPT 5.1 Codex Max
            Cost: 
            Input = $1.25 <= 1M tokens
            Output = $10.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            4x Fast
            4x Clever 
            Thinking: Yes
            Knowledge: 30/09/2024 

            Agency: 
            - Coder
    """,

    #1.14 OpenAI 
    "gpt-5.2":"""
        Model: GPT 5.2
            Cost: 
            Input = $1.75 <= 1M tokens
            Output = $14.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            3x Fast
            5x Clever 
            Thinking: Yes
            Knowledge: 31/08/2025 

            Agency: 
            - Coder
    """,
    
    #1.15 OpenAI
    "gpt-5.2-chat-latest":"""
        Model: GPT 5.2 Chat
            Cost: 
            Input = $1.74 <= 1M tokens
            Output = $14.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 128,000 tokens
            Output = 16,384 tokens

            Misc: 
            3x Fast
            3x Clever 
            Thinking: No
            Knowledge: 31/08/2025 

            Agency: 
            - Admin
    """,   

    #1.16 OpenAI 
    "gpt-5.2-pro":"""
        Model: GPT 5.2 Pro
            Cost: 
            Input = $21.00 <= 1M tokens
            Output = $168.00 <= 1M tokens

            Data Type:
            Input = (Text, Image) 
            Output = Text

            Context Length:
            Input  = 400,000 tokens
            Output = 128,000 tokens

            Misc: 
            1x Fast
            5x Clever 
            Thinking: Yes
            Knowledge: 31/08/2025 

            Agency: 
            - Coder
    """,   

    # =========================
    #2   GOOGLE
    # =========================
    #2.1 Google
    "gemini-3-pro-preview": """
        Model: Gemini 3 Pro
        Cost: 
        Input = $2.00 <= 200k tokens / $4.00 > 200k tokens
        Output = $12.00 <= 200k tokens / $18.00 > 200k tokens

        Data Type:
        Input = (Text, Image, Video, Audio, and PDF) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 65.5k tokens

        Agency: 
        - Coder
    """,  
    
    #2.2 Google
    "gemini-3-flash-preview": """
        Model: Gemini 3 Flash
        Cost: 
        Input = $0.50 <= 1M tokens
        Output = $3.00 <= 1M tokens

        Data Type:
        Input = (Text, Image, Video, Audio, PDF) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 65.5k tokens

        Agencies recommended:
        - Coder
        - Admin
        - Chat
        - Classifier
        - Summarizer
        - ImageTexter
    """,

    #2.3 Google
    "gemini-2.5-pro": """
        Model: Gemini 2.5 Pro
        Cost: 
        Input = $1.25 <= 200k tokens / $10.00 > 200k tokens
        Output = $2.50 > 200k tokens / $15.00 > 200k tokens

        Data Type:
        Input = (Text, Image, Video, Audio, PDF) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 65.5k tokens

        Agencies recommended:
        - Coder
    """,

    #2.4 Google
    "gemini-2.5-flash": """
        Model: Gemini 2.5 Flash
        Cost: 
        Input = $0.30 <= 1M tokens
        Output = $2.50 <= 1M tokens

        Data Type:
        Input = (Text, Image, Video, Audio) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 65.5k tokens

        Agencies recommended:
        - Admin
        - Chat
        - Classifier
        - Summarizer
        - ImageTexter              
    """,

    #2.5 Google
    "gemini-2.5-flash-lite": """
        Model: Gemini 2.5 Flash Lite
        Cost: 
        Input = $0.10 <= 1M tokens
        Output = $0.40 <= 1M tokens

        Data Type:
        Input = (Text, image, video, audio, PDF)
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 65.5k tokens

        Agencies recommended:
        - Chat
        - ImageTexter
        - Classifier
        - Summarizer
        - ImageTexter  
    """,
   
    #2.6 Google
    "gemini-2.0-flash": """
        Model: Gemini 2.0 Flash
        Cost: 
        Input = $0.10 <= 1M tokens
        Output = $0.40 <= 1M tokens

        Data Type:
        Input = (Text, Image, Video, Audio) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 8k tokens

        Agencies recommended:
        - ImageTexter 
        - Summarizer
        - Classifier    
    """,

    #2.7 Google
    "gemini-2.0-flash-lite": """
        Model: Gemini 2.0 Flash Lite
        
        Cost: 
        Input = $0.075 <= 1M tokens
        Output = $0.30 <= 1M tokens

        Data Type:
        Input = (Text, Image, Video, Audio) 
        Output = Text

        Context Length:
        Input = 1M tokens
        Output = 8k tokens

        Agencies recommended:
        - ImageTexter 
        - Summarizer
        - Classifier 
    """,

    #3.1 XAI
    "grok-4-1-fast-reasoning": """
        Model: Grok 4.1 Fast Thinking 
        Cost: 
        Input = $0.20 <= 1M tokens
        Output = $0.50 <= 1M tokens

        Data Type:
        Input = (Text, Image) 
        Output = Text

        Context Length:
        Input = 2M tokens
        Output = ?

        Agencies recommended:
        - Coder
        - ImageTexter
    """,

    #3.2 XAI
    "grok-4-1-fast-non-reasoning": """
        Model: Grok 4.1 Fast 
        Cost: 
        Input = $0.20 <= 1M tokens
        Output = $0.50 <= 1M tokens

        Data Type:
        Input = (Text, Image) 
        Output = Text

        Context Length:
        Input = 2M tokens
        Output = ?

        Agencies recommended:
        - Admin
        - Chat
        - Summarizer
        - Classifier 
        - ImageTexter
    """,

    #3.3 XAI
    "grok-code-fast-1": """
        Model: Grok Code Fast 
        Cost: 
        Input = $0.20 <= 1M tokens
        Output = $1.50 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input = 256k tokens
        Output = ?

        Agencies recommended:
        - Code
        - Chat
        - Summarizer
        - Classifier 
    """,

    #3.4 XAI
    "grok-4": """
        Model: Grok 4 
        Cost: 
        Input = $3.00 <= 1M tokens
        Output = $15.00 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input = 256k tokens
        Output = ?

        Agencies recommended:
        - Code  
    """,

    #4.1 Anthropic
    "claude-opus-4-5": """
        Model: Claude Opus 4.5 
        Cost: 
        Input = $5.00 <= 1M tokens
        Output = $25.00 <= 1M tokens

        Data Type:
        Input = Text, Image 
        Output = Text

        Context Length:
        Input = 200k tokens
        Output = 64k

        Speed, Intelligence, and Training: 
            3x Fast
            5x Clever 
            Thinking: Yes
            Knowledge: May 2025

        Agencies recommended:
        - Coder
    """,
    
    #4.2 Anthropic
    "claude-sonnet-4-5": """
        Model: Claude Sonnet 4.5 
        Cost: 
        Input = $3.00 <= 1M tokens
        Output = $15.00 <= 1M tokens

        Data Type:
        Input = Text, Image 
        Output = Text

        Context Length:
        Input = 200k tokens
        Output = 64k

        Speed, Intelligence, and Training: 
            4x Fast
            4x Clever 
            Thinking: Yes
            Knowledge: Jan 2025

        Agencies recommended:
        - Code  
    """,

    #4.3 Anthropic
    "claude-haiku-4-5":"""
        Model: Claude Haiku 4.5 
        Cost: 
        Input = $1.00 <= 1M tokens
        Output = $5.00 <= 1M tokens

        Data Type:
        Input = Text, Image 
        Output = Text

        Context Length:
        Input = 200k tokens
        Output = 64k

        Speed, Intelligence, and Training: 
            5x Fast
            3x Clever 
            Thinking: Yes
            Knowledge: Feb 2025

        Agencies recommended:
        - Admin
        - Chat
        - Code  
    """,
    
    #5.1 DeepSeek 
    "deepseek-chat":"""
        Model: DeepSeek Chat
        
        Cost: 
        Input = $0.28 <= 1M tokens
        Output = $0.42 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 128,000 tokens
        Output = 4k-Default / 8k-Max tokens

        Misc: 
        4x Fast
        4x Clever 
        Thinking: No
        Knowledge: 31/05/2024 

        Agency: 
        - Chat
        - Classifier
        - Summarizer
    """,

    #5.2 DeepSeek 
    "deepseek-reasoner":"""
        Model: DeepSeek Reasoner
        
        Cost: 
        Input = $0.28 <= 1M tokens
        Output = $0.42 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 128,000 tokens
        Output = 32,000-Default / 64,000-Max tokens

        Misc: 
        4x Fast
        4x Clever 
        Thinking: Yes
        Knowledge: 31/05/2024 

        Agency: 
        - Coder
        - Chat
        - Classifier
        - Summarizer
    """,

    #6.1 Alibaba
    "qwen3-max":"""   
        Model: Qwen3 Max      
        Cost: 
        Input:  $1.20 <= 32k tokens/ $2.40 32k-128k tokens/ $3 128k-256k tokens
        Output: $6.00 <= 32k tokens/ $12 32k-128k tokens/   $15 128k-256k tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 252k
        Output = 64k

        Misc: 
        3x Fast
        5x Clever 
        Thinking: Available 
        Knowledge: ?

        Agency:
        - Code 
    """,

    #6.2 Alibaba
    "qwen3-coder-plus":"""  
        Model: Qwen3 Coder Plus       
        Cost: 
        Input:  $1.00 <= 32k tokens/ $1.80 <= 128k tokens/ $6 <= 1M tokens
        Output: $5.00 <= 32k tokens/ $9.00 <= 128k tokens/ $60.00 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 1M tokens
        Output = 64k tokens

        Misc: 
        2x Fast
        5x Clever 
        Thinking: Available 
        Knowledge: ?

        Agency:
        - Code 
    """,

    #6.3 Alibaba
    "qwen3-coder-flash":"""  
        Model: Qwen3 Coder Flash       
        Cost: 
        Input:  $0.30 <= 32k tokens/ $0.50 <= 128k tokens/ $0.80 <= 256k tokens/ $1.6 <= 1M tokens
        Output: $1.50 <= 32k tokens/ $2.50 <= 128k tokens/ $4.00 <= 256k tokens/ $9.6 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 997k tokens
        Output = 64k tokens

        Misc: 
        2x Fast
        5x Clever 
        Thinking: Available 
        Knowledge: ?

        Agency:
        - Code 
    """,

    #6.4 Alibaba
    "qwen-plush":"""   
        Model: Qwen Plus      
        Cost: 
        Input:  $0.40 <= 256k tokens/ $1.2 <= 1M tokens
        Output: $1.20 <= 256k tokens/ $3.6 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 995k tokens
        Output = 32k

        Misc: 
        3x Fast
        4x Clever 
        Thinking: Available 
        Knowledge: ?

        Agency:
        - Code 
        - Chat
        - Classifier
        - Summarizer
    """,

    #6.5 Alibaba
    "qwen-flash":"""  
        Model: Qwen Flash       
        Cost: 
        Input:  $0.05 <= 256k tokens/ $0.25 <= 1M tokens
        Output: $0.40 <= 256k tokens/ $2.00 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Input  = 995k tokens
        Output = 32k tokens

        Misc: 
        5x Fast
        3x Clever 
        Thinking: Available 
        Knowledge: ?

        Agency: 
        - Chat
        - Classifier
        - Summarizer
    """,

    #7.1 Moonshot
    "kimi-k2-0905-preview":"""
        Model: Kimi K2
        Cost: 
        Input = $0.15 <= 1M tokens
        Output = $2.50 <= 1M tokens

        Data Type:
        Input = Text
        Output = Text

        Context Length:
        Window: 256k tokens
        
        Misc: 
        4x Fast
        3x Clever 
        
        Agency: 
        - Chat
        - Classifier
        - Summarizer
    """,

    
    #7.2 Moonshot
    "kimi-k2-turbo-preview":"""
        Model: Kimi K2 Turbo
        Cost: 
        Input = $0.15 <= 1M tokens
        Output = $8.00 <= 1M tokens

        Data Type:
        Input = Text 
        Output = Text

        Context Length:
        Window: 256k tokens
        
        Misc: 
        5x Fast
        3x Clever 

        Agency: 
        - Chat
        - Classifier
        - Summarizer
    """,
    
    #7.3 Moonshot
    "kimi-k2-thinking":"""
        Model: Kimi K2 Thinking
        Cost: 
        Input = $0.15 <= 1M tokens
        Output = $2.50 <= 1M tokens

        Data Type:
        Input = (Text, Image) 
        Output = Text

        Context Length:
        Window: 256k tokens
        
        Misc: 
        3x Fast
        4x Clever 

        Agency: 
        - Coder
        - Chat
        - Classifier
        - Summarizer
    """,
    
    #7.4 Moonshot
    "kimi-k2-thinking-turbo":"""
        Model: Kimi K2 Thinking Turbo
        Cost: 
        Input = $0.15 <= 1M tokens
        Output = $8.00 <= 1M tokens

        Data Type:
        Input = Text
        Output = Text

        Context Length:
        Window: 256k tokens
        
        Misc: 
        4x Fast
        5x Clever 

        Agency: 
        - Coder
        - Chat
        - Classifier
        - Summarizer
    """,
}

# Agencies
# -----------------------------------------------------------------------------
PURPOSE_TAGS = [
    "admin",
    "chat",
    "coder",
    "classifier",
    "summarizer",  
    "imagetexter",
    # "textimager",
    # "imageeditor"
]

# -----------------------------------------------------------------------------
EMBEDDING_MODELS = {
    "openai": [
    "text-embedding-3-small",
    "text-embedding-3-large",
    ],
}


GPT_MODELS_LATEST = [
    "gpt-5.2",                     
    "gpt-5.2-chat-latest",          # $1.75	$0.175	$14.00
    "gpt-5.2-pro",                  # $21.00	-	$168.00
    "gpt-5.1",                      # $1.25	$0.125	$10.00
    "gpt-5.1-chat-latest",          # $1.25	$0.125	$10.00
    "gpt-5.1-codex-mini",           
    "gpt-5.1-codex-max",  
    "gpt-5",
    "gpt-5-nano",
    "gpt-5-mini",    
]
