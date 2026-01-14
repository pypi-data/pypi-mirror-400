import os
import sys
import platform
import json
import argparse
import warnings
from pathlib import Path

# Suppress Pydantic warnings from litellm/pydantic v2 compatibility issues
warnings.filterwarnings("ignore", message=".*Pydantic serializer warnings.*")

import litellm
import pyperclip

CONFIG_FILE = Path.home() / ".clitr_config.json"

def get_os_info():
    return platform.system() + " " + platform.release()

def get_shell_info():
    # Simple heuristic
    if platform.system() == "Windows":
        # Check if running in PowerShell
        if "PSModulePath" in os.environ:
            return "PowerShell"
        return "Command Prompt (cmd.exe)"
    else:
        return os.environ.get("SHELL", "bash")

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}", file=sys.stderr)
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving config: {e}", file=sys.stderr)

def get_recent_history(n=3):
    system = platform.system()
    history_file = None
    
    if system == "Windows":
         appdata = os.environ.get("APPDATA")
         if appdata:
             history_file = Path(appdata) / "Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt"
    elif system in ["Linux", "Darwin"]:
         shell = os.environ.get("SHELL", "")
         if "zsh" in shell:
             history_file = Path.home() / ".zsh_history"
         else:
             history_file = Path.home() / ".bash_history"
             
    if history_file and history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                # Return last n non-empty lines
                return [line.strip() for line in lines if line.strip()][-n:]
        except Exception:
            pass
    return []

def print_config_help():
    print("Configuration Options for --set-config:")
    print("  -local_endpoint=<url>    Set the URL for a local LLM endpoint (e.g., http://localhost:8000/v1)")
    print("  -model=<name>            Set the model name to use (e.g., openai/gpt-4o, hosted_vllm/llama-3)")
    print("  -command_history=<n>     Number of recent shell commands to include in context (default: 3)")
    print("  -api_key=<key>           (Optional) Set OpenAI API key directly in config")
    print("\nUsage Example:")
    print("  clitr --set-config -local_endpoint=http://127.0.0.1:1234/v1 -command_history=5")

def inject_command_to_console(command):
    """
    Injects the command into the console input buffer on Windows.
    This simulates typing the command so the user can just press Enter.
    """
    if platform.system() != "Windows":
        return

    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        return

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    STD_INPUT_HANDLE = -10
    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    if hStdIn == -1 or hStdIn == 0:
        return # Not a console

    KEY_EVENT = 0x0001
    
    # Define necessary structures
    class KEY_EVENT_RECORD_Char(ctypes.Union):
        _fields_ = [("UnicodeChar", wintypes.WCHAR),
                    ("AsciiChar", ctypes.c_char)]

    class KEY_EVENT_RECORD(ctypes.Structure):
        _fields_ = [("bKeyDown", wintypes.BOOL),
                    ("wRepeatCount", wintypes.WORD),
                    ("wVirtualKeyCode", wintypes.WORD),
                    ("wVirtualScanCode", wintypes.WORD),
                    ("uChar", KEY_EVENT_RECORD_Char),
                    ("dwControlKeyState", wintypes.DWORD)]

    class INPUT_RECORD_Event(ctypes.Union):
        _fields_ = [("KeyEvent", KEY_EVENT_RECORD)]

    class INPUT_RECORD(ctypes.Structure):
        _fields_ = [("EventType", wintypes.WORD),
                    ("Event", INPUT_RECORD_Event)]

    records = []
    for char in command:
        # Key Down
        rec_down = INPUT_RECORD()
        rec_down.EventType = KEY_EVENT
        rec_down.Event.KeyEvent.bKeyDown = True
        rec_down.Event.KeyEvent.wRepeatCount = 1
        rec_down.Event.KeyEvent.wVirtualKeyCode = 0 
        rec_down.Event.KeyEvent.wVirtualScanCode = 0
        rec_down.Event.KeyEvent.uChar.UnicodeChar = char
        rec_down.Event.KeyEvent.dwControlKeyState = 0
        records.append(rec_down)

        # Key Up
        rec_up = INPUT_RECORD()
        rec_up.EventType = KEY_EVENT
        rec_up.Event.KeyEvent.bKeyDown = False
        rec_up.Event.KeyEvent.wRepeatCount = 1
        rec_up.Event.KeyEvent.wVirtualKeyCode = 0
        rec_up.Event.KeyEvent.wVirtualScanCode = 0
        rec_up.Event.KeyEvent.uChar.UnicodeChar = char
        rec_up.Event.KeyEvent.dwControlKeyState = 0
        records.append(rec_up)

    if not records:
        return

    n_records = len(records)
    lpBuffer = (INPUT_RECORD * n_records)(*records)
    lpNumberOfEventsWritten = wintypes.DWORD(0)

    success = kernel32.WriteConsoleInputW(
        hStdIn,
        lpBuffer,
        n_records,
        ctypes.byref(lpNumberOfEventsWritten)
    )
    
    if not success:
        # Silently ignore failures to inject
        pass

