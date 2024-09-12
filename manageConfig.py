import encryption as en
import base64encode as enc
import logging
import configparser
from logging_setup import setup_logging

# Set up logging using the imported function
setup_logging(log_level=logging.INFO)

# Initialize the config object at the module level to hold the configuration
_config = None

# Function to initialize the configuration by reading the config file
# Args:
#   file_path: The path to the configuration file. Defaults to 'config.properties'.
# Returns:
#   True if the initialization is successful
def _initialize_config(file_path='config.properties'):
    global _config
    if _config is None:
        try:
            # Create a ConfigParser object to read the configuration file
            config = configparser.ConfigParser()
            config.optionxform = str  # Disable case folding for option names (case-sensitive keys)
            
            # Read the configuration file
            config.read(file_path)
            _config = config
            logging.info(f"Configuration initialized from {file_path}")
        except FileNotFoundError as e:
            logging.error(f"Configuration file not found: {file_path}")
            print(f"Configuration file not found: {file_path}")
            raise e  # Re-raise the exception after logging
        except Exception as e:
            logging.error(f"Error initializing configuration: {e}")
            print(f"Error initializing configuration: {e}")
            raise e  # Re-raise the exception after logging
    return True

# Function to reinitialize the configuration (force reload)
# Args:
#   file_path: The path to the configuration file. Defaults to 'config.properties'.
# Returns:
#   True if the reinitialization is successful
def _reinitialize_config(file_path='config.properties'):
    global _config
    try:
        # Create a new ConfigParser object to reload the configuration file
        config = configparser.ConfigParser()
        config.optionxform = str  # Disable case folding for option names (case-sensitive keys)

        # Read the configuration file
        config.read(file_path)
        _config = config
        logging.info(f"Configuration reinitialized from {file_path}")
    except FileNotFoundError as e:
        logging.error(f"Configuration file not found: {file_path}")
        print(f"Configuration file not found: {file_path}")
        raise e  # Re-raise the exception after logging
    except Exception as e:
        logging.error(f"Error reinitializing configuration: {e}")
        print(f"Error reinitializing configuration: {e}")
        raise e  # Re-raise the exception after logging
    return True

# Function to retrieve a value from the configuration
# Args:
#   section: The section in the configuration file where the key is located
#   key: The key whose value needs to be retrieved
# Returns:
#   The value corresponding to the provided section and key
def getValue(section, key):
    try:
        _initialize_config()  # Ensure the config is initialized
        value = _config[section].get(key)
        logging.info(f"Retrieved value for {key} in section {section}: {value}")
        return value
    except KeyError as e:
        logging.error(f"KeyError: {e} - Section: '{section}', Key: '{key}' not found.")
        print(f"Error: Section '{section}' or Key '{key}' not found in the config.")
        raise e  # Re-raise the exception after logging
    except Exception as e:
        logging.error(f"Failed to get value from config: {e}")
        print(f"Failed to get value from config: {e}")
        raise e  # Re-raise the exception after logging

# Function to set a value in the configuration
# Args:
#   section: The section in the configuration file where the key is located
#   key: The key whose value needs to be set
#   value: The value to be set for the given key
# Returns:
#   True if the value is successfully set
def setValue(section, key, value):
    try:
        _initialize_config()  # Ensure the config is initialized
        _config.set(section, key, value)
        logging.info(f"Set value for {key} in section {section} to {value}")
        return True
    except Exception as e:
        logging.error(f"Failed to set value in config: {e}")
        print(f"Failed to set value in config: {e}")
        raise e  # Re-raise the exception after logging

# Function to print all values in the configuration file
def print_all_config_values():
    print("=====================")
    try:
        if _initialize_config():  # Ensure the config is initialized
            for section in _config.sections():
                print(f"Section: {section}")
                for key, value in _config.items(section):
                    print(f"  {key} = {value}")
    except Exception as e:
        logging.error(f"Error printing config values: {e}")
        print(f"Error printing config values: {e}")

# Function to write the configuration to a new file
# Args:
#   new_config_file_location: The path where the new configuration file should be saved
# Returns:
#   True if the configuration is successfully written to the file
def writeConfig(new_config_file_location):
    try:
        # Ensure config is initialized
        if _initialize_config():
            # Write the current configuration to the specified file location
            with open(new_config_file_location, "w") as configfile:
                _config.write(configfile)
            logging.info(f'Configuration file saved at {new_config_file_location}')
            print(f'Configuration file saved at {new_config_file_location}')
            return True
    except Exception as e:
        logging.error(f"Failed to write config to {new_config_file_location}: {e}")
        print(f"Failed to write config to {new_config_file_location}: {e}")
        raise e  # Re-raise the exception after logging

# Function to retrieve the list of models from the configuration
# Returns:
#   A list of models if available, otherwise an empty list
def get_models():
    try:
        if _initialize_config():  # Ensure the config is initialized
            models = _config['models'].items()
            logging.info("Models retrieved from config")
            return models
    except KeyError as e:
        logging.error(f"KeyError: 'models' section not found. {e}")
        print(f"Error: 'models' section not found in the config.")
        raise e  # Re-raise the exception after logging
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        print(f"Error fetching models: {e}")
        raise e  # Re-raise the exception after logging
    return []
