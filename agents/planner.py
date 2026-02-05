import json
from typing import Dict, Any, List
from llm.client import generate_structured_response

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "enum": ["github.search_repos", "weather.get_weather"]
                    },
                    "input": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "limit": {"type": "integer"},
                            "city": {"type": "string"}
                        }
                    },
                    "description": {"type": "string"}
                },
                "required": ["tool", "input"]
            }
        }
    },
    "required": ["steps"]
}


def create_plan(task: str) -> Dict[str, Any]:
    """Converts natural language task into structured execution plan with tool selections."""
    prompt = f"""You are an AI Operations Planner Agent. Your role is to analyze user tasks and create a structured execution plan.

Available Tools:
1. github.search_repos(query: str, limit: int) - Search GitHub repositories by query
2. weather.get_weather(city: str) - Get current weather for a city

Task: {task}

Analyze the task and create a step-by-step execution plan. For each step:
- Select the appropriate tool (must be one of: "github.search_repos" or "weather.get_weather")
- Provide the required input parameters:
  - For github.search_repos: provide "query" (string) and "limit" (integer)
  - For weather.get_weather: provide "city" (string)
- Add a brief description of what this step accomplishes

CRITICAL: You MUST return ONLY valid JSON in this exact format:
{{
  "steps": [
    {{
      "tool": "weather.get_weather",
      "input": {{"city": "New York"}},
      "description": "Get weather for New York"
    }}
  ]
}}

Do NOT include any text before or after the JSON. Return ONLY the JSON object."""

    try:
        plan = generate_structured_response(prompt, PLAN_SCHEMA)
        
        if not plan or not isinstance(plan, dict):
            print("ERROR: Planner returned invalid response (not a dict)")
            return {"steps": []}
        
        if "steps" not in plan:
            print("ERROR: Planner response missing 'steps' key")
            return {"steps": []}
        
        if not plan.get("steps") or not isinstance(plan["steps"], list):
            print(f"ERROR: Invalid plan structure. Got: {type(plan.get('steps'))}")
            return {"steps": []}
        
        valid_steps = []
        for idx, step in enumerate(plan["steps"]):
            if not isinstance(step, dict):
                print(f"WARNING: Step {idx} is not a dictionary, skipping")
                continue
            
            if "tool" not in step or "input" not in step:
                print(f"WARNING: Step {idx} missing required fields (tool/input), skipping")
                continue
            
            tool = step.get("tool")
            if tool not in ["github.search_repos", "weather.get_weather"]:
                print(f"WARNING: Step {idx} has invalid tool '{tool}', skipping")
                continue
            
            valid_steps.append(step)
        
        if not valid_steps:
            print("ERROR: No valid steps found in plan")
            return {"steps": []}
        
        plan["steps"] = valid_steps
        print(f"[OK] Planner created {len(plan['steps'])} valid step(s)")
        return plan
        
    except Exception as e:
        print(f"ERROR: Planner exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {"steps": []}
