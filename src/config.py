
class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            config = {}
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
        return config
    
    def get(self, key, default=None):
        return self.config.get(key, default)
