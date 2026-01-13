from .client import ask

def run():
    print("Gemini CLI (type 'exit' to quit)")
    while True:
        q = input("You > ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        print("Gemini >", ask(q))
