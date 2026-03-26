"""
Earthquake Rescue Coordination System - Entry Point

TUBITAK-supported research project for post-disaster rescue coordination.
Provides REST API backend and IoT sensor integration via MQTT.
"""

import uvicorn
import yaml
import logging
from pathlib import Path


def load_config() -> dict:
    """Load application configuration from YAML file."""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_logging(config: dict) -> None:
    """Configure application logging."""
    log_config = config.get("logging", {})
    log_file = log_config.get("file", "logs/rescue_api.log")

    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO")),
        format=log_config.get(
            "format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def main():
    """Start the Earthquake Rescue Coordination API server."""
    config = load_config()
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info("Starting Earthquake Rescue Coordination System")

    server_config = config.get("server", {})

    uvicorn.run(
        "src.api.main:app",
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8000),
        reload=server_config.get("debug", False),
        workers=1 if server_config.get("debug", False) else server_config.get("workers", 4),
    )


if __name__ == "__main__":
    main()
