from openai import OpenAI
import json
import os

from tsbuddy.tslog2csv.tslog2csv import main as tsbuddy_main
from tsbuddy.extracttar.extract_ts_tar import main as extract_all_main
from tsbuddy.aos.aosdl import main as aosdl_main, lookup_ga_build, aosup
from tsbuddy.log_analyzer.logparser import main as logparser_main
#from logparser_v3 import main as logparser_main
from tsbuddy.log_analyzer.get_techsupport import grab_tech_support
#from src.analyze.graph_hmon import main as graph_hmon_main

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

def append_to_env_file(key, value):
    """Append a new key=value to .env"""
    with open(ENV_FILE, "a") as f:
        f.write(f"{key}={value}\n")

# Load .env into environment
load_env_file()

# Prompt if API key not set
if "OPENAI_API_KEY" not in os.environ:
    api_key = input("Enter your OpenAI API key: ").strip()
    os.environ["OPENAI_API_KEY"] = api_key
    append_to_env_file("OPENAI_API_KEY", api_key)

# Use the key
# openai.api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# Define your function wrappers
def function_router(name, args=None):
    print(f"Calling function: {name}")
    if name == "lookup_ga_build":
        return lookup_ga_build()
    elif name == "get_techsupport_main":
        hosts = []
        if isinstance(args, dict):
            hosts = args.get("hosts", []) or []
        # Prompt for missing username/password
        for host in hosts:
            if "username" not in host or not host["username"]:
                host["username"] = input(f"Enter username for {host['ip']} [admin]: ") or "admin"
            if "password" not in host or not host["password"]:
                host["password"] = input(f"Enter password for {host['ip']} [switch]: ") or "switch"
        return grab_tech_support(hosts)
    elif name == "extract_all_main":
        return extract_all_main()
    elif name == "tsbuddy_main":
        return tsbuddy_main()
    elif name == "log_analyzer":
        if isinstance(args, dict):
            filename = args.get("filename", "")
            request = args.get("request")
            chassis_selection = args.get("chassis_selection", "all")
            time = args.get("time", "")
            api = args.get("api", True)
            missing = []
            if request is None:
                missing.append("request")
            if missing:
                return f"Missing required arguments: {', '.join(missing)}"
            return logparser_main(filename, request, chassis_selection, time, api)
        else:
            return "Missing or invalid arguments for main."
    elif name == "aosup":
        return aosup()
    elif name == "aosdl_main":
        if isinstance(args, dict):
            folder_name = args.get("folder_name")
            reload_when_finished = args.get("reload_when_finished")
            found_ga_build = args.get("found_ga_build")
            hosts = args.get("hosts")
            missing = []
            if folder_name is None:
                missing.append("folder_name")
            if reload_when_finished is None:
                missing.append("reload_when_finished")
            if found_ga_build is None:
                missing.append("found_ga_build")
            if hosts is None:
                missing.append("hosts")
            if missing:
                return f"Missing required arguments: {', '.join(missing)}"
            return aosdl_main(folder_name, reload_when_finished, found_ga_build, hosts)
        else:
            return "Missing or invalid arguments for aosdl_main."
    elif name == "graph_hmon_main":
        return graph_hmon_main()
    elif name == "change_directory":
        return change_directory()
    elif name == "upgrade_downgrade_choice":
        return upgrade_downgrade_choice()
    elif name == "print_help":
        return print_help()
    else:
        return "Unknown function."

