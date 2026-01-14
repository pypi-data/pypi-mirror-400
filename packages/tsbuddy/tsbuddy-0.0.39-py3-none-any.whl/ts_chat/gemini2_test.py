import os
import json
import sys # For clean exit on exception
from google import genai
from google.genai.types import FunctionDeclaration, Part

# --- Import your local modules ---
# NOTE: Ensure 'tsbuddy' and all internal functions are importable from the current environment
try:
    from tsbuddy.tslog2csv.tslog2csv import main as tsbuddy_main
    from tsbuddy.extracttar.extract_ts_tar import main as extract_all_main
    from tsbuddy.aos.aosdl import main as aosdl_main, lookup_ga_build, aosup
    from tsbuddy.log_analyzer.logparser import main as logparser_main
    from tsbuddy.log_analyzer.get_techsupport import grab_tech_support
    # from src.analyze.graph_hmon import main as graph_hmon_main
except ImportError as e:
    print(f"⚠️ Warning: Local module import failed. Tools will not be functional. Error: {e}")

# In the main() function, modify step 2:
# 2. Create a Chat Session with Tools

system_prompt = (
    "You are an expert network engineer's assistant named 'TS-Buddy'. "
    "Your primary goal is to **ALWAYS** use the provided tools to interact "
    "with network devices or process log files. "
    "If a user asks to 'grab tech support files', 'get logs', or 'download' "
    "from an IP address, you **MUST** call the 'get_techsupport_main' function. "
    "Do not provide generic instructions on how to manually perform the task. "
    "You exist only to route the user's request to the correct internal tool."
)

# --- Configuration & Setup ---
ENV_FILE = os.path.join(os.path.expanduser("~"), ".tsbuddy_secrets")
ACTIVE_MODEL = "gemini-2.5-flash"

