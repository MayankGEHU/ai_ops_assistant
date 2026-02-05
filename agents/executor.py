from tools.github_tool import search_repos
from tools.weather_tool import get_weather

TOOL_MAP = {
    "github.search_repos": search_repos,
    "weather.get_weather": get_weather
}


def execute_plan(plan):

    results = []

    for step in plan.get("steps", []):
        tool_name = step.get("tool")
        tool_input = step.get("input", {})

        tool_func = TOOL_MAP.get(tool_name)

        if not tool_func:
            continue

        try:
            output = tool_func(**tool_input)
        except Exception as e:
            output = {"error": str(e)}

        results.append({
            "tool": tool_name,
            "output": output
        })

    return results
