# AWS Lambda Layer Deployment Template for Python (aws-lambda-layer-deployment-template)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/aws-samples/lambda-layer-deployment-template?style=flat-square)
[![License](https://img.shields.io/github/license/aws-samples/lambda-layer-deployment-template?style=flat-square)](./LICENSE)

## Overview
This project will automate the deployment of AWS Lambda Layers for Python-based deployments using AWS CloudFormation. Traditional Lambda Layer management often leads to outdated dependencies, as layers are typically created manually and updated infrequently. This project is ideal for AWS developers and DevOps engineers who want to streamline their Lambda function management and ensure consistent Python package versions across their serverless applications.

## Use Cases
- **Serverless Applications**: Keep dependencies current across multiple Lambda functions
- **CI/CD Pipelines**: Automate Lambda Layer updates as part of your deployment process
- **Development Teams**: Standardize package versions across different environments
- **Security Compliance**: Ensure your functions use the latest, most secure package versions

## Architecture
![AWS Lambda Layer Deployment Template Architecture](images/aws-lambda-layer-deployment-template-light.png)

**Deployment Flow**
1. Customers deploy the AWS CloudFormation template [lambda-layer-deployment-template-python.yaml](lambda-layer-deployment-template-python.yaml) with parameters:
    - Python package name (See [Supported Packages (Python)](#supported-packages-python))
    - Lambda runtime version (See [Supported Runtimes - AWS Lambda (Python)](#supported-runtimes---aws-lambda-python))
    - Lambda CPU architecture (See [Supported Architectures - AWS Lambda](#supported-architectures---aws-lambda))
2. The AWS Lambda - Layer Creator function will:
    - Download the specified package from PyPI to ephemeral storage
    - Packages all dependencies into a Lambda Layer ZIP File
    - Uploads the Lambda Layer ZIP file to Amazon S3 bucket
3. AWS CloudFormation Template creates Lambda Layer from ZIP stored in Amazon S3 using:
    - The specified Lambda runtime version
    - Selected Lambda CPU architecture
    - Latest package version
4. The AWS Lambda - Layer Tester validates:
    - Package installation
    - Import functionality
    - Runtime compatibility
  
## Supported Configurations
### Supported Packages (Python)
| Package Name | Import Name | Description | PyPI Link |
|--------------|-------------|-------------|-----------|
| boto3 | boto3 | AWS SDK for Python | [![PyPI](https://img.shields.io/pypi/v/boto3.svg)](https://pypi.org/project/boto3/) |
| requests | requests | HTTP requests library | [![PyPI](https://img.shields.io/pypi/v/requests.svg)](https://pypi.org/project/requests/) |
| urllib3 | urllib3 | HTTP client library | [![PyPI](https://img.shields.io/pypi/v/urllib3.svg)](https://pypi.org/project/urllib3/) |
| aws-lambda-powertools | aws_lambda_powertools | AWS Lambda utilities | [![PyPI](https://img.shields.io/pypi/v/aws-lambda-powertools.svg)](https://pypi.org/project/aws-lambda-powertools/) |
| aws-xray-sdk | aws_xray_sdk | AWS X-Ray tracing | [![PyPI](https://img.shields.io/pypi/v/aws-xray-sdk.svg)](https://pypi.org/project/aws-xray-sdk/) |

**Important Notes**
- All packages will be deployed using the latest package version from [PyPI](https://pypi.org)
- This project has logic in place to support:
  - Simple packages names (e.g., `boto3`)
  - Hyphenated packages with Python import conversion (e.g., `aws-lambda-powertools` → `aws_lambda_powertools`)
- This list of supported packages represents commonly used packages that have been tested by the developer, and can be extended based on your needs with your own testing.

### Supported Runtimes - AWS Lambda (Python)
- python3.10
- python3.11
- python3.12
- python3.13

### Supported Architectures - AWS Lambda
- arm64
- x86_64

## Getting Started
### Prerequisites
- AWS Console access with appropriate permissions
- Python 3.10 or later
- AWS account with Lambda and S3 access

### Deployment (AWS Console)
1. **Download the AWS CloudFormation Template:** [lambda-layer-deployment-template-python.yaml](lambda-layer-deployment-template-python.yaml)

2. **Launch AWS CloudFormation**
   - Open [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation)
   - Click "Create stack" → "With new resources (standard)"
   - Choose "Upload a template file"
   - Upload `lambda-layer-deployment-template-python.yaml`
   - Click "Next"

3. **Configure Stack**
   - Stack name: Provide a unique stack name (e.g., `lambda-layer-stack`)
   - Parameters:
     - PackageName: Choose from [supported packages](#supported-packages-python) (e.g., `boto3`)
     - Runtime: Select Python version (e.g., `python3.13`)
     - Architecture: Choose `arm64` or `x86_64`
   - Click "Next"

4. **Review and Create**
   - Review configuration
   - Acknowledge IAM resource creation
   - Click "Create stack"

5. **Monitor Deployment**
   - Wait for stack creation (approximately 2-3 minutes)
   - Check the "Events" tab for progress
   - Stack status should show "CREATE_COMPLETE"
   - Review the "Outputs" tab to validate deployment

### Using your AWS Lambda Layer 
Your Lambda Layer is now ready for use with your AWS Lambda functions. For detailed instructions on adding layers to Lambda functions, refer to the [AWS Lambda Developer Guide - Using Layers](https://docs.aws.amazon.com/lambda/latest/dg/adding-layers.html).

## Additional Resources
- [AWS Lambda Developer Guide - Managing Lambda dependencies with layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [AWS Lambda Developer Guide - Selecting and configuring an instruction set architecture for your Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/foundation-arch.html)
- [AWS Lambda Developer Guide - Lambda Runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)
- [AWS Lambda Developer Guide - Using AWS CloudFormation with layers](https://docs.aws.amazon.com/lambda/latest/dg/layers-cfn.html)
- [PEP 423 – Naming conventions and recipes related to packaging](https://www.python.org/dev/peps/pep-0423/)

## Troubleshooting
1. **Layer Creation Failures**
   - Check CloudWatch logs for the `LayerCreatorFunction`
   - Verify PyPI package name is correct
   - Ensure S3 bucket permissions are properly configured
2. **Layer Testing Failures**
   - Examine `LayerTestCustomResource` logs in CloudWatch
   - Verify Python runtime compatibility
   - Check if package import name matches PyPI name
3. **Deployment Issues**
   - Ensure AWS CLI has sufficient permissions
   - Verify CloudFormation service role permissions
   - Check if the specified runtime/architecture combination is supported

## Contributing
See [CONTRIBUTING](CONTRIBUTING.md) for more information

## Security
See [CONTRIBUTING - Security issue notifications](CONTRIBUTING.md#security-issue-notifications) for more information.

## License
This library is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file.

## Author
Taylan Unal, Specialist Solutions Architect II, Amazon Web Services
