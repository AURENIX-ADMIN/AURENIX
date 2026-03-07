from temporalio import activity
import logging

# In production, this interacts with Vertex AI Code Interpreter or a Dockerized Sandbox.
# For this phase, we act as a "Passthrough" to a safe local evaluator or mock.

@activity.defn
async def execute_python(code: str) -> str:
    activity.logger.info(f"Executing Python Code in Sandbox: {code}")
    
    # SAFETY: DO NOT EXECUTE ARBITRARY CODE IN LOCAL DEV ENVIRONMENT WITHOUT SANDBOX.
    # Return mock result to demonstrate architecture.
    
    logging.warning("SANDBOX: Executing code in mock mode for safety.")
    
    if "print" in code:
        return "OUTPUT: [Stdout] " + code.replace("print(", "").replace(")", "").replace('"', "")
    
    return "OUTPUT: [Sandbox Result] Code executed successfully (Mock)."
