## Ensure Cross Account Private Connectivity via VPC Endpoints for Amazon Bedrock

# Amazon Bedrock Access Patterns

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API. It also provides broad set of capabilities you need to build generative AI applications, simplifying development while maintaining privacy and security. Since Amazon Bedrock is serverless, you don't have to manage any infrastructure, and you can securely integrate and deploy generative AI capabilities into your applications using the AWS services you are already familiar with.

As of September, 28 2023 AWS Bedrock is Generally Available [Press Release: https://www.aboutamazon.com/news/aws/aws-amazon-bedrock-general-availability-generative-ai-innovations]

This workshop detail mechanisms customers can use to consume AWS Bedrock service. Namely:
1) Access Bedrock via Public Route throught NAT Gateway
2) Enable secure access to Bedrock using VPC Endpoints (PrivateLink)
3) Cross-Account access via AssumeRole

![Bedrock Architecture](./images/bedrock-vpce.jpg)

# Workshop Overview
This workshop provides hands-on experience and Python code snippets to consume Foundational Models available in AWS Bedrock. "prompt.txt" file contains necessary model configurations to invoke FMs in Amazon Bedrock. Below is one such sample for Anthropic Claude V2 Model invocation.

```JSON
{
        "prompt": "\n\nHuman: What is square root of 16? Provide step by step explaination\n\nAssistant:", 
        "max_tokens_to_sample":300,
        "stop_sequences":["\n\nHuman:","\n\nAssistant"],
        "temperature":1,
        "top_p":0.9,
        "top_k":250,
        "anthropic_version":"bedrock-2023-05-31"
}
```

<details>
  
<summary>How to find prompt configuration for various models</summary>

### Bedrock API Request

Visit the Amazon Bedrock Service page and follow the numbered sequence shown in the screenshot below.

![View API Request](./images/bedrock-playground.jpg)
  
</details>

# Prerequisites

1. Ensure Foundational Models are enabled in Amazon Bedrock

   <details>
  
   <summary>How to enable foundational models</summary>

   ### Model Access

   Visit the Amazon Bedrock Service page and follow the numbered sequence as shown in the screenshot below.

   ![View API Request](./images/model-access.jpg)

   ![View API Request](./images/model-access-2.jpg)
  
   </details>

2. Setup IAM Roles for Bedrock Access [Refer: https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html] and assign it as an EC2 role to AWS Cloud9 environment.

3. Create Private VPC Endpoints for Bedrock Access to test Private Acccess [Refer: https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html]

   Note: You can control access to VPCe by updating the resource policy to specific Principal and Resources. 

