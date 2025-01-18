import google.generativeai as gemini
import os
from dotenv import load_dotenv
load_dotenv()

gemini.configure(api_key=os.getenv("GEMINI_KEY"))

model = gemini.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Explain how AI works")
print(response.text)



