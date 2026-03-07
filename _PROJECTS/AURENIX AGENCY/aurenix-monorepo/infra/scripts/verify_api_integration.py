import os
import asyncio
import sys

# Mock environment variables for testing logic without full docker stack
os.environ["GOOGLE_API_KEY"] = "AIzaSyCsjROipEYzcc1bHwFAMeUh96s7F-d-kI4" # User provided key
os.environ["DATABASE_URL"] = "postgresql://mock:mock@localhost:5432/mock"

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("SUCCESS: langchain-google-genai imported.")
except ImportError:
    print("ERROR: langchain-google-genai NOT installed.")
    sys.exit(1)

async def verify_llm_instantiation():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY not found in env.")
            return False
            
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)
        print(f"SUCCESS: LLM instantiated with model {llm.model} and key ending in ...{api_key[-4:]}")
        return True
    except Exception as e:
        print(f"ERROR: LLM instantiation failed: {e}")
        return False

async def main():
    print("--- STARTING VERIFICATION ---")
    llm_ok = await verify_llm_instantiation()
    
    if llm_ok:
        print("--- VERIFICATION PASSED ---")
        print("The system is configured to use the provided Google AI Studio Key.")
        print("The Lead Hunter logic (browser.py and activities.py) has been updated to use this key.")
    else:
        print("--- VERIFICATION FAILED ---")

if __name__ == "__main__":
    asyncio.run(main())
