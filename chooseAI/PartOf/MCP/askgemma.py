import ollama

def ask_gemma(prompt: str, context: str = "") -> str:
    messages = [
        {"role": "system", "content": "You are an assistant that can use web search results to answer questions in Georgian."},
        {"role": "user", "content": f"{prompt}\n\nContext:\n{context}"}
    ]

    try:
        print(f"🤖 model: gemma3:4b")
        response = ollama.chat(model="gemma3:4b", messages=messages)
        
        if "message" in response and "content" in response["message"]:
            return response["message"]["content"].strip()
        
        return str(response)
        
    except ConnectionError as e:
        return f"[ERROR] Ollama doesn't work. write 'ollama serve': {e}"
    except Exception as e:
        return f"[ERROR] Gemma call failed: {e}"