def load_env_file():
    """Load key-value pairs from the secrets file into os.environ."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, sep, value = line.strip().partition("=")
                    if sep:
                        # Use os.environ.get to ensure keys are not overwritten if already set
                        os.environ.setdefault(key.strip(), value.strip())

def append_to_env_file(key, value):
    """Append a new key=value to the secrets file."""
    # Ensure the directory exists if the file is being created
    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
    with open(ENV_FILE, "a") as f:
        f.write(f"\n{key}={value}\n")

# Load environment variables
load_env_file()

# --- Gemini API Key Handling ---
if "GEMINI_API_KEY" not in os.environ:
    api_key = input("Enter your Google Gemini API key: ").strip()
    if not api_key:
        print("🚨 API key is required to run the client. Exiting.")
        sys.exit(1)
    os.environ["GEMINI_API_KEY"] = api_key
    append_to_env_file("GEMINI_API_KEY", api_key)

# --- Function Router (Includes robust argument handling) ---
def function_router(name: str, args: dict):
    """
    Calls the appropriate Python function based on the model's request.
    Includes robust logic to handle common model argument hallucinations.
    """
    print(f"▶️ Calling function: {name} with args: {args}")
    args = args or {}

    if name == "lookup_ga_build":
        return lookup_ga_build()

    elif name == "get_techsupport_main":
        hosts = args.get("hosts", [])
        
        # 🟢 FIX: Robustly handle model using 'ip_address' instead of 'hosts' array
        ip_address_str = args.get("ip_address")
        if not hosts and ip_address_str:
             hosts = [{"ip": ip_address_str}]
        
        # Collect credentials interactively if not provided by the model
        for host in hosts:
            if not host.get("username"):
                host["username"] = input(f"Enter username for {host['ip']} [admin]: ") or "admin"
            if not host.get("password"):
                host["password"] = input(f"Enter password for {host['ip']} [switch]: ") or "switch"
        
        if not hosts:
             return "Error: No hosts provided for tech support gathering."
             
        return grab_tech_support(hosts)

    elif name == "extract_all_main":
        return extract_all_main()
    elif name == "tsbuddy_main":
        return tsbuddy_main()
    elif name == "logparser_main":
        return logparser_main()
    elif name == "aosup":
        return aosup()
    elif name == "aosdl_main":
        return aosdl_main(**args)
    
    else:
        return f"Unknown function: {name}"

# --- Gemini Tool Declarations ---

# The original raw_tool_declarations were correct.
raw_tool_declarations = [
    # 1. lookup_ga_build (aosga)
    {"name": "lookup_ga_build", "description": "Get GA Build, Family, or Upgrade (aosga)"},
    # 2. get_techsupport_main (ts-get)
    {
        "name": "get_techsupport_main",
        "description": "Run tech support gatherer (ts-get) from one or more hosts. You can use 'ip_address' as a shorthand for a single host.",
        "parameters": {
            "type": "object",
            "properties": {
                # Added 'ip_address' as a potential shorthand for the model to use
                "ip_address": {"type": "string", "description": "Shorthand for a single host IP address."},
                "hosts": {
                    "type": "array",
                    "description": "A list of host objects to connect to. Each must have 'ip'. Username/password are optional.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["ip"],
                    },
                }
            },
        },
    },
    # 3. extract_all_main (ts-extract)
    {"name": "extract_all_main", "description": "Run tech_support_complete.tar extractor (ts-extract)"},
    # 4. tsbuddy_main (ts-csv)
    {"name": "tsbuddy_main", "description": "Run tech_support.log to CSV converter (ts-csv)"},
    # 5. logparser_main (ts-log)
    {"name": "logparser_main", "description": "Run swlog parser to CSV & JSON (ts-log)"},
    # 6. aosup
    {"name": "aosup", "description": "Run AOS Upgrader (aosup)"},
    # 7. aosdl_main (AOS download)
    {
        "name": "aosdl_main",
        "description": "Download an AOS version file to a device.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {"type": "string", "description": "The destination folder on the device (e.g., 'working')."},
                "reload_when_finished": {"type": "boolean", "description": "Set to true to automatically reload the device after the download is complete."},
                "found_ga_build": {"type": "string", "description": "The full AOS version string (e.g., '8.9.221.R03') to download."},
                "hosts": {
                    "type": "array",
                    "description": "A list of host objects (each with 'ip', 'username', 'password') to download the file to.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["ip"],
                    },
                },
            },
            "required": ["folder_name", "reload_when_finished", "found_ga_build", "hosts"],
        },
    },
]

# Convert the raw dictionaries into FunctionDeclaration objects
tools = [FunctionDeclaration(**d) for d in raw_tool_declarations]

# --- Main Chatbot Loop ---
def main():
    """Initializes and runs a chat session with the Gemini API."""
    try:
        client = genai.Client()
    except Exception as e:
        print(f"🚨 Error: Failed to initialize the Gemini client. Details: {e}")
        sys.exit(1)

    try:
        print(f"Starting chat session with model: {ACTIVE_MODEL}")
        
        # Create a Chat Session with the list of FunctionDeclaration objects
        # CORRECT: Both system_instruction and tools are in the config dictionary
        chat = client.chats.create(
            model=ACTIVE_MODEL,
            config={
                "tools": tools,
                "system_instruction": system_prompt  # 🥳 Pass it here
            }
        )
    except Exception as e:
        print(f"🚨 Error: Could not create chat session. Details: {e}")
        sys.exit(1)

    print("\n--- Gemini Chat ---")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    # Main Chat Loop
    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit"]:
                print("\nEnding chat session. Goodbye! 👋")
                break

            if not user_input.strip():
                continue

            # 1. Send message and get the model's response
            response = chat.send_message(user_input)

            # 2. Check for and handle function calls
            if response.function_calls:
                tool_outputs = []
                for fc in response.function_calls:
                    # Execute the local function
                    result = function_router(name=fc.name, args=dict(fc.args))
                    print(f"🤖 Function Execution Result: {result}")
                    
                    # Create the tool output payload
                    tool_outputs.append(
                        Part.from_function_response(
                            name=fc.name,
                            response={"result": str(result)} # Encapsulate output in a 'result' dict
                        )
                    )

                # 3. Send function results back to the model
                # Note: The subsequent send_message automatically uses the tool_outputs as the next message part.
                response = chat.send_message(tool_outputs)

            # 4. Print the final text response from the model
            print(f"Gemini: {response.text}\n")

        except Exception as e:
            print(f"\n🚨 An unexpected error occurred: {e}")
            break

if __name__ == "__main__":
    main()