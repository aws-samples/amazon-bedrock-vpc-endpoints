import boto3
import datetime
import json
import pytz
import encryption as en
import base64encode as enc
import creds
import sys
import logging
from botocore.exceptions import ClientError
import manageConfig as mc

# Set up logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
file_handler = logging.FileHandler('invoke.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Function to create and return a Bedrock client
# Args:
#   b_endpoint_url: The endpoint URL for the Bedrock service
# Returns:
#   The Bedrock client object
def get_bedrock_client(b_endpoint_url):
    try:
        # Fetch the region from the configuration and create a Bedrock client
        bedrock = boto3.client('bedrock', mc.getValue('default', 'Region'), endpoint_url=b_endpoint_url)
        return bedrock
    except ClientError as error:
        logger.error(f"Failed to create Bedrock client: {error}")
        print(f"Failed to create Bedrock client: {error}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error when creating Bedrock client: {e}")
        print(f"Unexpected error when creating Bedrock client: {e}")
        sys.exit(0)

# Function to create and return a Bedrock runtime client based on the configured credentials method
# Args:
#   b_endpoint_url: The endpoint URL for the Bedrock runtime service
# Returns:
#   The Bedrock runtime client object
def get_bedrock_runtime_client(b_endpoint_url):
    try:
        # Log the method of credential retrieval as configured
        logger.info(f"GetCredentialsFrom value is {mc.getValue('default', 'GetCredentialsFrom')}")
        print(f"GetCredentialsFrom value is {mc.getValue('default', 'GetCredentialsFrom')}")

        # Option 1: Fetch Bedrock runtime client via cross-account role assumption
        if mc.getValue('default', 'GetCredentialsFrom') == str(1):
            try:
                # Decrypt the AssumeRoleARN and retrieve credentials by assuming the role
                decoded = enc.decode_base64_to_string(mc.getValue('default', 'AssumeRoleARN'))
                assume_role_arn = en.decrypt(mc.getValue('default', 'SecretKeyFernet').encode(), decoded)
                credentials = creds.getCredentialsForRole(assume_role_arn, "MyBedrockClient")
                
                # Create a Bedrock runtime client using the assumed role credentials
                bedrock = boto3.client('bedrock-runtime', mc.getValue('default', 'Region'), endpoint_url=b_endpoint_url, 
                                       aws_access_key_id=credentials["AccessKeyId"],
                                       aws_secret_access_key=credentials["SecretAccessKey"],
                                       aws_session_token=credentials["SessionToken"])
            except ClientError as error:
                logger.error(f"Unable to assume role {assume_role_arn}. Ensure APIKey and APISecret are correct and have permission to assume the role. Error: {error}")
                print(f"Unable to assume role {assume_role_arn}. Ensure APIKey and APISecret are correct and have permission to assume the role. Error: {error}")
                sys.exit(0)

        # Option 2: Fetch Bedrock runtime client using IAM API Key and Secret
        elif mc.getValue('default', 'GetCredentialsFrom') == str(2):
            try:
                # Decrypt the API keys and assume the specified role using those credentials
                decoded = enc.decode_base64_to_string(mc.getValue('default', 'AssumeRoleARN'))
                assume_role_arn = en.decrypt(mc.getValue('default', 'SecretKeyFernet').encode(), decoded)
                decoded = enc.decode_base64_to_string(mc.getValue('default', 'AccessKey'))
                api_key = en.decrypt(mc.getValue('default', 'SecretKeyFernet').encode(), decoded)
                decoded = enc.decode_base64_to_string(mc.getValue('default', 'SecretKey'))
                api_secret = en.decrypt(mc.getValue('default', 'SecretKeyFernet').encode(), decoded)
                
                logger.info(f"api_key is {api_key}")
                logger.info(f"api_secret is {api_secret}")
                logger.info(f"assume_role_arn is {assume_role_arn}")
                print(api_key, api_secret, assume_role_arn)
                
                # Retrieve credentials by assuming the specified role with the API keys
                credentials = creds.getCredentialsfromAPIKeybyAssumingRole(api_key, api_secret, assume_role_arn)
                bedrock = boto3.client('bedrock-runtime', mc.getValue('default', 'Region'), endpoint_url=b_endpoint_url, 
                                       aws_access_key_id=credentials["AccessKeyId"],
                                       aws_secret_access_key=credentials["SecretAccessKey"],
                                       aws_session_token=credentials["SessionToken"])
            except ClientError as error:
                logger.error(f"Unable to assume role {assume_role_arn}. Ensure permission to assume the role. Error: {error}")
                print(f"Unable to assume role {assume_role_arn}. Ensure permission to assume the role. Error: {error}")
                sys.exit(0)

        # Default: Fetch Bedrock runtime client based on EC2 role permissions (no additional credentials required)
        else:
            bedrock = boto3.client('bedrock-runtime', mc.getValue('default', 'Region'), endpoint_url=b_endpoint_url)
    
        return bedrock

    except ClientError as error:
        logger.error(f"Failed to create Bedrock runtime client: {error}")
        print(f"Failed to create Bedrock runtime client: {error}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error when creating Bedrock runtime client: {e}")
        print(f"Unexpected error when creating Bedrock runtime client: {e}")
        sys.exit(0)
