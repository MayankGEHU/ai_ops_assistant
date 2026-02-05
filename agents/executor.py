from typing import Dict, Any, List
from tools.github_tool import search_repos
from tools.weather_tool import get_weather

TOOL_MAP = {
    "github.search_repos": search_repos,
    "weather.get_weather": get_weather
}


def execute_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Executes plan steps sequentially, calling tools and returning results per step."""
    results = []
    steps = plan.get("steps", [])
    
    if not steps:
        return [{"error": "No steps to execute"}]
    
    print(f"Executor starting execution of {len(steps)} step(s)")
    
    for idx, step in enumerate(steps, 1):
        tool_name = step.get("tool")
        tool_input = step.get("input", {})
        description = step.get("description", f"Step {idx}")
        
        print(f"  Step {idx}: {description} using {tool_name}")
        
        tool_func = TOOL_MAP.get(tool_name)
        
        if not tool_func:
            results.append({
                "step": idx,
                "tool": tool_name,
                "description": description,
                "output": {"error": f"Unknown tool: {tool_name}"},
                "success": False
            })
            continue
        
        try:
            output = tool_func(**tool_input)
            
            success = not (isinstance(output, dict) and output.get("error"))
            
            results.append({
                "step": idx,
                "tool": tool_name,
                "description": description,
                "input": tool_input,
                "output": output,
                "success": success
            })
            
            if success:
                print(f"    [OK] Step {idx} completed successfully")
            else:
                print(f"    [FAIL] Step {idx} failed: {output.get('error', 'Unknown error')}")
                
        except TypeError as e:
            results.append({
                "step": idx,
                "tool": tool_name,
                "description": description,
                "input": tool_input,
                "output": {"error": f"Invalid parameters: {str(e)}"},
                "success": False
            })
            print(f"    [FAIL] Step {idx} failed: Invalid parameters")
        except Exception as e:
            results.append({
                "step": idx,
                "tool": tool_name,
                "description": description,
                "input": tool_input,
                "output": {"error": f"Execution error: {str(e)}"},
                "success": False
            })
            print(f"    [FAIL] Step {idx} failed: {str(e)}")
    
    return results
