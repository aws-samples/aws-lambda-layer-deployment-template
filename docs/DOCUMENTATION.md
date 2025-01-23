## DOCUMENTATION.md

## Technical Overview
The AWS CloudFormation template will:
1. Deploy an AWS Lambda function that can create AWS Lambda Layers, storing them in Amazon S3.
2. Run the AWS Lambda function to create an AWS Lambda Layer according to the parameters provided by AWS CloudFormation
3. Deploy an AWS Lambda Function (test-lambda-layer) that will use the deployed AWS Lambda Layer, and run a basic version check.
4. Run the AWS Lambda Function (test-lambda-layer), and return the results of the test as AWS CloudFormation outputs.

###  Notes regarding package names and imports (PEP8 Styling Guide)
**Package Names on PyPI:**
- Can use hyphens (-) or underscores (_)
- Hyphens are more common as they're more readable
- Examples: aws-lambda-powertools, python-dateutil

**Import Names in Python:**
- Must use underscores (_) as hyphens aren't valid in Python identifiers
- The same package is imported using underscores
- Examples: aws_lambda_powertools, python_dateutil

### Technical Details
This project leverages Python's flexible package management system to create Lambda Layers dynamically:
1. **Inline Package Installation**: Utilizes Python's ability to install packages programmatically during runtime
   ```python
   import subprocess
   subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
   ```
2. **Dynamic Layer Creation**: Packages are installed directly into the Lambda execution environment
3. **Runtime Compatibility**: Ensures packages are compiled for the specific Lambda runtime and architecture
4. **Automatic Testing**: Validates package imports before finalizing the layer

## Github Description
🚀 AWS Lambda Layer Deployment Template | Streamline Python dependency management in your serverless applications by automatically creating, versioning, and deploying Lambda Layers. Features version control, multiple runtime and architecture support, and Infrastructure as Code (IaC) templates for seamless CI/CD integration.