import argparse
import secrets
import shutil
from pathlib import Path


# ANSI color codes
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    NC = "\033[0m"  # No Color


def log_info(message):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def log_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def generate_api_key():
    return secrets.token_hex(32)


def needs_api_key_update(env_file):
    try:
        with open(env_file, "r") as file:
            content = file.read()
        return "API_KEY=EXAMPLE_API_KEY" in content
    except Exception as e:
        log_error(f"Failed to read {env_file}: {str(e)}")
        return False


def update_api_key(env_file, api_key):
    try:
        with open(env_file, "r") as file:
            content = file.read()

        content = content.replace("API_KEY=EXAMPLE_API_KEY", f"API_KEY={api_key}")

        with open(env_file, "w") as file:
            file.write(content)

        log_info(f"Updated API key in {env_file}")
    except Exception as e:
        log_error(f"Failed to update {env_file}: {str(e)}")


def clean_env_files():
    files_to_remove = [".env", ".ragignore", ".systemprompt"]
    count = 0
    for pattern in files_to_remove:
        for file in Path(".").rglob(pattern):
            try:
                file.unlink()
                count += 1
                log_info(f"Removed {file}")
            except Exception as e:
                log_error(f"Failed to remove {file}: {str(e)}")

    if count > 0:
        log_info(f"Removed {count} file{'s' if count > 1 else ''}")
    else:
        log_info("No files found to remove")


def copy_example_files():
    example_mappings = {
        ".env.example": ".env",
        ".ragignore.example": ".ragignore",
        ".systemprompt.example": ".systemprompt",
    }

    found_files = []
    files_needing_update = []

    for example_pattern in example_mappings.keys():
        for example_file in Path(".").rglob(example_pattern):
            actual_file = example_file.with_name(example_mappings[example_pattern])
            found_files.append(actual_file)

            if not actual_file.exists():
                shutil.copy(example_file, actual_file)
                log_info(f"Created {actual_file} from {example_file}")

            if example_pattern == ".env.example" and needs_api_key_update(
                str(actual_file)
            ):
                files_needing_update.append(actual_file)

    return found_files, files_needing_update


def main():
    parser = argparse.ArgumentParser(description="Environment file setup utility")
    parser.add_argument(
        "--clean", action="store_true", help="Remove all generated files"
    )
    args = parser.parse_args()

    if args.clean:
        clean_env_files()
        return 0

    log_info("Starting to search for example files...")

    found_files, files_needing_update = copy_example_files()

    if not found_files:
        log_error("No example files found!")
        return 1

    if not files_needing_update:
        log_info("No API keys need updating.")
        return 0

    log_info("Generating new API key...")
    new_api_key = generate_api_key()

    log_info("Updating API keys in .env files...")
    for env_file in files_needing_update:
        update_api_key(str(env_file), new_api_key)

    log_info("Setup completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
