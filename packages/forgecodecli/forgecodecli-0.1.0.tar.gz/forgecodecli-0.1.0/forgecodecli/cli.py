import typer
from forgecodecli.agent import think
from forgecodecli.tools import read_file, list_files, write_file, create_dir
import getpass

from forgecodecli.secrets import save_api_key, delete_api_key
from forgecodecli.config import save_config, config_exists, delete_config

app = typer.Typer()

import os

def show_logo():
    cwd = os.getcwd()

    print(f"""
███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

ForgeCode CLI • Agentic File Assistant
Safe • Deterministic • File-aware

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Mode : Code Agent
Model      : Gemini 2.5 Flash
Workspace  : {cwd}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type natural language commands to manage files.
(type 'quit' or Ctrl+C to exit)\n
""")

@app.command()
def init() :
    """
    Initialize ForgeCode CLI configuration
    """
    if config_exists():
        typer.echo("ForgeCodeCLI is already set up.")
        typer.echo("Use `forgecodecli reset` to reconfigure.")
        return
    
    typer.echo("Welcome to ForgeCodeCLI ✨")
    typer.echo("Let's set things up.\n")

    typer.echo("Select LLM provider:")
    typer.echo("  1) Gemini")
    typer.echo("  2) Exit")
    
    choice = typer.prompt(">")
    if choice != "1":
        typer.echo("Exiting setup.")
        return
    
    api_key = getpass.getpass("Enter your Gemini API Key: ")
    if not api_key.strip():
        typer.echo("API Key cannot be empty. Exiting setup.")
        return
    save_api_key(api_key)
    
    config = {
        "provider": "gemini",
        "model": "gemini-2.5-flash"
    }
    
    save_config(config)
    
    typer.echo("\n✓ API key saved securely")
    typer.echo("✓ Provider set to Gemini")
    typer.echo("✓ Model set to gemini-2.5-flash")
    typer.echo("\nSetup complete.")
    typer.echo("Run `forgecodecli` to start.")
    
@app.command()
def reset():
    """
    Reset ForgeCodeCLI configuration and API key
    """
    if not config_exists():
        typer.echo("ForgeCodeCLI is not set up.")
        return

    typer.echo(
        "This will remove your ForgeCodeCLI configuration and API key."
    )
    confirm = typer.prompt("Are you sure? (y/N)", default="n")

    if confirm.lower() != "y":
        typer.echo("Reset cancelled.")
        return

    try:
        delete_api_key()
        typer.echo("✓ API key removed")
    except Exception:
        typer.echo("⚠️ No API key found")

    delete_config()
    typer.echo("✓ Configuration deleted")

    typer.echo("\nForgeCodeCLI has been reset.")
    typer.echo("Run `forgecodecli init` to set it up again.")


def describe_action(action: str, args: dict):
    if action == "read_file":
        print(f"📂 Reading file: {args.get('path')}")
    elif action == "list_files":
        print(f"📄 Listing files in: {args.get('path', '.')}")
    elif action == "create_dir":
        print(f"📁 Creating directory: {args.get('path')}")
    elif action == "write_file":
        print(f"✍️ Writing file: {args.get('path')}")


@app.callback(invoke_without_command=True)
def run(ctx: typer.Context):
    """
    ForgeCode CLI — agent with actions
    """
    if ctx.invoked_subcommand is not None:
        return

    if not config_exists():
        typer.echo("ForgeCodeCLI is not set up yet.")
        typer.echo("Run `forgecodecli init` first.")
        return

    # ===============================
    # INTERACTIVE MODE
    # ===============================
    show_logo()
    messages = []

    try:
        while True:
                user_input = input("forgecode (agent) >  ").strip()

                if user_input.lower() in ("quit", "exit"):
                    print("Bye")
                    break

                messages.append({"role": "user", "content": user_input})
                # print("🤔 Planning actions...")
                answered = False

                for _ in range(5):
                    decision = think(messages)
                    action = decision.get("action")
                    args = decision.get("args", {})

                    if action == "read_file":
                        describe_action(action, args)
                        result = read_file(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})
                    
                    elif action == "list_files":
                        describe_action(action, args)
                        result = list_files(args.get("path", "."))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "create_dir":
                        describe_action(action, args)
                        result = create_dir(args.get("path"))
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "write_file":
                        describe_action(action, args)
                        result = write_file(
                            args.get("path"),
                            args.get("content")
                        )
                        print(result)
                        messages.append({"role": "assistant", "content": result})

                    elif action == "answer":
                        print(args.get("text", ""))
                        answered = True
                        # Keep only last 10 messages to avoid context overflow
                        if len(messages) > 20:
                            messages = messages[-20:]
                        break

                if not answered:
                    print("⚠️ I couldn't complete this request.")
                    print("✅ Done")
                    # Keep only last 10 messages to avoid context overflow
                    if len(messages) > 20:
                        messages = messages[-20:]

    except KeyboardInterrupt:
            print("\nBye")

    return



def main():
    app()


if __name__ == "__main__":
    main()
