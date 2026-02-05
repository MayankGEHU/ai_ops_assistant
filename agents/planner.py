import json
from llm.client import generate_response


def create_plan(task):

    prompt = f"""
You are an AI planner.

Convert user task into JSON execution steps.

Rules:
- Only return JSON
- Do NOT explain
- Do NOT add text before or after JSON

Available tools:
1. github.search_repos(query, limit)
2. weather.get_weather(city)

Output format EXACTLY:

{{
  "steps": [
    {{
      "tool": "weather.get_weather",
      "input": {{
        "city": "Delhi"
      }}
    }}
  ]
}}

Task: {task}
"""

    plan_text = generate_response(prompt)

    print("RAW LLM OUTPUT:", plan_text)

    try:
        return json.loads(plan_text)
    except:
        return {"steps": []}
