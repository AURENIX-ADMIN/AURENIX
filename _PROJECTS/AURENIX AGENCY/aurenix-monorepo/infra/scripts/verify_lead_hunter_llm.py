import os
import asyncio
import sys

# Script to be run INSIDE the temporal-worker container
# It mimics the logic used in activities.py

async def verify_lead_hunter_ai():
    print("--- LEAD HUNTER AI VERIFICATION ---")
    
    # 1. Check Env
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ FAIL: GOOGLE_API_KEY is missing from environment.")
        sys.exit(1)
    
    if api_key.startswith("AIza"):
        print("✅ PASS: GOOGLE_API_KEY format looks correct (AI Studio).")
    else:
        print(f"⚠️ WARN: GOOGLE_API_KEY may be invalid format: {api_key[:5]}...")

    # 2. Check Import
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ PASS: langchain-google-genai library is installed.")
    except ImportError:
        print("❌ FAIL: langchain-google-genai library is MISSING.")
        sys.exit(1)

    # 3. Check Instantiation & Connectivity
    try:
        print("🔄 TESTING: Instantiating ChatGoogleGenerativeAI...")
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)
        
        # Simple invoke to check auth
        print("🔄 TESTING: Sending 'Hello' to Gemini...")
        response = llm.invoke("Hello, are you ready for lead generation?")
        print(f"✅ PASS: Gemini Responded: {response.content}")
        
    except Exception as e:
        print(f"❌ FAIL: LLM Invocation failed. Error: {e}")
        sys.exit(1)

    print("--- VERIFICATION COMPLETE: ALL SYSTEMS GO ---")

if __name__ == "__main__":
    asyncio.run(verify_lead_hunter_ai())