4. Create VPC Peering Connection to test cross account access through VPC EndPoints [Refer: https://repost.aws/knowledge-center/vpc-peering-connection-create]

   Note: This workshop uses VPC Peering, however, same can be achieved through Transit Gateway setup that overcomes some of VPC Peering Limitations. [Refer: https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/vpc-to-vpc-connectivity.html]

5. Cloud9 comes pre-installed with Python. However, you would need to install Boto3 Bedrock SDK libraries. [Refer: https://docs.aws.amazon.com/bedrock/latest/userguide/api-setup.html]

> [!NOTE]
> If your dev environment is in PrivateSubnet make sure to have NAT setup appropriately to access Bedrock Service when not using VPC Endpoints [Refer: https://docs.aws.amazon.com/appstream2/latest/developerguide/managing-network-internet-NAT-gateway.html]


# Executing Workshop

Download contents of the workshop in your Cloud9 development environment. Prior to executing the .py files, lets analyze the configuration files that drive various integrations to AWS Bedrock. 

```ini
[default]
UseVPCe = <true/false>
GetCredentialsFrom = <0/1/2>
Region = <us-east-1/us-west-2/others>
AccessKey = <access-key>
SecretKey = <secret-key>
AssumeRoleARN = <iam-role-arn>
VPCEndpointURL = <bedrock-vpc-endpoint-url>
PromptFilePath = <prompt-file-name>
Debug = <true/false>

[models]
Claude-35-Sonnet = anthropic.claude-3-5-sonnet-20240620-v1:0
Claude-3-Opus = anthropic.claude-3-opus-20240229-v1:0
Claude-3-Sonnet = anthropic.claude-3-sonnet-20240229-v1:0
Claude-3-Haiku = anthropic.claude-3-haiku-20240307-v1:0
Claude-21 = anthropic.claude-v2:1
Llama-31-70b-Instruct = meta.llama3-1-70b-instruct-v1:0
Llama-31-8b-Instruct = meta.llama3-1-8b-instruct-v1:0
Llama-3-8b-Instruct = meta.llama3-8b-instruct-v1:0
Mistral-Large-2 = mistral.mistral-large-2407-v1:0
Mistral-7b-Instruct = mistral.mistral-7b-instruct-v0:2
Mixtral-8x7b-Instruct = mistral.mixtral-8x7b-instruct-v0:1
Titan-Text-Lite = amazon.titan-text-lite-v1
Titan-Text = amazon.titan-text-express-v1
```

* UseVPCe - Accepts <true/false> as values and defines if application should connect to Bedrock via VPC EndPoint or through public bedrock endpoint [https://bedrock-runtime.<Region>.amazonaws.com](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html).
* GetCredentialsFrom - defines where application should fetch credentials from to connect with Bedrock. Valid values are <0/1/2>
        0 - defines system should use the EC2 Instance Role credentials (assuming role assigned to EC2/Cloud9 environment has access to bedrock)
        1 - refers to an option of fetching credentials through AWS STS by assuming role across account
        2 - refers to the option of fetching credentials using IAM Access Key and Secret Key. You would still need to assume a role using these keys to fetch short team credentials to access Bedrock. 
* AccessKey - IAM Access Key
* SecretKey - IAM Secret Key
  
> [!NOTE]
> Use of IAM Access/Secret Keys are discouraged since that open a security risk considering they are long lived tokens. Ideally, developers should use AWS SSO cli to fetch temporary credentials to connect with AWS Services from outside AWS. [Refer: https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html]. This workshop do provide ability to provide Access/Secret keys to unblock users to gaining hands-on experince in case AWS SSO is not setup or user do not have any other means of gaining temporary credentials.

* AssumeRoleARN - IAM Role ARN for the role that has access to Amazon Bedrock
* VPCEndpointURL - VPC Endpoint URL [Example: https://vpce-xxxxxxx-xxxxx.bedrock-runtime.us-west-2.vpce.amazonaws.com](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html)
* PromptFilePath - Path to file containing prompt structure
* Debug - Enables logging. Accepted values <true/false>
* [models] - This section contains the list of models the user can invoke on Bedrock. The user can make updates to this list as necessary. Please ensure models are activated in Amazon Bedrock through Model access page before using this tool and the models from this list.



**Walkthrough**

Step 1: cd to project directory

Step 2: Create Config file and name it config-original.properties.

Sample Config File
```ini
[default]
UseVPCe=true
GetCredentialsFrom=1
Region=us-west-2
AccessKey=xxxxxxxxx
SecretKey=xxxxxxxxx
AssumeRoleARN=arn:aws:iam::xxxxx:role/my-bedrock
VPCEndpointURL=https://vpce-xxxx-xxx.bedrock.us-west-2.vpce.amazonaws.com
PromptFilePath=prompt.txt
Debug=false
```

Step 3: Encrypt the configuration file by running following command. Application uses Fernet to encrypt and decrypt values from configuration files. Each time you encrypt a new key is generated and used as secret required to encrypt and decrypt values. 
```text
python3 encryptConfig.py
```

Sample Execution: 

In below sample 'cpcgMwyzPCi-IMD5O1ESZGaAeMy6N_xxxxxxxxx' is the secret that is generated as run time to encrypt values. This Secret is converted to base64 and added to the new configuration file.
```text
python3 encryptConfig.py
cpcgMwyzPCi-IMD5O1ESZGaAeMy6N_xxxxxxxxx
Please provide configuration file path including its name:  config-original.properties
Please provide new configuration file path including its name:  config.properties
{'UseVPCe': 'true', 'GetCredentialsFrom': '1', 'Region': 'us-west-2', 'AccessKey': 'xxxxx', 'SecretKey': 'xxxxx', 'AssumeRoleARN': 'Z0FBQUFBQmxHU2txQUVpUjNaazAwZ0dDTjV3QTB5ZEtEaDFEQTFveU52NEl4VkhaTmhOVkl1bHZMhkhfuiwcei2u3yi2FkWWVmS2huSmRCMHV3ZXJ1ckhvZkFpN3JXdUJmUWV2VUcwUUxUQ1Z3WkNBPT0=', 'VPCEndpointURL': 'Z0FBQUFBQmxHU2txRllEOW1xNDRVN1h5bDNkdhfskjhfdskhfdkXcW5CbVU4M0xROWl3Z05hMlpjd1pRWUpQdkRBTlIyLTNKRnpWY2RtYWNBdU9uOE5wT296Smc2Vk5fdFh2dE5pbHJodGZ3MW9hMWttcVlKUnVOWHM5elhxWC1QaU9xSElUcFBPOU1CMENu', 'PromptFilePath': 'prompt.txt', 'ModelID': 'anthropic.claude-v2', 'Debug': 'true', 'SecretKeyFernet': 'xxxxx='}
```
Step 4: Delete the original config-original.properties file. 

Step 5: Run following command to invoke bedrock model.
```text
python3 invoke.py
```
Sample prompt - prompt.txt
```json
{
        "prompt": "Human: What is square root of 16? Provide step by step explaination\nAssistant:", 
        "max_tokens_to_sample":300,
        "stop_sequences":["\n\nHuman:","\n\nAssistant"],
        "temperature":1,
        "top_p":0.9,
        "top_k":250,
        "anthropic_version":"bedrock-2023-05-31"
}
```

Sample invoke - Refer to completion in the section below. This is the response from the model.
```text
python3 invoke.py
lplAg7xROZfCc1XRtPLweIudCXn1hHKwhCCuvqKM178=
Please provide configuration file path including its name (if no path it provided it will look for config.properties in the same folder as invoke.py):  config.properties
-----------------------
{'completion': " Okay, here are the step-by-step workings to find the square root of 16:\n1) 16 is a perfect square number, meaning it can be expressed as the square of an integer.\n2) To find the square root, we need to find the integer that when multiplied by itself gives 16. \n3) Let's think through the possible integers:\n1 x 1 = 1 \n2 x 2 = 4\n3 x 3 = 9  \n4 x 4 = 16\n4) Since 4 x 4 equals 16, the square root of 16 is 4.\n\nIn summary, to find the square root of a number:\n- Determine if it is a perfect square \n- Find the integer that when squared gives the original number\n- The square root is that integer\n\nSo the square root of 16 is 4.", 'stop_reason': 'stop_sequence'}
Model Execution Time in Seconds:  5
=================
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

