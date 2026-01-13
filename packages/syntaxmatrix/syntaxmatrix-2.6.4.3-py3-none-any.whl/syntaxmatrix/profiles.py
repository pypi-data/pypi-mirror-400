# syntaxmatrix/profiles.py
from openai import OpenAI
from google import genai
import anthropic
from datetime import date
from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}

def _refresh_profiles() -> None:
    _profiles.clear()
    for p in list_profiles():
        prof = load_profile(p["name"])
        if prof:
            _profiles[prof["purpose"]] = prof

def refresh_profiles_cache() -> None:
    _refresh_profiles()
            
def get_profile(purpose: str) -> dict:
    prof = _profiles.get(purpose)
    if prof:
        return prof
    _refresh_profiles()
    return _profiles.get(purpose)

def get_profiles():
    return list_profiles()

def get_client(profile):
    
    provider = profile["provider"].lower()
    model = profile["model"]
    api_key = profile["api_key"]

    #1 - Google - gemini series
    if provider == "google":    
        return  genai.Client(api_key=api_key)
    
    #2 OpenAI gpt-5 series
    if provider == "openai":    
        return OpenAI(api_key=api_key)
    
    #3 - Anthropic claude series
    if provider == "anthropic": 
        return anthropic.Anthropic(api_key=api_key)
    
    #4 - xAI - grok series
    if provider == "xai":   
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    
    #5 - DeepSeek chat model
    if provider == "deepseek":
        url_special = "https://api.deepseek.com/v3.2_speciale_expires_on_20251215"
        url_default = "https://api.deepseek.com"
        expiry_date = date(2025, 12, 15)
        today = date.today()
        if today < expiry_date:
            base_url = url_special
        else:
            base_url = url_default
        return OpenAI(api_key=api_key, base_url=base_url)
    
    #6 - Moonshot chat model
    if provider == "moonshot":  #5
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
    
    #7 - Alibaba qwen series
    if provider == "alibaba":   #6
        return OpenAI(api_key=api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",)
    
    #8 - ZAI GLM series
    if provider == "zai":
        url = ""
        if profile.get('name') == "coding":
            url = "https://api.z.ai/api/coding/paas/v4"
        else: url = "https://api.z.ai/api/paas/v4"
        return OpenAI(api_key=api_key, base_url=url)
    
    
def drop_cached_profile_by_name(profile_name: str) -> bool:
    """
    Remove the cached profile with this name (if present) from the in-memory map.
    Returns True if something was removed.
    """
    removed = False
    for purpose, prof in list(_profiles.items()):
        if isinstance(prof, dict) and prof.get("name") == profile_name:
            _profiles.pop(purpose, None)
            removed = True
    return removed