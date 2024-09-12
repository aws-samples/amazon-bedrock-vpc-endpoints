## Ensure Cross Account Private Connectivity via VPC Endpoints for Amazon Bedrock

Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon via a single API. It also provides broad set of capabilities you need to build generative AI applications, simplifying development while maintaining privacy and security. Since Amazon Bedrock is serverless, you don't have to manage any infrastructure, and you can securely integrate and deploy generative AI capabilities into your applications using the AWS services you are already familiar with.

As of September, 28 2023 AWS Bedrock is Generally Available [Press Release: https://www.aboutamazon.com/news/aws/aws-amazon-bedrock-general-availability-generative-ai-innovations]

This workshop detail mechanisms customers can use to consume AWS Bedrock service. Namely:
1) Access Bedrock via Public Route throught NAT Gateway
2) Enable secure access to Bedrock using VPC Endpoints (PrivateLink)
3) Cross-Account access via AssumeRole

![Bedrock Architecture](./images/bedrock-vpce.jpg)

## Workshop Overview
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

## Prerequisites

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

## Python Prerequisites

Please ensure you have below libraries installed for tool to work successfully in your development environment

```text
pip install cryptography
pip install boto3
pip install botocore
pip install pytz
```

## Executing Workshop

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

Step 2: Update the config file named config-original.properties with appropriate values.

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
Step 4: Delete the original config-original.properties file. (optional)

Step 5: Run following command to invoke bedrock model.
```text
python3 invoke.py
```


