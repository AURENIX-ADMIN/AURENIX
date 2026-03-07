
import os
from langchain_google_vertexai import ChatVertexAI

try:
    print("Testing Vertex AI Auth...")
    llm = ChatVertexAI(model_name="gemini-pro")
    response = llm.invoke("Hello, are you working?")
    print("Success! Response:", response.content)
except Exception as e:
    print("Auth Failed:", e)
