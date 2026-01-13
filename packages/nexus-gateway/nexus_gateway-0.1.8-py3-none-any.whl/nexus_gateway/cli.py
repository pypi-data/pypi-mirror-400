import os
import sys
import time
from .client import NexusClient

def main():
    print("\n========================================")
    print("    Nexus Gateway - Interactive CLI")
    print("========================================")

    # 1. Get Key
    api_key = os.getenv("NEXUS_API_KEY")
    if not api_key:
        try:
            api_key = input("🔑 Enter your Nexus API Key: ").strip()
        except KeyboardInterrupt:
            sys.exit(0)

    # 2. Validate Key (The Fix)
    print("Connecting...", end="\r")
    client = NexusClient(api_key=api_key)
    
    if not client.validate_key():
        print("\n❌ Error: Invalid API Key. Please check your key.")
        print("Get a key at: https://nexus-gateway.org")
        return

    print("✅ Connected! Type 'exit' to quit.\n")

    # 3. Chat Loop
    while True:
        try:
            user_input = input("\033[1mYou:\033[0m ") # Bold text
            
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye! 👋")
                break

            if not user_input.strip():
                continue

            print("\033[1;34mNexus:\033[0m ", end="", flush=True) # Blue text

            # THE STREAMING MAGIC
            try:
                # We ask for a stream, and we loop over the chunks
                for chunk in client.chat(user_input, stream=True):
                    print(chunk, end="", flush=True)
                    # Tiny sleep makes it look cooler (optional)
                    # time.sleep(0.01) 
                print("\n")
                
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break

if __name__ == "__main__":
    main()