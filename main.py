import asyncio

from agent.brain import ask_llm


async def main():

    print("================================")
    print("          ROBOT IA")
    print("================================")
    print()

    print("Modelo conectado.")
    print("Escribe 'salir' para terminar.")
    print()

    while True:

        user_message = input("Tú: ").strip()

        if not user_message:
            continue

        if user_message.lower() in [
            "salir",
            "exit",
            "quit"
        ]:
            print("Apagando robot...")
            break

        try:

            response = await ask_llm(user_message)

            print()
            print(f"🤖 Robot: {response}")
            print()

        except Exception as e:

            print()
            print(f"❌ Error: {e}")
            print()


if __name__ == "__main__":
    asyncio.run(main())