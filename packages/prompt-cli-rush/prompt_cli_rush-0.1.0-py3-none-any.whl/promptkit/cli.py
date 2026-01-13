from promptkit.core import ask

def main():
    print("PromptKit Interactive Console")
    print("Type 'exit' to quit\n")

    history = [
        {
            "role": "system",
            "content": "You assist with programming, DSA, and database queries."
        }
    ]

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            break

        response = ask(user_input, history)

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

        print("\n", response, "\n")
