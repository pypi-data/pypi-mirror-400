import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, TypedDict
from .engine import IntentObject

class LLMConfig(TypedDict):
    endpoint: str
    headers: Dict[str, str]
    model: str
    max_tokens: Optional[int]
    temperature: Optional[float]

SYSTEM_PROMPT = """You are an API that analyzes conversational intent. 
Given a RESPONSE and CONTEXT, output a JSON object with:
- orientation: "YES" | "NO" | "NON_COMMITTAL" | "UNKNOWN"
- intent_type: string (short descriptor)
- sentiment_tone: "negative" | "neutral" | "positive" | "mixed"
- sentiment_score: number (-1 to 1)
- politeness: "low" | "medium" | "high"
- politeness_score: number (0 to 1)
- mismatch: boolean (true if tone contradicts intent)
- confidence: number (0 to 1)
- evidence_phrases: string[]
- explanation: string (max 2 sentences)

Output ONLY JSON.
"""

def analyze_intent_llm(
    response: str,
    context: Optional[str],
    llm: LLMConfig,
    options: Optional[Any] = None
) -> IntentObject:
    
    user_content = f'Context: {context or "None"}\nResponse: "{response}"'
    
    payload = {
        "model": llm["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": llm.get("temperature", 0),
        "max_tokens": llm.get("max_tokens", 500)
    }
    
    try:
        req = urllib.request.Request(
            llm["endpoint"],
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                **llm["headers"]
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as f:
            resp_body = f.read().decode('utf-8')
            data = json.loads(resp_body)
            
        content = ""
        if "choices" in data and len(data["choices"]) > 0:
             content = data["choices"][0]["message"]["content"]
        else:
             content = json.dumps(data)
             
        # Clean markdown
        content = content.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(content)
        return result 
        
    except Exception as e:
        # User requested clear error if validation fails
        raise RuntimeError(f"LLM analysis failed: {str(e)}")
