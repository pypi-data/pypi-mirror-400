import os
from google import genai

# --- Configuration ---
FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"
ACTIVE_MODEL = PRO_MODEL  # Change as needed

ENV_FILE = os.path.join(os.path.expanduser("~"), ".tsbuddy_secrets")

def load_env_file():
    """Load key-value pairs from .env into os.environ"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, sep, value = line.strip().partition("=")
                    if sep:  # Only set if '=' was found
                        os.environ.setdefault(key, value)
                        #print(f"Loaded {key} from env file. value length: {len(value)}")

def append_to_env_file(key, value):
    """Append a new key=value to .env"""
    with open(ENV_FILE, "a") as f:
        f.write(f"{key}={value}\n")

# Load .env into environment
load_env_file()

# Prompt if API key not set
if "GEMINI_API_KEY" not in os.environ:
    api_key = input("Enter your Gemini API key: ").strip()
    os.environ["GEMINI_API_KEY"] = api_key
    append_to_env_file("GEMINI_API_KEY", api_key)

def run_chat_session():
    """
    Initializes a chat session with the Gemini 2.5 Flash model and runs a
    continuous chat loop until the user types 'exit' or 'quit'.
    """
    # 1. Initialize the Client
    try:
        # The client automatically uses the GEMINI_API_KEY environment variable.
        api_key = os.environ["GEMINI_API_KEY"]
        #print(f"api_key length: {len(api_key)}")
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print("🚨 Error: Failed to initialize the Gemini client.")
        print(f"Please ensure you have set the GEMINI_API_KEY environment variable. Details: {e}")
        return

    # 2. Create a Chat Session
    # The `chats` service maintains conversation history automatically.
    try:
        print(f"Starting chat session with model: {ACTIVE_MODEL}")
        chat = client.chats.create(model=ACTIVE_MODEL)
    except Exception as e:
        print(f"🚨 Error: Could not create chat session. Details: {e}")
        return

    print("\n--- Gemini Chat ---")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    # 3. Main Chat Loop
    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("\nEnding chat session. Goodbye! 👋")
                break

            if not user_input.strip():
                continue

            # Send the user message and get the model's response
            response = chat.send_message(user_input)

            # Print the model's response
            print(f"Gemini: {response.text}\n")

        except Exception as e:
            print(f"\n🚨 An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    run_chat_session()