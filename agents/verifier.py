from typing import Dict, Any, List
from llm.client import generate_structured_response


VERIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "verified": {"type": "boolean"},
        "issues": {
            "type": "array",
            "items": {"type": "string"}
        },
        "summary": {"type": "string"},
        "needs_retry": {"type": "boolean"},
        "retry_steps": {
            "type": "array",
            "items": {"type": "integer"}
        }
    },
    "required": ["verified", "summary"]
}


def verify_results(results: List[Dict[str, Any]], original_plan: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validates execution results, identifies issues, and formats final structured output."""
    if not results:
        return {
            "verified": False,
            "summary": "No results to verify",
            "results": [],
            "final_output": {}
        }
    
    results_summary = []
    for result in results:
        step_info = {
            "step": result.get("step"),
            "tool": result.get("tool"),
            "success": result.get("success", False),
            "has_output": bool(result.get("output")),
            "has_error": isinstance(result.get("output"), dict) and "error" in result.get("output", {})
        }
        results_summary.append(step_info)
    
    prompt = f"""You are an AI Operations Verifier Agent. Your role is to validate execution results and ensure completeness.

Execution Results Summary:
{results_summary}

Full Results:
{results}

Analyze the results and determine:
1. Are all steps completed successfully?
2. Are there any missing or incomplete outputs?
3. Are there any errors that need to be addressed?
4. Should any steps be retried?
5. Provide a clear summary of the verification

Return a JSON object with:
- verified: boolean indicating if all results are valid
- issues: array of any issues found
- summary: human-readable summary of verification
- needs_retry: boolean indicating if retry is needed
- retry_steps: array of step numbers that should be retried (if any)"""

    try:
        verification = generate_structured_response(prompt, VERIFICATION_SCHEMA)
        
        final_output = {
            "task_completed": verification.get("verified", False),
            "summary": verification.get("summary", "Verification completed"),
            "total_steps": len(results),
            "successful_steps": sum(1 for r in results if r.get("success")),
            "failed_steps": sum(1 for r in results if not r.get("success")),
            "issues": verification.get("issues", []),
            "results": results
        }
        
        if verification.get("verified"):
            formatted_data = {}
            for result in results:
                tool = result.get("tool", "").split(".")[-1]
                if result.get("success"):
                    formatted_data[tool] = result.get("output")
            final_output["data"] = formatted_data
        
        return {
            "verified": verification.get("verified", False),
            "summary": verification.get("summary", "Verification completed"),
            "needs_retry": verification.get("needs_retry", False),
            "retry_steps": verification.get("retry_steps", []),
            "results": results,
            "final_output": final_output
        }
        
    except Exception as e:
        print(f"Verifier error: {e}")
        all_success = all(r.get("success", False) for r in results)
        return {
            "verified": all_success,
            "summary": f"Verification completed with {'success' if all_success else 'errors'}",
            "needs_retry": not all_success,
            "retry_steps": [r.get("step") for r in results if not r.get("success")],
            "results": results,
            "final_output": {
                "task_completed": all_success,
                "summary": "Basic verification completed",
                "results": results
            }
        }
