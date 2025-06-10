import json
from pydantic import BaseModel

CONFIG_PATH = "config.json"  # change with default env variable from docker


class GeneralValidator(BaseModel):
    """
    General configuration validator.
    """

    version: str
    data_path: str
    data_filename: str


class Configuration(BaseModel):
    """
    Main configuration class that includes general settings and specific configurations.
    """

    general: GeneralValidator


# Load the JSON data from the file into a dictionary
with open(CONFIG_PATH, "r") as file:
    config_dict = json.load(file)

# Parse the dictionary into a Configuration object
config = Configuration(**config_dict)
