import boto3
from botocore.exceptions import ClientError
import logging
import sys

# Set up logging configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
file_handler = logging.FileHandler('invoke.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Function to assume an AWS role and obtain temporary credentials
# Args:
#   assume_role_arn: The ARN of the role to assume
#   role_session_name: A name for the session during which the role is assumed
# Returns:
#   A dictionary containing temporary credentials obtained from assuming the role
def getCredentialsForRole(assume_role_arn, role_session_name):
    logger.info(f"Assumed role ARN is {assume_role_arn}")
    
    # Initialize the STS client to use for assuming roles
    sts_client = boto3.client('sts')
    
    try:
        # Attempt to assume the specified role with a session duration of 15 minutes (900 seconds)
        response = sts_client.assume_role(
            RoleArn=assume_role_arn, 
            RoleSessionName=role_session_name, 
            DurationSeconds=900
        )
        temp_credentials = response['Credentials']
        return temp_credentials
    
    except ClientError as err:
        # Handle and log any errors encountered during role assumption
        logger.error(f"Unable to assume role {assume_role_arn}")
        logger.error(f"Error: {err}")
        sys.exit(0)  # Exit the program if role assumption fails

# Function to get temporary AWS STS credentials by assuming a role using provided IAM access and secret keys
# Args:
#   access_key: The AWS IAM Access Key
#   secret_key: The AWS IAM Secret Key
#   role_arn: The ARN of the role to assume
# Returns:
#   A dictionary containing the temporary AWS STS credentials
def getCredentialsfromAPIKeybyAssumingRole(access_key, secret_key, role_arn):
    logger.info(f"Attempting to assume role {role_arn} using provided API keys.")
    
    try:
        # Initialize the STS client with the provided access and secret keys
        sts_client = boto3.client(
            'sts', 
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        
        # Attempt to assume the specified role
        assume_role_response = sts_client.assume_role(
            RoleArn=role_arn, 
            RoleSessionName='my-session-name'
        )
        return assume_role_response['Credentials']
    
    except ClientError as err:
        # Handle and log any errors encountered during role assumption
        logger.error(f"Unable to assume role {role_arn}. Ensure that the APIKey and APISecret are correct and have permission to assume the role.")
        logger.error(f"Error: {err}")
        print(f"Make sure APIKey and APISecret are correct and have permission to assume role - {err}")
        sys.exit(0)  # Exit the program if role assumption fails