def main():
    # Check for config help
    if "--set-config" in sys.argv and ("-h" in sys.argv or "--help" in sys.argv):
        print_config_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="clitr: CLI Translate - AI command helper")
    parser.add_argument("query", type=str, nargs='?', help="The natural language description of the command you need.")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy the result to clipboard.")
    parser.add_argument("--set-config", action="store_true", help="Update configuration values (e.g., -local_endpoint=... -model=...).")
    
    args, unknown = parser.parse_known_args()
    
    if args.set_config:
        config = load_config()
        updated = False
        for arg in unknown:
            if arg.startswith("-"):
                clean_arg = arg.lstrip("-")
                if "=" in clean_arg:
                    key, val = clean_arg.split("=", 1)
                    config[key] = val
                    print(f"Updated configuration: {key} = {val}")
                    updated = True
                else:
                    print(f"Warning: Argument '{arg}' does not match expected format 'key=value'. Ignoring.", file=sys.stderr)
            else:
                print(f"Warning: Ignoring invalid argument '{arg}'. Expected -key=value.", file=sys.stderr)
        
        if updated:
            save_config(config)
        else:
            print("No configuration changes detected. Use format: clitr --set-config -key=value")
        return

    if not args.query:
        parser.print_help()
        sys.exit(1)
    
    query = args.query
    os_info = get_os_info()
    shell_info = get_shell_info()
    
    config = load_config()
    
    # Determine model and base_url
    api_key = os.environ.get("OPENAI_API_KEY")
    local_endpoint = config.get("local_endpoint")
    
    model = "gpt-4o-mini" # Default for OpenAI
    api_base = None
    
    if api_key:
        # Use OpenAI
        pass # litellm handles this default if OPENAI_API_KEY is set
    elif local_endpoint:
        # Use local endpoint
        api_base = local_endpoint
        model = config.get("model", "openai/qwen3-30b-a3b") # User can override model name if needed for local
        api_key = "sk-xxxx" # Dummy key often needed for local servers
    else:
        print("Error: No OPENAI_API_KEY found in environment and no 'local_endpoint' specified in ~/.clitr_config.json.", file=sys.stderr)
        sys.exit(1)
        
    # Load history
    try:
        history_size = int(config.get("command_history", 3))
    except ValueError:
        history_size = 3
        
    history_lines = get_recent_history(history_size)
    history_context = ""
    if history_lines:
        history_context = "Recent command history:\n" + "\n".join(history_lines) + "\n\n"
        
    system_prompt = (
        f"You are a command line helper. "
        f"The user needs a command for the following OS: {os_info} "
        f"running in shell: {shell_info}. "
        f"{history_context}"
        f"Output ONLY the command, no markdown (no backticks), no explanations. "
        f"If multiple commands are needed, chain them appropriately for the shell."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]
    
    try:
        # litellm configuration
        kwargs = {
            "model": model,
            "messages": messages,
        }
        if api_base:
            kwargs["api_base"] = api_base
        if api_key and not os.environ.get("OPENAI_API_KEY"):
             kwargs["api_key"] = api_key

        response = litellm.completion(**kwargs)
        
        command = response.choices[0].message.content.strip()
        
        # Strip potential markdown code blocks
        if command.startswith("```") and command.endswith("```"):
            lines = command.splitlines()
            if len(lines) >= 2:
                command = "\n".join(lines[1:-1])
            else:
                command = command.strip("`")
        elif command.startswith("`") and command.endswith("`"):
             command = command.strip("`")
             
        print(command)
        
        # Inject into console input (Windows only)
        inject_command_to_console(command)
        
        if not args.no_copy:
            try:
                pyperclip.copy(command)
                print("(Copied to clipboard)", file=sys.stderr)
            except Exception as e:
                print(f"(Failed to copy to clipboard: {e})", file=sys.stderr)
                
    except Exception as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
