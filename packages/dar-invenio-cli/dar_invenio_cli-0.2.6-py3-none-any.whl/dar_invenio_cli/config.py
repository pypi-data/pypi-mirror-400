import json
import click
from pathlib import Path

CONFIG_FILE = Path(".dar-invenio-cli.json")


class Config:
    def __init__(self, api_token=None, base_api_url=None, model=None, community=None):
        self.api_token = api_token
        self.base_api_url = base_api_url
        self.model = model
        self.community = community
        self.base_model_url = f"{self.base_api_url}/{self.model}" if self.base_api_url and self.model else None
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        } if self.api_token else None

    def to_dict(self):
        return {
            "api_token": self.api_token,
            "base_api_url": self.base_api_url,
            "model": self.model,
            "community": self.community
        }


def set_config(config):
    """Sets the configuration."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.to_dict(), f, indent=4)
    return config


def get_config():
    """Gets the configuration."""
    if not CONFIG_FILE.is_file():
        click.echo("Configuration file not found. Please run config 'init' first.")
        return None
    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)
        config = Config(**config_data)
        if not all(vars(config).values()):
            click.echo("Configuration is invalid. Please run config 'init' first.")
            return None
        return config
