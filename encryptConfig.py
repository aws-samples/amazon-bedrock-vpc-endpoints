import encryption as en
import base64encode as enc
import logging
import manageConfig as mc
import sys
from logging_setup import setup_logging

# Set up logging using the imported function
setup_logging(log_level=logging.INFO)

# Prompt the user to provide the path to the unencrypted configuration file
config_file_location = input('Please provide configuration file path including its name:  ')

# Prompt the user to provide the absolute path where the new encrypted configuration file should be saved
new_config_file_location = input('Please provide absolute path to store new configuration file path including its name:  ')

# Use a default configuration file name if the user doesn't provide one
if config_file_location == '':
    config_file_location = "config.properties"

try:
    # Initialize the configuration by reading the unencrypted config file
    mc._initialize_config(config_file_location)

    # Generate a new encryption key
    key = en.generateKey()
    logging.info("Generated encryption key")

    # Encrypt the 'SecretKeyFernet' value and store it back in the configuration
    mc.setValue("default", 'SecretKeyFernet', key.decode())
    apikey = mc.getValue("default", 'SecretKeyFernet')
    encrypted = en.encrypt(key, apikey)
    mc.setValue('default', 'AccessKey', enc.encode_string_to_base64(encrypted))
    logging.info("Encrypted and stored AccessKey")

    # Encrypt the 'SecretKey' value and store it back in the configuration
    apisecret = mc.getValue("default", 'SecretKey')
    encrypted = en.encrypt(key, apisecret)
    mc.setValue('default', 'SecretKey', enc.encode_string_to_base64(encrypted))
    logging.info("Encrypted and stored SecretKey")

    # Encrypt the 'AssumeRoleARN' value and store it back in the configuration
    role = mc.getValue("default", 'AssumeRoleARN')
    encrypted = en.encrypt(key, role)
    mc.setValue('default', 'AssumeRoleARN', enc.encode_string_to_base64(encrypted))
    logging.info("Encrypted and stored AssumeRoleARN")

    # Encrypt the 'VPCEndpointURL' value and store it back in the configuration
    vpce = mc.getValue("default", 'VPCEndpointURL')
    encrypted = en.encrypt(key, vpce)
    mc.setValue('default', 'VPCEndpointURL', enc.encode_string_to_base64(encrypted))
    logging.info("Encrypted and stored VPCEndpointURL")

    # Print all configuration values to verify encryption
    mc.print_all_config_values()

    # Write the encrypted configuration to a new file
    mc.writeConfig(new_config_file_location)
    logging.info(f"Encrypted configuration file saved at {new_config_file_location}")

except FileNotFoundError as e:
    logging.error(f"Configuration file not found: {e}")
    print(f"Configuration file not found: {e}")
    sys.exit(1)

except Exception as e:
    logging.error(f"Unexpected error occurred: {e}")
    print(f"Unexpected error occurred: {e}")
    sys.exit(1)
