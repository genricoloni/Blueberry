"""
Module to manage configuration settings from a file.
"""

class ConfigManager:
    """
    A class to manage configuration settings from a file.

    This class allows for loading, retrieving, and managing configuration
    settings stored in a key-value format.

    Attributes:
        config_file (str): The path to the configuration file.
        config (dict): A dictionary containing the loaded configuration settings.
    """

    def __init__(self, config_file):
        """
        Initialize a new instance of the ConfigManager class.

        This method loads the configuration from the specified file and stores 
        it in the `config` attribute.

        Parameters:
            config_file (str): The path to the configuration file.
        """
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """
        Load configuration settings from the file.

        This method reads the configuration file, assuming it contains key-value pairs
        separated by an '=' sign on each line.

        Returns:
            dict: A dictionary containing the loaded configuration settings.
        """
        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = {}
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
        return config

    def get(self, key, default=None):
        """
        Retrieve the value associated with a specified key from the configuration.

        If the key is not found in the configuration, the method returns a default value.

        Parameters:
            key (str): The key whose value is to be retrieved.
            default (optional): The value to return if the key is not found. Defaults to None.

        Returns:
            str: The value associated with the key if found, or the default value if not.
        """
        return self.config.get(key, default)
