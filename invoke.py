import encryption as en
import base64encode as enc
import creds
import json
import boto3
import datetime
import bedrockclient as bd
import pytz
import logging
import sys
import botocore
from myutils import create_complete_prompt, pretty_print, read_file_contents
import manageConfig as mc
from logging_setup import setup_logging

# Set up logging using the imported function
setup_logging(log_level=logging.DEBUG)

# Function to read the contents of a file
# Args: filename: The path to the file.
# Returns: The contents of the file as a string.
def read_file_contents(filename):
    try:
        # Open and read the file
        with open(filename, 'r') as f:
            file_contents = f.read()
        return file_contents
    except Exception as e:
        logging.error(f"Error reading file {filename}: {e}")
        print(f"Error reading file {filename}: {e}")
        sys.exit(0)

# Function to invoke the model with the provided model_id and endpoint URL
# Args: 
#   b_endpoint_url: The endpoint URL for the Bedrock service
#   model_id: The ID of the model to invoke
def invokeModel(b_endpoint_url, model_id):
    try:
        # Fetch the Bedrock runtime client
        bedrock_runtime = bd.get_bedrock_runtime_client(b_endpoint_url)

        message_list = []

        # Read the system prompt from a file
        system_prompt = read_file_contents("system.txt")

        print("=============================")
        print("Complete Prompt Context \n\n")
        print(system_prompt)

        # Create the summary message to be sent to the model
        summary_message = {
            "role": "user",
            "content": []
        }

        # Check if model_id contains "titan" or "mistral" (case insensitive)
        # Titan and Mistral models do not support system prompts with the exception of Mistral-Large-2
        if "titan" in model_id.lower() or "mistral" in model_id.lower():
            # Append system prompt content first
            summary_message["content"].append({"text": system_prompt})
            system_prompt = None  # Remove system prompt for the API call
        
        # Append the user query and prompt template to the message list
        summary_message["content"].append({"text": create_complete_prompt("prompt.txt", "user-query.txt")})
        
        # Add the summary message to the message list
        message_list.append(summary_message)

        # Call the model with or without the system prompt based on the condition
        response = bedrock_runtime.converse_stream(
            modelId=model_id,
            messages=message_list,
            system=[{"text": system_prompt}] if system_prompt else [],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0
            },
        )
        
        print("=============================")
        print("RESULT: \n")

        # Process and print the response stream
        stream = response.get('stream')
        if stream:
            for event in stream:
                if 'messageStart' in event:
                    print(f"\nRole: {event['messageStart']['role']}")

                if 'contentBlockDelta' in event:
                    print(event['contentBlockDelta']['delta']['text'], end="")

                if 'messageStop' in event:
                    print(f"\n\nStop reason: {event['messageStop']['stopReason']}")

                if 'metadata' in event:
                    metadata = event['metadata']
                    print('=====================')
                    if 'usage' in metadata:
                        print("\nToken usage\n")
                        print(f"Input tokens: {metadata['usage']['inputTokens']}")
                        print(f"Output tokens: {metadata['usage']['outputTokens']}")
                        print(f"Total tokens: {metadata['usage']['totalTokens']}")
                    if 'metrics' in event['metadata']:
                        print(f"Latency: {metadata['metrics']['latencyMs']} milliseconds")

    except botocore.exceptions.ClientError as error:
        logging.error(f"Failed to invoke model {model_id}: {error}")
        print(f"Failed to invoke model {model_id}: {error}")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Unexpected error during model invocation: {e}")
        print(f"Unexpected error during model invocation: {e}")
        sys.exit(0)

if __name__ == '__main__':
    try:
        b_endpoint_url = ''
        # Request the user to provide the path to the encrypted config file
        config_file_location = input('\n\nPlease provide configuration file path including its name (if no path is provided it will look for config.properties in the same folder as main.py):  ')

        # Default to "config.properties" if no path is provided
        if config_file_location == '':
            config_file_location = "config.properties"
        
        # Ensure the config file is not empty and valid
        if not mc._initialize_config(config_file_location):
            logging.info(f'Please make sure the provided config file path is correct and not empty, exiting ....')
            print(f'Please make sure the provided config file path is correct and not empty, exiting .... ')
            sys.exit(0)
        
        # Check if the config file contains the 'UseVPCe' key
        if not mc.getValue('default', 'UseVPCe'):
            logging.info(f'Ensure that UseVPCe exists in the config file, exiting....')
            print(f'Ensure that UseVPCe exists in the config file, exiting....')
            sys.exit(0)
        
        # Check if 'UseVPCe' is set to 'true' or 'false'
        elif mc.getValue('default', 'UseVPCe') == 'true':
            # Fetch and decrypt the VPC Endpoint URL
            decoded = enc.decode_base64_to_string(mc.getValue('default', 'VPCEndpointURL'))
            b_endpoint_url = en.decrypt(mc.getValue('default', 'SecretKeyFernet').encode(), decoded)
            logging.info(f'Bedrock VPCE is enabled. Here is the EndPoint URL - {b_endpoint_url}')
            print("\nNote:")
            print(f'Bedrock VPCE is enabled. Here is the EndPoint URL - {b_endpoint_url}')
        else:
            # If VPC Endpoint is not enabled, use the default Bedrock Service URL
            b_endpoint_url = 'https://bedrock-runtime.'+ mc.getValue('default','Region')+'.amazonaws.com'
            logging.info(f'Bedrock VPCE is not enabled. Here is the Bedrock Service URL - {b_endpoint_url}')
            print("\nNote:")
            print(f'Bedrock VPCE is not enabled. Using the Bedrock Service URL - {b_endpoint_url}')
        
        # Get available models from the configuration
        models = mc.get_models()

        # Convert the ItemsView to a list of tuples
        models_list = list(models)

        print("\nAvailable Models:", models)
        # Print available models with their index numbers
        for index, (key, value) in enumerate(models_list):
            print(f"{index}: {key}")

        # Allow the user to select a model by entering its index number
        selected_index = int(input("Select the model by entering the number: ")) 

        # Validate the selected index
        if selected_index < 0 or selected_index >= len(models_list):
            print("Invalid selection. Exiting...")
            sys.exit(0)

        print("\n\nModel Selected: "+ models_list[selected_index][1]+ "\n\n")
        # Invoking the selected model
        invokeModel(b_endpoint_url, models_list[selected_index][1])

    except Exception as e:
        logging.error(f"Unexpected error in the main block: {e}")
        print(f"Unexpected error: {e}")
        sys.exit(0)
