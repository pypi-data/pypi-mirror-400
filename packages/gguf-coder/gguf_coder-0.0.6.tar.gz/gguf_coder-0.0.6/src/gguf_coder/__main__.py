
import json, os

def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter y or n.")

def setup_config():
    print("=== Create coder.config.json ===\n")

    providers = []

    while True:
        print("Add a provider:")

        name = input("  Enter provider name (e.g. lmstudio, ollama, etc.):  ").strip()
        model = input("  Model naem (e.g. openai/gpt-oss-20b, gpt-oss:20b, etc.): ").strip()
        base_url = input("  Enter baseUrl (e.g. http://localhost:1234/v1 or http://localhost:11434/v1 etc.): ").strip()

        provider = {
            "name": name,
            "models": [model],
            "baseUrl": base_url
        }

        providers.append(provider)

        print()
        if not ask_yes_no("Add another provider?"):
            break
        print()

    config = {
        "coder": {
            "providers": providers
        }
    }

    output_file = "coder.config.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"\n✔ coder.config.json created at:")
    print(f"  {os.path.abspath(output_file)}")

setup_config()
