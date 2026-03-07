
import os
from typing import Optional, List, Dict, Any
# Correct imports based on verification
from browser_use import Browser, Agent
from langchain_core.messages import HumanMessage, SystemMessage

class BrowserManager:
    """
    Wrapper for 'browser-use' library to enable AI agents to control a headless browser.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        
    async def initialize(self):
        """
        Lazy initialization of the browser to save resources.
        """
        if not self.browser:
            try:
                # Direct instantiation as verified (no BrowserConfig)
                self.browser = Browser(headless=self.headless)
            except Exception as e:
                print(f"Error initializing Browser: {e}")
                raise e
            
    async def navigate_and_extract(self, url: str, instruction: str) -> str:
        """
        Navigates to a URL and performs an action/extraction based on natural language instruction.
        """
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            print(f"[BrowserManager] STARTING AGENT for: {url}")
            
            # Initialize the agent with Google GenAI (Gemini) using API Key
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
            
            # SAFE instantiation: Try passing browser reuse, fallback if not supported
            try:
                agent = Agent(
                    task=f"Go to {url}. {instruction}",
                    llm=llm,
                    browser=self.browser
                )
            except TypeError:
                print("[BrowserManager] Warning: Agent does not accept 'browser' arg. Creating new instance.")
                agent = Agent(
                    task=f"Go to {url}. {instruction}",
                    llm=llm
                )
            
            # Execute the agent
            result = await agent.run()
            return str(result)
            
        except ImportError:
            return "Error: langchain-google-genai not installed."
        except Exception as e:
            return f"Error running browser agent: {e}"

    async def close(self):
        if self.browser:
            # Inspection showed no 'close' method on BrowserSession, but let's be safe
            # If it's a context manager, we might leave it.
            # But if it has close, call it.
            if hasattr(self.browser, "close"):
                await self.browser.close()
            self.browser = None
