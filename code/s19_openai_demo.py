from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()  # reads OPENAI_API_KEY from .env

messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("Chatbot ready! Type 'quit' to exit.")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break
    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})

    print(f"Assistant: {reply}")
