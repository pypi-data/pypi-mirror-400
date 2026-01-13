from google import genai

# 🔴 HARD-CODED KEY (as requested)
GEMINI_API_KEY = "AIzaSyBPq4BsbwsQUao4cAULGtkqWnPPl6fGfao"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are a competitive programming assistant. No commenting the code whatsoever. "
    "Give ONLY the required output. No Comments. No explanations. "
    "If code is asked, give ONLY code.  NO COMMENTS IN THE CODE. "
    "No explanation. No comments. No extra text."
)

def ask(prompt: str):
    stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=[
            SYSTEM_PROMPT,
            prompt
        ]
    )

    for chunk in stream:
        if chunk.text:
            print(chunk.text, end="", flush=True)

    print()