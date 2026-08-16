from ollama import chat

messages = []

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    messages.append({"role": "user", "content": user_input})

    response = chat(model="qwen3:8b", messages=messages)

    #Get the AI's reply
    ai_response = response["message"]["content"]

    print("Assistant:", ai_response)

    #Store the AI's reply
    messages.append({"role": "assistant", "content": ai_response})