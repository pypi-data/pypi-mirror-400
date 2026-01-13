# from dotenv import load_dotenv
from openai import OpenAI
# import os
import json
from json import JSONDecoder
from openai import RateLimitError
from forgecodecli.config import load_config
from forgecodecli.secrets import load_api_key

# Load env
# load_dotenv()

def get_client():
    config = load_config()
    api_key = load_api_key()

    if not config:
        raise RuntimeError(
            "ForgeCodeCLI is not set up. Run `forgecodecli init`."
        )

    if not api_key:
        raise RuntimeError(
            "API key not found. Run `forgecodecli init` again."
        )

    provider = config.get("provider")

    if provider == "gemini":
        return OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    raise RuntimeError(f"Unsupported provider: {provider}")


# client = OpenAI(
#     api_key=os.getenv("GEMINI_API_KEY"),
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

SYSTEM_PROMPT = """
You are an agent that decides what action to take.

CRITICAL RULES:
1. Each user request requires AT MOST TWO action that makes a change (write_file, create_dir, read_file, or list_files)
2. After you have completed all required actions
(up to the allowed limit), respond with "answer"
3. Do NOT take multiple write_file or create_dir actions
4. Do NOT repeat actions

Actions available:
- "read_file": read a file
- "list_files": list directory contents
- "write_file": write/create a file
- "create_dir": create a directory
- "answer": respond to the user (use this after task is complete)

RESPONSE FORMAT - You MUST respond ONLY with valid JSON, nothing else:
{
  "action": "answer",
  "args": {
    "text": "Your message here"
  }
}

Examples:
- User: "create file.py with print('hello')" → write_file → ✅ appears → immediately return answer
- User: "read file.py" → read_file → content appears → immediately return answer
- User: "what's in src?" → list_files → files appear → immediately return answer


"""

def think(messages: list[dict]) -> dict:
    config = load_config()
    model = config.get("model", "gemini-2.5-flash")
    try:
      client = get_client()
      response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages
    )
    except RateLimitError as e:
      return {
        "action": "answer",
        "args": {
            "text": "⚠️ Rate limit hit. Please wait a few seconds and try again."
        }
    }
    except Exception as e:
      return {
        "action": "answer",
        "args": {
            "text": f"❌ LLM error: {str(e)}"
        }
    }


    content = response.choices[0].message.content
    
    # Handle empty response
    if content is None or not content.strip():
        return {
            "action": "answer",
            "args": {
                "text": "Task completed successfully!"
            }
        }
    
    cleaned = content.strip()

    # Robust JSON extraction
    decoder = JSONDecoder()
    
    # Try to find JSON object in the content
    idx = cleaned.find("{")
    if idx == -1:
        return {
        "action": "answer",
        "args": {
            "text": cleaned
        }
    }
    
    # Extract from first { onwards
    cleaned = cleaned[idx:]
    
    # Try to decode JSON, handling partial/malformed content
    try:
        obj, _ = decoder.raw_decode(cleaned)
        return obj
    except json.JSONDecodeError:
        # If it fails, try to find the end of a valid JSON object
        # by trying progressively shorter strings from the end
        for end_pos in range(len(cleaned), idx, -1):
            try:
                obj, _ = decoder.raw_decode(cleaned[:end_pos])
                return obj
            except json.JSONDecodeError:
                continue
        
        raise ValueError(f"Could not parse JSON from LLM output: {cleaned[:100]}...")
