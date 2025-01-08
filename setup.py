import argparse
import os
import platform
import secrets
import shutil
import subprocess
from pathlib import Path


# ANSI color codes
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    NC = "\033[0m"


def log_info(message):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")


def log_warning(message):
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def log_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


SHARED_API_KEY = None
EXTERNAL_OLLAMA_URL = None


def check_external_ollama_requirement() -> bool:
    system = platform.system()
    release = platform.release()

    log_info(f"Platform: {system}/{release}")

    if system in ["Darwin", "Linux"]:
        is_wsl = "microsoft" in release.lower()
        if is_wsl:
            return False

        log_info(f"Using external Ollama server at {EXTERNAL_OLLAMA_URL}")
        log_warning("--------------------")
        log_warning(
            "Note: Currently GPU support in Docker Desktop is only available on Windows with the WSL2 backend."
        )
        log_warning(
            "Please ensure you have Ollama installed and running at the specified URL."
        )
        log_warning("You must set up Ollama manually before using Chipper.")
        log_warning("Download and installation instructions: https://ollama.com")
        log_warning("--------------------")
        return True
    return False


def generate_api_key():
    global SHARED_API_KEY
    if SHARED_API_KEY is None:
        SHARED_API_KEY = secrets.token_hex(32)
    return SHARED_API_KEY


def detect_gpu_profile():
    system = platform.system()

    # Check macOS
    if system == "Darwin":
        log_info("Detected macOS system")
        return "macos"

    # Check NVIDIA GPU
    try:
        subprocess.run(["nvidia-smi"], capture_output=True, check=True)
        log_info("Detected NVIDIA GPU")
        return "nvidia"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check AMD GPU
    if system == "Linux":
        if Path("/dev/dri").exists() and Path("/dev/kfd").exists():
            log_info("Detected AMD GPU with ROCm support")
            return "amd"
    elif system == "Windows":
        try:
            wmic_output = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
            ).stdout
            if "AMD" in wmic_output or "Radeon" in wmic_output:
                log_info("Detected AMD GPU")
                return "amd"
        except Exception:
            pass

    log_warning("No GPU detected or unsupported GPU configuration")
    return "cpu"


def has_example_api_key_set(env_file):
    try:
        with open(env_file, "r") as file:
            content = file.read()
        return "API_KEY=EXAMPLE_API_KEY" in content
    except Exception as e:
        log_error(f"Failed to read {env_file}: {str(e)}")
        return False


def has_ollama_key(env_file):
    try:
        with open(env_file, "r") as file:
            content = file.read()
        return "OLLAMA_URL=http://host.docker.internal:21240" in content
    except Exception as e:
        log_error(f"Failed to read {env_file}: {str(e)}")
        return False


def update_env_file(env_file, updates):
    try:
        with open(env_file, "r") as file:
            content = file.read()

        for key, value in updates.items():
            if f"{key}=" in content:
                if key == "API_KEY":
                    content = content.replace(
                        f"{key}=EXAMPLE_API_KEY", f"{key}={value}"
                    )
                elif key == "OLLAMA_URL":
                    lines = content.split("\n")
                    ollama_found = False
                    for i, line in enumerate(lines):
                        if line.startswith("OLLAMA_URL="):
                            lines[i] = f"OLLAMA_URL={value}"
                            ollama_found = True
                            break
                    if not ollama_found:
                        lines.append(f"OLLAMA_URL={value}")
                    content = "\n".join(lines)
                else:
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if line.startswith(f"{key}="):
                            lines[i] = f"{key}={value}"
                    content = "\n".join(lines)
            else:
                content += f"\n{key}={value}"

        with open(env_file, "w") as file:
            file.write(content)

        log_info(f"Updated {env_file}")
    except Exception as e:
        log_error(f"Failed to update {env_file}: {str(e)}")


def create_docker_env(profile):
    docker_dir = Path("docker")
    if not docker_dir.exists():
        docker_dir.mkdir(exist_ok=True)
        log_info("Created docker directory")

    docker_env = docker_dir / ".env"

    env_content = f"""# Automatically generated Docker environment file
COMPOSE_PROFILES={profile}"""
    try:
        with open(docker_env, "w") as f:
            f.write(env_content)
        log_info(f"Created {docker_env} with profile configuration")
    except Exception as e:
        log_error(f"Failed to create {docker_env}: {str(e)}")


def clean_env_files():
    global SHARED_API_KEY, EXTERNAL_OLLAMA_URL
    SHARED_API_KEY = None
    EXTERNAL_OLLAMA_URL = None

    files_to_remove = [".env", ".ragignore", ".systemprompt"]
    docker_env = Path("docker/.env")
    if docker_env.exists():
        try:
            docker_env.unlink()
            log_info(f"Removed {docker_env}")
        except Exception as e:
            log_error(f"Failed to remove {docker_env}: {str(e)}")

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

            if example_pattern == ".env.example" or has_example_api_key_set(
                str(actual_file)
            ):
                files_needing_update.append(actual_file)

    return found_files, files_needing_update


def main():
    parser = argparse.ArgumentParser(description="Environment file setup utility")
    parser.add_argument(
        "--clean", action="store_true", help="Remove all generated files"
    )
    parser.add_argument(
        "--docker-only", action="store_true", help="Only create Docker environment file"
    )
    parser.add_argument(
        "--ollama-url",
        help="URL for external Ollama server (default: http://host.docker.internal:11434/)",
    )
    args = parser.parse_args()

    if args.clean:
        clean_env_files()
        return 0

    # Set Ollama URL from environment variable or command line argument
    global EXTERNAL_OLLAMA_URL
    EXTERNAL_OLLAMA_URL = (
        args.ollama_url
        or os.environ.get("OLLAMA_URL")
        or "http://host.docker.internal:11434/"
    )

    # Generate API key
    generate_api_key()

    # Detect GPU profile
    gpu_profile = detect_gpu_profile()

    # Create Docker environment file
    create_docker_env(gpu_profile)

    # Check Ollama configuration
    use_external_ollama = check_external_ollama_requirement()

    if args.docker_only:
        return 0

    log_info("Starting to search for example files...")

    found_env_files, files_needing_update = copy_example_files()

    if not found_env_files:
        log_error("No example .env files found!")
        return 1

    # Configure environment
    for env_file in files_needing_update:
        if str(env_file).endswith(".env"):
            updates = {}
            if has_example_api_key_set(str(env_file)):
                updates["API_KEY"] = SHARED_API_KEY
            if has_ollama_key(str(env_file)) and use_external_ollama:
                updates["OLLAMA_URL"] = EXTERNAL_OLLAMA_URL
            if updates:
                update_env_file(str(env_file), updates)

    log_info("Setup completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())