# Register functions for OpenAI API
functions = [
    {
        "name": "lookup_ga_build",
        "description": "Get GA Build, Family, or Upgrade (aosga)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
        {
        "name": "get_techsupport_main",
        "description": "Run tech support gatherer (ts-get)",
        "parameters": {
            "type": "object",
            "properties": {
                "hosts": {
                    "type": "array",
                    "description": "List of host objects to collect tech support from. Each item should include 'ip' and 'username' and 'password'.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"}
                        },
                        "required": ["ip", "username", "password"]
                    }
                }
            },
            "required": []
        }
    },
    {
        "name": "extract_all_main",
        "description": "Run tech_support_complete.tar extractor (ts-extract)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "tsbuddy_main",
        "description": "Run tech_support.log to CSV converter (ts-csv)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "logparser_main",
        "description": "Run swlog parser to CSV & JSON (ts-log)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "aosup",
        "description": "Run AOS Upgrader (aosup)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "aosdl_main",
        "description": "Use this to download an AOS version file to a device. Requires 'folder_name', 'reload_when_finished', 'found_ga_build', and 'hosts'.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_name": {
                    "type": "string",
                    "description": "Folder name on the device to download the image to (e.g., 'working')."
                },
                "reload_when_finished": {
                    "type": "boolean",
                    "description": "Whether to reload the device after download is complete."
                },
                "found_ga_build": {
                    "type": "string",
                    "description": "Full AOS version string to download (e.g., '8.9.221.R03')."
                },
                "hosts": {
                    "type": "array",
                    "description": "List of host objects to collect tech support from. Each item should include 'ip', 'username', and 'password'.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ip": {"type": "string"},
                            "username": {"type": "string"},
                            "password": {"type": "string"}
                        },
                        "required": ["ip", "username", "password"]
                    }
                }
            },
            "required": ["folder_name", "reload_when_finished", "found_ga_build", "hosts"]
        }
    },
    {
        "name": "log_analyzer",
        "description": "Analyzes network log files from a support archive and returns results based on the specified request type and filters.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Path to the .tar archive containing the log files. If not provided, a file picker will prompt the user."
                },
                "request": {
                    "type": "string",
                    "description": "Type of analysis to perform. Options include: 'All Logs', 'Reboot', 'VC', 'Interface', 'OSPF', 'SPB', 'Health', 'Connectity', 'Critical', 'Hardware', 'Upgrades', 'General', 'MACLearning', 'Unused', 'STP', 'Security', 'Unclear', 'Unknown'."
                },
                "chassis_selection": {
                    "type": "string",
                    "description": "Specifies which chassis logs to analyze. Use 'all' to include all chassis."
                },
                "time": {
                    "type": "string",
                    "description": "Timestamp string to filter logs (e.g., '2023-09-15 14:00'). If empty, all logs are included."
                },
                "api": {
                    "type": "boolean",
                    "description": "Whether the output should be formatted for API consumption. Set to true for structured output."
                }
            },
            "required": ["request"]
        }
    },
    {
        "name": "graph_hmon_main",
        "description": "Run HMON Graph tool (ts-graph-hmon)",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "change_directory",
        "description": "Change current working directory",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "upgrade_downgrade_choice",
        "description": "Upgrade or downgrade tsbuddy",
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "print_help",
        "description": "Show help info",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
]

# Main chatbot loop
def main():
    print("💬 Chatbot is ready. Type 'exit' to quit.")
    # Initialize memory (conversation history)
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break
        
        # Add user message to memory
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            functions=functions,
            function_call="auto"
        )
        message = response.choices[0].message
        if message.function_call:
            fn_name = message.function_call.name
            args = json.loads(message.function_call.arguments or "{}")
            result = function_router(fn_name, args)
            
            # # Add assistant function call result to memory
            # messages.append({
            #     "role": "function",
            #     "name": fn_name,
            #     "content": str(result)
            # })

            # ✅ Add function result as an assistant message (not a 'function' role)
            reply = f"The result of `{fn_name}` is: {result}"
            messages.append({"role": "assistant", "content": reply})
            print(f"🤖 Result: {result}")
        else:
            try:
                reply = message["content"]
            except TypeError:
                reply = message.content

            # Add assistant message to memory
            messages.append({"role": "assistant", "content": reply})
            print("🤖", reply)

if __name__ == "__main__":
    main()