Sample invoke - Refer to completion in the section below. User is prompted specify the location of configuration file and choice of model. For visibility and context, the tool lists the complete prompt sent to model (combining System prompt 'system.txt', prompt body 'prompt.txt', user input 'user-query.txt') and further generates the response from the model.
```text
python3 invoke.py
Please provide configuration file path including its name (if no path is provided it will look for config.properties in the same folder as main.py):  

Note:
Bedrock VPCE is not enabled. Using the Bedrock Service URL - https://bedrock-runtime.us-west-2.amazonaws.com

Available Models: ItemsView(<Section: models>)
0: Claude-35-Sonnet
1: Claude-3-Opus
2: Claude-3-Sonnet
3: Claude-3-Haiku
4: Claude-21
5: Llama-31-70b-Instruct
6: Llama-31-8b-Instruct
7: Llama-3-8b-Instruct
8: Mistral-Large-2
9: Mistral-7b-Instruct
10: Mixtral-8x7b-Instruct
11: Titan-Text-Lite
12: Titan-Text
Select the model by entering the number: 0


Model Selected: anthropic.claude-3-5-sonnet-20240620-v1:0


GetCredentialsFrom value is 0
=============================
Complete Prompt Context 


You are an expert SRE (Site Reliability Engineer) who helps other engineers troubleshoot production issues by analyzing logs. An engineer has come to you for help with an issue they are seeing in production. You have been asked to assist a junior engineer in diagnosing and resolving an issue based on an nginx error log entry they have provided.

When the junior engineer provides an error log entry, carefully analyze it to identify the specific issue or error. Explain in detail the likely causes of the issue and the potential impact to the production environment. Provide clear, step-by-step recommendations for troubleshooting and resolving the problem. Also include any preventive measures or best practices that could help avoid similar issues in the future.

Respond using the following JSON format:
<format>
{
  "issue": "Brief description of the identified issue or error",
  "causes": [
    "Potential cause 1",
    "Potential cause 2",
    "..."
  ],
  "impact": "Explanation of how the issue may impact the production environment",
  "troubleshooting": [
    "Step 1",
    "Step 2",
    "..."
  ],
  "prevention": [
    "Preventive measure or best practice 1",
    "Preventive measure or best practice 2",
    "..."  
  ]
}
</format>


Your goal is to provide expert guidance to help the junior engineer efficiently resolve the production issue and learn nginx troubleshooting best practices.

Here are a few examples of nginx error log entries and the expected troubleshooting responses in JSON format:

<example1>
2023/05/21 14:32:10 [error] 12345#12345: *1234567 connect() failed (111: Connection refused) while connecting to upstream, client: 192.168.1.100, server: example.com, request: "GET /api/data HTTP/1.1", upstream: "http://192.168.1.200:8080/api/data", host: "example.com"

{
  "issue": "Connection refused error while connecting to upstream server",
  "causes": [
    "The upstream server at 192.168.1.200:8080 may be down or not responding",
    "There could be a firewall blocking the connection to the upstream server",
    "The upstream server may not be configured to listen on the specified port 8080"
  ],
  "impact": "Requests to the /api/data endpoint are failing, which could impact any features or services dependent on this API",
  "troubleshooting": [
    "Check if the upstream server at 192.168.1.200:8080 is running and responsive",
    "Verify that there are no firewall rules blocking the connection from the nginx server to the upstream server",
    "Ensure that the upstream server is configured to listen on port 8080"
  ],
  "prevention": [
    "Implement proper monitoring and alerting for the upstream server to quickly detect and resolve outages",
    "Regularly review and update firewall rules to ensure necessary connections are allowed",
    "Double-check the upstream server configuration whenever changes are made"
  ]
}
</example1>

<example2>
2023/05/21 15:45:30 [error] 12345#12345: *7654321 open() "/var/www/example.com/nonexistent.html" failed (2: No such file or directory), client: 192.168.1.101, server: example.com, request: "GET /nonexistent.html HTTP/1.1", host: "example.com"

{
  "issue": "File not found error for requested resource",
  "causes": [
    "The requested file /var/www/example.com/nonexistent.html does not exist on the server",
    "There could be a broken link or incorrect URL pointing to this non-existent resource"
  ],
  "impact": "Users are encountering 404 Not Found errors when trying to access the specified resource, leading to a poor user experience",
  "troubleshooting": [
    "Check if the file path is correct and the file exists on the server",
    "Search the codebase and database for any references to the incorrect URL and update them",
    "Consider implementing custom 404 error pages to provide a better user experience"
  ], 
  "prevention": [
    "Regularly audit the website for broken links and missing resources",
    "Implement automated tests to check for 404 errors",
    "Use version control and code reviews to catch and prevent incorrect URL references"
  ]
}
</example2>


Please analyze the following nginx error log entry and provide troubleshooting guidance:

2023/05/21 18:15:45 [crit] 12345#12345: *5432109 SSL_do_handshake() failed (SSL: error:14094438:SSL routines:ssl3_read_bytes:tlsv1 alert internal error) while SSL handshaking, client: 192.168.1.102, server: 0.0.0.0:443


=============================
RESULT: 


Role: assistant
Here's the analysis and troubleshooting guidance for the provided nginx error log entry:

{
  "issue": "SSL handshake failure due to TLSv1 alert internal error",
  "causes": [
    "Mismatch between the SSL/TLS versions supported by the client and server",
    "Incorrect or corrupted SSL certificate configuration on the server",
    "Incompatible cipher suites between client and server",
    "Potential issues with the client's SSL/TLS implementation"
  ],
  "impact": "Users are unable to establish secure HTTPS connections to the server, potentially affecting all SSL/TLS traffic and compromising the security of the service",
  "troubleshooting": [
    "Check the SSL/TLS protocol versions enabled on the nginx server and ensure they match the client's capabilities",
    "Verify the SSL certificate configuration in the nginx server, including the certificate chain and private key",
    "Review the cipher suites enabled on the server and ensure they are compatible with modern clients",
    "Examine the nginx SSL configuration for any misconfigurations or syntax errors",
    "Use OpenSSL's s_client tool to test the SSL handshake and identify specific issues",
    "Check the nginx error logs for any additional context or related errors",
    "If possible, gather information about the client's SSL/TLS implementation and version"
  ],
  "prevention": [
    "Regularly update nginx and OpenSSL to the latest stable versions to ensure support for modern SSL/TLS protocols and security fixes",
    "Implement automated monitoring for SSL/TLS configuration and certificate expiration",
    "Use tools like SSL Labs Server Test to regularly assess the SSL/TLS configuration",
    "Follow industry best practices for SSL/TLS configuration, such as disabling older, insecure protocols and using strong cipher suites",
    "Implement proper logging and alerting for SSL/TLS-related errors to catch issues early",
    "Conduct periodic security audits of the SSL/TLS configuration"
  ]
}

Stop reason: end_turn
=====================

Token usage

Input tokens: 1195
Output tokens: 466
Total tokens: 1661
Latency: 10510 milliseconds
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

