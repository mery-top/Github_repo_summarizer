import google.generativeai as gemini
import os
from dotenv import load_dotenv
load_dotenv()

gemini.configure(api_key=os.getenv("GEMINI_KEY"))

def generate_ai_description_with_gemini(code_snippets):
    prompt = "Analyze the following code snippets and describe the purpose of the repository:\n"
    for snippet in code_snippets:
        prompt += f"\n---\n{snippet[:1000]}\n"  # Limit the snippet size
    
    model = gemini.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    return response.text



