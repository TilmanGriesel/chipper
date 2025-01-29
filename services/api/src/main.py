import os

from api.config import APP_VERSION, BUILD_NUMBER, app, logger
from api.routes_setup import setup_all_routes


def show_welcome():
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    print("\n", flush=True)
    print(f"{PURPLE}", flush=True)
    print("        __    _                      ", flush=True)
    print("  _____/ /_  (_)___  ____  ___  _____", flush=True)
    print(" / ___/ __ \\/ / __ \\/ __ \\/ _ \\/ ___/", flush=True)
    print("/ /__/ / / / / /_/ / /_/ /  __/ /    ", flush=True)
    print("\\___/_/ /_/_/ .___/ .___/\\___/_/     ", flush=True)
    print("           /_/   /_/                 ", flush=True)
    print(f"{RESET}", flush=True)
    print(f"{CYAN}       Chipper API {APP_VERSION}.{BUILD_NUMBER}", flush=True)
    print(f"{RESET}\n", flush=True)


def create_app():
    try:
        setup_all_routes(app)
        logger.info(f"Initialized Chipper API {APP_VERSION}.{BUILD_NUMBER}")
        return app
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        raise


def get_server_config():
    return {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "debug": os.getenv("DEBUG", "False").lower() == "true",
    }


application = create_app()  # For Gunicorn

# Development server
if __name__ == "__main__":
    try:
        show_welcome()
        server_config = get_server_config()

        logger.info(
            f"Starting development server on {server_config['host']}:{server_config['port']}"
        )

        application.run(
            host=server_config["host"],
            port=server_config["port"],
            debug=server_config["debug"],
        )
    except Exception as e:
        logger.error(f"Failed to start development server: {e}", exc_info=True)
        exit(1)
