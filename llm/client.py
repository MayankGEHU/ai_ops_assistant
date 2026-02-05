import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_model_instance = None
_model_name_used = None

def get_model():
    global _model_instance, _model_name_used
    
    if _model_instance is not None:
        return _model_instance
    
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not found in environment variables!")
        print("Please set GEMINI_API_KEY in your .env file")
        return None
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    model_names = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    
    last_error = None
    for model_name in model_names:
        try:
            _model_instance = genai.GenerativeModel(model_name)
            _model_name_used = model_name
            return _model_instance
        except Exception as e:
            last_error = e
            continue
    
    try:
        print("Attempting to find available models...")
        available_models = list(genai.list_models())
        if available_models:
            for model_obj in available_models:
                model_full_name = model_obj.name
                if "gemini" in model_full_name.lower():
                    model_id = model_full_name.split("/")[-1]
                    try:
                        _model_instance = genai.GenerativeModel(model_id)
                        _model_name_used = model_id
                        print(f"[OK] Found working model: {model_id}")
                        return _model_instance
                    except:
                        continue
    except:
        pass
    
    print("ERROR: Could not initialize any Gemini model.")
    if last_error:
        print(f"Last error: {last_error}")
    print("Check your API key at https://makersuite.google.com/app/apikey")
    return None


def generate_response(prompt: str, json_schema: Optional[Dict[str, Any]] = None) -> str:
    """Calls LLM with optional JSON schema constraint. Extracts JSON from markdown blocks if present."""
    try:
        if not GEMINI_API_KEY:
            print("ERROR: GEMINI_API_KEY not configured. Cannot call LLM.")
            return "{}"
        
        model = get_model()
        if model is None:
            print("ERROR: Model not initialized. Check API key.")
            return "{}"
        
        generation_config = {}
        
        if json_schema:
            schema_prompt = f"""
{prompt}

IMPORTANT: You MUST respond with valid JSON that matches this schema:
{json.dumps(json_schema, indent=2)}

Return ONLY the JSON object, no additional text or explanation.
"""
            response = model.generate_content(
                schema_prompt,
                generation_config=generation_config
            )
        else:
            response = model.generate_content(prompt)

        if not response.candidates:
            print("ERROR: LLM returned no candidates")
            return "{}"

        text = response.candidates[0].content.parts[0].text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        return text

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"ERROR: LLM call failed - {error_type}: {error_msg}")
        
        if "404" in error_msg or "not found" in error_msg.lower():
            print(f"  → Model '{_model_name_used}' not available for your API key")
            print("  → Verify your API key at https://makersuite.google.com/app/apikey")
            global _model_instance
            _model_instance = None
        elif "API_KEY" in error_msg or "authentication" in error_msg.lower():
            print("  → Check your GEMINI_API_KEY in .env file")
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            print("  → API quota exceeded or rate limited")
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            print("  → Network connection issue")
        
        return "{}"


def generate_structured_response(prompt: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
    """Returns parsed JSON matching schema; attempts regex extraction on parse failure."""
    response_text = generate_response(prompt, json_schema)
    
    if not response_text or response_text.strip() == "":
        print("ERROR: LLM returned empty response")
        return {}
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}")
        print(f"Response text (full): {response_text}")
        
        import re
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        return {}
