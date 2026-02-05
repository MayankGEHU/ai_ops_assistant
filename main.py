import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.planner import create_plan
from agents.executor import execute_plan
from agents.verifier import verify_results
import uvicorn

app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent AI system for task planning, execution, and verification",
    version="1.0.0"
)


class TaskRequest(BaseModel):
    """Request model for task execution"""
    task: str
    max_retries: Optional[int] = 3


class TaskResponse(BaseModel):
    """Response model for task execution"""
    task: str
    plan: dict
    results: list
    verification: dict


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Operations Assistant",
        "version": "1.0.0",
        "endpoints": {
            "/run-task": "POST - Execute a natural language task",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai_ops_assistant"}


@app.post("/run-task", response_model=TaskResponse)
def run_task(request: TaskRequest):
    """
    Main endpoint to execute a natural language task.
    
    Flow:
    1. Planner Agent creates execution plan
    2. Executor Agent executes steps and calls APIs
    3. Verifier Agent validates results
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        TaskResponse with plan, results, and verification
    """
    try:
        # Step 1: Planner Agent - Create execution plan
        print(f"\n{'='*60}")
        print(f"Processing task: {request.task}")
        print(f"{'='*60}\n")
        
        plan = create_plan(request.task)
        
        if not plan.get("steps"):
            error_detail = {
                "error": "Planner failed to create a valid execution plan",
                "task": request.task,
                "plan_received": plan,
                "possible_causes": [
                    "LLM API key might be invalid or missing",
                    "LLM service might be unavailable",
                    "Task might be unclear or not match available tools",
                    "LLM response format might be invalid"
                ],
                "suggestions": [
                    "Check your GEMINI_API_KEY in .env file",
                    "Try a simpler task like 'Get weather in New York'",
                    "Check server console for detailed error messages"
                ]
            }
            print(f"\nERROR: {error_detail}\n")
            raise HTTPException(
                status_code=400,
                detail=error_detail
            )
        
        # Step 2: Executor Agent - Execute plan
        results = execute_plan(plan)
        
        # Step 3: Verifier Agent - Verify results
        verification = verify_results(results, plan)
        
        # Retry logic if needed
        retry_count = 0
        while verification.get("needs_retry") and retry_count < request.max_retries:
            retry_count += 1
            print(f"\nRetry attempt {retry_count}/{request.max_retries}")
            
            retry_steps = verification.get("retry_steps", [])
            if retry_steps:
                # Re-execute failed steps
                retry_plan = {
                    "steps": [
                        plan["steps"][step - 1] 
                        for step in retry_steps 
                        if step <= len(plan["steps"])
                    ]
                }
                retry_results = execute_plan(retry_plan)
                
                # Update original results with retry results
                for retry_result in retry_results:
                    step_num = retry_result.get("step")
                    if step_num:
                        # Find corresponding original result and update
                        for idx, orig_result in enumerate(results):
                            if orig_result.get("step") == step_num:
                                results[idx] = retry_result
                                break
                
                # Re-verify
                verification = verify_results(results, plan)
        
        print(f"\n{'='*60}")
        print(f"Task completed: {verification.get('verified', False)}")
        print(f"{'='*60}\n")
        
        return TaskResponse(
            task=request.task,
            plan=plan,
            results=results,
            verification=verification
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def run_cli():
    """CLI interface for running tasks"""
    if len(sys.argv) < 2:
        print("Usage: python main.py '<task description>'")
        print("\nExample:")
        print("  python main.py 'Get the weather in New York and find top 3 Python repositories'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    print("AI Operations Assistant - CLI Mode")
    print("=" * 60)
    
    try:
        plan = create_plan(task)
        print(f"\nPlan created with {len(plan.get('steps', []))} step(s)")
        
        # Execute plan
        results = execute_plan(plan)
        
        # Verify results
        verification = verify_results(results, plan)
        
        # Display results
        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"\nTask: {task}")
        print(f"Status: {'[OK] Completed' if verification.get('verified') else '[FAIL] Failed'}")
        print(f"Summary: {verification.get('summary', 'N/A')}")
        
        if verification.get("final_output", {}).get("data"):
            print("\nData:")
            import json
            print(json.dumps(verification["final_output"]["data"], indent=2))
        
        print("\nDetailed Results:")
        for result in results:
            status = "[OK]" if result.get("success") else "[FAIL]"
            print(f"  {status} Step {result.get('step')}: {result.get('description', 'N/A')}")
            if not result.get("success"):
                print(f"    Error: {result.get('output', {}).get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running as CLI or server
    if len(sys.argv) > 1 and sys.argv[1] not in ["--server", "-s"]:
        run_cli()
    else:
        # Run as API server
        print("Starting AI Operations Assistant API server...")
        print("API available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        uvicorn.run(app, host="0.0.0.0", port=8000)
