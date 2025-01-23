# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# Description: This script will create an AWS Lambda Layer with the specified configurations, and upload it to Amazon S3.
# Version: 2025-01-21
import os
import sys
import subprocess
import shutil
import json
import logging
import urllib3
import boto3
import cfnresponse

# Configure Logging and HTTP Client
logger = logging.getLogger()
logger.setLevel(logging.INFO)
http = urllib3.PoolManager()

# Initialize AWS service clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Define supported Python packages by this utility. Note that other packages have not been tested to work with this utility.
# Note: Only single-word packages or hyphenated packages that follow standard Python import naming are currently supported.
SUPPORTED_PACKAGES = ['boto3', 'requests', 'urllib3', 'aws-lambda-powertools', 'aws-xray-sdk']

def get_latest_package_version(package_name):
    """Retrieve the latest version of a Python package from PyPI."""
    try:
        url = f'https://pypi.org/pypi/{package_name}/json'
        response = http.request('GET', url)
        if response.status != 200: 
            raise ValueError("PyPI request failed with status %d" % response.status)
        
        data = json.loads(response.data)
        version = data.get("info").get('version')
        if not version:
            raise ValueError("Version information not found in PyPI response")
        return version
    except Exception as e:
        error_message = "Failed to get latest version for %s: %s" % (package_name, str(e))
        raise Exception(error_message)

def create_layer_package(package_name, package_version, runtime_version):
    """
    Create a Lambda Layer package by installing the specified Python package
    and organizing it in the required directory structure.

    Args:
        package_name (str): Name of the Python package to install
        package_version (str): Specific version of the package to install
        runtime_version (str): Python runtime version (e.g., 'python3.12')

    Returns:
        str: File path to the created ZIP file

    Notes:
        - Creates directory structure: /python/lib/python3.x/site-packages/
        - Uses pip to install the package with specific version
        - Packages everything into a ZIP file suitable for Lambda Layers
    """
    # Validate input parameters
    if not all([package_name, package_version, runtime_version]):
        raise ValueError("Missing required parameters for package installation.")

    # Define directory structure
    temp_root = "/tmp"
    site_packages_dir = os.path.join(temp_root, "site-packages")
    python_dir = os.path.join(temp_root, "python")
    temp_dirs = [site_packages_dir, python_dir]

    # Define Lambda Layer ZIP Path
    # Naming Convention: {package_name}-{runtime_version}-{architecture} ex. boto3-python313-arm64
    zip_file = os.path.join(temp_root, f"{package_name}-{runtime_version}-{package_version}.zip")

    try:
        # Cleanup existing directories and files
        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
        if os.path.exists(zip_file):
            os.remove(zip_file)
        
        # Install package using pip (quiet mode)
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q",
            f"{package_name}=={package_version}",
            "--target", site_packages_dir,
            "--no-cache-dir",
            "--disable-pip-version-check"
        ])

        # Create and populate Lambda Layer directory structure
        python_lib_path = os.path.join(python_dir, "lib", runtime_version)
        os.makedirs(python_lib_path, exist_ok=True)
        shutil.move(site_packages_dir, os.path.join(python_lib_path, "site-packages"))

        # Create ZIP file
        zip_base = os.path.splitext(zip_file)[0]
        shutil.make_archive(zip_base, 'zip', temp_root, 'python')
        if not os.path.exists(zip_file):
            raise FileNotFoundError(f"Failed to create ZIP file: {zip_file}")
        
        return zip_file
    except Exception as e:
        raise Exception(f"Layer package creation failed: {str(e)}")
    finally:
        # Cleanup temporary directories
        for dir_path in temp_dirs:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)

def lambda_handler(event, context):
    """
    Main Lambda handler for creating Lambda Layer packages and storing them in Amazon S3.
    
    Workflow:
    1. Get latest version of specified package from PyPI
    2. Create Lambda Layer package with correct structure
    3. Upload Lamba Layer package to Amazon S3
    """
    logger.info("Event Received: %s", json.dumps(event, default=str))
    logger.debug("Installed Boto3 Version: %s", boto3.__version__)

    # Define ResponseData
    response_data = {
        "S3Location": "", "S3Bucket": "", "S3Key": "",
        "PackageName": "", "PackageVersion": "", "PackageImportName": "",
        "CompatibleRuntimes": "", "CompatibleArchitectures": ""
    }

    # Handle CloudFormation Delete Event
    if event.get('RequestType') == 'Delete':
        cfnresponse.send(event, context, "SUCCESS", response_data)
        return response_data

    try:
        # Get Configuration from Resource Properties. Ex: "ResourceProperties": {"ServiceToken": "", "BucketName": "", "PackageName": "", "Runtime": "", "Architecture": ""}
        properties = event.get('ResourceProperties', {})
        bucket_name = properties.get('BucketName')
        package_name = properties.get('PackageName')
        runtime = properties.get('Runtime')
        architecture = properties.get('Architecture')

        # Validate that Required Properties are set
        required_props = {'BucketName': bucket_name, 'PackageName': package_name, 'Runtime': runtime, 'Architecture': architecture}
        missing_props = [k for k, v in required_props.items() if not v]
        if missing_props:
            raise ValueError("Missing required properties: %s" % ', '.join(missing_props))

        # Validate that the requested package is a Supported Package
        if package_name not in SUPPORTED_PACKAGES:
            raise ValueError(f"Package '{package_name}' is not supported. Supported packages: {', '.join(sorted(SUPPORTED_PACKAGES))}\n")
        
        # Step 1: Get Package Information: 1) Package Version from PyPI, 2) Package Import Name.
        package_version = get_latest_package_version(package_name)
        package_import_name = package_name.replace('-', '_') # Get package "import_name" from "package_name" according to PEP8 convention. (Converting hyphens to underscores
        logger.info("Package: %s - Version: %s - Import Name: %s", package_name, package_version, package_import_name)
        
        # Step 2: Create the Layer package
        zip_file = create_layer_package(package_name, package_version, runtime)
        logger.info("Layer package created: %s", zip_file)
        
        # Step 3: Upload Lambda Layer to Amazon S3 Bucket
        layer_name = f"{runtime.replace('.', '')}-{architecture}-{package_name}" # ex. python313-arm64-boto3
        s3_key = f'{layer_name}.zip'
        logger.info("Uploading package to S3: s3://%s/%s", bucket_name, s3_key)

        try:
            s3_client.upload_file(zip_file, bucket_name, s3_key)
            logger.info("Package uploaded to s3://%s/%s", bucket_name, s3_key)
        finally:
            # Cleanup zip file after upload
            if os.path.exists(zip_file):
                os.remove(zip_file)
                logger.info("Cleaned up local zip file: %s", zip_file)

        # Step 4: Update response_data with S3 and package information
        response_data.update({
            "S3Location": f"s3://{bucket_name}/{s3_key}", "S3Bucket": bucket_name, "S3Key": s3_key,
            "PackageName": package_name, "PackageVersion": package_version, "PackageImportName": package_import_name,
            "CompatibleRuntimes": str([runtime]), "CompatibleArchitectures": str([architecture])
        })
        
        # Send success response to CloudFormation
        logger.info("Package successfully uploaded to Amazon S3: %s", response_data["S3Location"])
        cfnresponse.send(event, context, "SUCCESS", response_data)
    except Exception as e:
        error_msg = "Lambda Layer creation failed: %s" % str(e)
        logger.error(error_msg, exc_info=True)
        cfnresponse.send(event, context, "FAILED", response_data, reason=error_msg)

    # Log and Return Response Data
    logger.info("Response Data: %s", json.dumps(response_data, default=str))
    return response_data