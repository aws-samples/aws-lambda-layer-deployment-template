# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# Description: Lambda Layer Validation Handler tests and validates package deployments by verifying package availability and version.
# Version: 2025-01-22
import json
import logging
import importlib
import platform
import sys
import cfnresponse

# Configure Logging Client
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """ Validate Lambda Layer deployment and return comprehensive status information about package, version, runtime, and architecture compatibility """
    logger.info("Event Received: %s", json.dumps(event, default=str))
    
    # Define consistent Response Data expected by AWS CloudFormation
    response_data = {"Status": "", "Message": "", "TestPackage": "", "TestPackageVersion": "", "TestRuntime": "", "TestArchitecture": ""}
    
    # Handle CloudFormation stack deletion
    if event.get('RequestType') == 'Delete':
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
        return response_data
        
    try:
        # Get configuration from ResourceProperties (Expected: {"ServiceToken": "", "PackageName": "", "PackageVersion": "", "TargetRuntime": "", "TargetArchitecture": ""})
        properties = event.get('ResourceProperties', {})
        package_name = properties.get('PackageName', 'N/A')
        package_import_name = properties.get('PackageImportName', 'N/A')
        target_version = properties.get('PackageVersion', 'N/A')
        target_runtime = properties.get('Runtime', 'N/A')
        target_architecture = properties.get('Architecture', 'N/A')
            
        # Get Current Configuration 
        current_runtime = f"python{sys.version_info.major}.{sys.version_info.minor}"
        current_arch = platform.machine() # "x86_64" | "aarch64"
        current_arch = "arm64" if current_arch == "aarch64" else current_arch # If platform.machine() returns "aarch64", then current_arch = "arm64"

        # Import the package from Lambda Layer, validating the installation.
        try:
            # Note: Package Import Name is the same as Package Name if the package is PEP 8 compliant
            package = importlib.import_module(package_import_name)
            installed_version = getattr(package, '__version__', 'Version Not Found')
            package_status = "INSTALLED"
        except ImportError:
            installed_version = "NOT INSTALLED"
            package_status = "NOT INSTALLED"
        
        # Construct Overall Status from individual test cases.
        overall_status = "SUCCESS" if all([
            package_status == "INSTALLED",
            installed_version == target_version, 
            current_runtime == target_runtime,
            current_arch == target_architecture
        ]) else "FAILED"

        # Construct TestMessage with individual test data
        test_message = (
            f"Installation: Target: {package_name}, Current: {package_status}. "
            f"Version: Target: {target_version}, Current: {installed_version}. "
            f"Runtime: Target: {target_runtime}, Current: {current_runtime}. "
            f"Architecture: Target: {target_architecture}, Current: {current_arch}. "
        )

        # Update Response Data and send Response
        response_data.update({"Status": overall_status, "Message": test_message})
        cfnresponse.send(event, context, overall_status, response_data)
    except Exception as e:
        error_message = str(e)
        logger.error("Error during validation: %s", error_message)
        response_data.update({"Status": "FAILED", "Message": error_message})
        cfnresponse.send(event, context, cfnresponse.FAILED, response_data, reason=error_message)
    
    # Log and return Response Data
    logger.info("Response Data: %s", json.dumps(response_data, default=str))
    return response_data