"""Configuration utilities for the Prudentia CLI."""

import configparser
import os

CONFIG_DIR = os.path.expanduser("~/.config/prudentia")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def get_config():
    """Get the configuration from the config file."""
    ensure_config_dir()

    config = configparser.ConfigParser()

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)

    return config


def save_config(config):
    """Save the configuration to the config file."""
    ensure_config_dir()

    with open(CONFIG_FILE, "w") as f:
        config.write(f)
