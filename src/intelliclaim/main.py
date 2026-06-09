"""Application entry point."""

import uvicorn

from intelliclaim.api.app import create_app
from intelliclaim.infrastructure.config.settings import get_settings

app = create_app()


def run() -> None:
    """Run the application with uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "intelliclaim.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run()
