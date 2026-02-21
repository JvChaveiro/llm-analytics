import ollama

def ask(prompt: str, model: str = "qwen2.5-coder:7b-instruct") -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

if __name__ == "__main__":
    result = ask("Escreva um SELECT com GROUP BY para vendas mensais")
    print(result)