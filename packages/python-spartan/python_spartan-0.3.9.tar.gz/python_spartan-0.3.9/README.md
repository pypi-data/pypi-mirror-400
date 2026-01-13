
# Spartan CLI for Spartan Serverless Framework

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Spartan CLI** is the official command-line interface for the [Spartan Serverless Framework](https://github.com/nerdmonkey/spartan-framework), the Swiss Army knife for serverless development. The CLI provides powerful commands and utilities to scaffold, manage, and operate serverless applications built with the Spartan Framework on AWS, GCP, and (soon) Azure.

---

## What is Spartan CLI?

Spartan CLI is the companion tool for the [Spartan Serverless Framework](https://github.com/nerdmonkey/spartan-framework), a Python-based scaffold and library for building scalable, consistent serverless applications (APIs, workflows, ETL, microservices, and more). The CLI lets you generate, configure, deploy, and manage these applications from the command line, automating common tasks and ensuring best practices.

**Use Spartan CLI to:**
- Generate handler and workflow code compatible with the Spartan Framework
- Manage cloud resources and deployments
- Validate and inspect your project configuration
- Run, test, and debug serverless workflows and functions
- Integrate with CI/CD and automate your serverless development workflow

> **Note:** Spartan CLI is tightly integrated with the Spartan Framework and is the recommended way to interact with Spartan-based projects.

---

## Why Spartan?

Spartan (Framework + CLI) is often called "the Swiss Army knife for serverless development." It simplifies the creation of serverless applications on popular cloud providers by generating Python code, scaffolding best practices, and providing a unified developer experience. Spartan streamlines your development process, saving you time and ensuring code consistency in your serverless projects.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd spartan-cli

# Install dependencies
make dev-install

# Run the CLI
poetry run spartan --help
```

### Basic Usage

```bash
# Show available commands
spartan --help

# Workflow operations (AWS Step Functions / GCP Workflows)
spartan workflow --help
spartan workflow list
spartan workflow view my-workflow
spartan workflow run my-workflow

# S3 operations
spartan s3 --help

# Job operations
spartan job --help

# Parquet operations
spartan parquet --help
```

## 📝 Configuration

Spartan CLI supports project-level configuration through a `.spartan` configuration file. This allows you to specify cloud provider preferences and other settings on a per-project basis.

### Configuration File Format

The `.spartan` file uses INI format with a `[default]` section:

```ini
[default]
provider = aws
```

**Supported Providers:**
- `aws` - Amazon Web Services
- `gcp` - Google Cloud Platform (default)

### Configuration File Discovery

Spartan automatically discovers your configuration file by:

1. Starting from your current working directory
2. Traversing upward through parent directories
3. Using the first `.spartan` file found
4. Stopping at your home directory or filesystem root

This means you can run Spartan commands from any subdirectory in your project, and it will automatically find and use your project's configuration.

**Example Directory Structure:**

```
my-project/
├── .spartan          # Project configuration
├── src/
│   └── handlers/     # Run commands from here
└── tests/            # Or from here
```

### Default Behavior

If no `.spartan` file is found, Spartan uses these defaults:
- **Provider**: `gcp` (Google Cloud Platform)
- No warnings or errors are displayed

This allows you to use Spartan immediately without any configuration setup.

### Creating a Configuration File

Create a `.spartan` file in your project root:

```bash
# Create configuration file
cat > .spartan << EOF
[default]
provider = aws
EOF
```

Or manually create the file with your preferred editor:

```ini
[default]
provider = aws
```

### Configuration Commands

Spartan provides commands to manage and validate your configuration:

```bash
# Validate your configuration file
spartan config --validate

# Show current configuration
spartan config --show
```

**Validation Output:**

```bash
$ spartan config --validate
✓ Configuration is valid
  Provider: aws
  Config file: /path/to/project/.spartan
```

**Show Configuration Output:**

```bash
$ spartan config --show
Current Configuration:
  Provider: aws
  Config file: /path/to/project/.spartan
```

### Configuration Errors

Spartan provides clear error messages when configuration issues occur:

**Invalid Provider:**
```bash
$ spartan config --validate
✗ Configuration Error: Invalid provider 'azure' in configuration.
  Valid options are: 'aws', 'gcp'.
```

**Invalid INI Syntax:**
```bash
$ spartan config --validate
✗ Configuration Error: Invalid configuration file syntax at line 2: ...
  Please check INI format.
```

**Permission Issues:**
```bash
$ spartan config --validate
✗ Configuration Error: Cannot read configuration file '.spartan': Permission denied.
  Please check file permissions.
```

### Example Configurations

**AWS Configuration:**
```ini
[default]
provider = aws
```

**GCP Configuration:**
```ini
[default]
provider = gcp
```

**Empty File (uses defaults):**
```ini
# Empty file or no provider key defaults to GCP
[default]
```

## 🔄 Workflow Commands

Spartan CLI provides comprehensive workflow management commands for orchestrating serverless workflows on both AWS Step Functions and GCP Workflows. The commands automatically adapt based on your configured cloud provider.

### Overview

The workflow commands allow you to:
- List and discover available workflows
- View workflow definitions and metadata
- Execute workflows with custom input
- Monitor execution history
- View detailed execution logs

### Provider Support

- **AWS**: Manages AWS Step Functions state machines
- **GCP**: Manages Google Cloud Platform Workflows

The CLI automatically uses the provider configured in your `.spartan` file, or you can override it using the `--provider` flag.

### Available Commands

#### List Workflows

List all available workflows in your cloud account:

```bash
# List all workflows (uses configured provider)
spartan workflow list

# List workflows with specific provider
spartan workflow list --provider aws
spartan workflow list --provider gcp

# Filter by status
spartan workflow list --status ACTIVE

# Different output formats
spartan workflow list --output json
spartan workflow list --output yaml
spartan workflow list --output table  # default
```

**Output Example:**
```
┌─────────────────────┬────────┬─────────────────────┐
│ Name                │ Status │ Created             │
├─────────────────────┼────────┼─────────────────────┤
│ my-workflow         │ ACTIVE │ 2024-01-15 10:30:00 │
│ data-processor      │ ACTIVE │ 2024-01-10 14:20:00 │
└─────────────────────┴────────┴─────────────────────┘
```

#### View Workflow Definition

View the complete definition and metadata for a specific workflow:

```bash
# View workflow definition
spartan workflow view my-workflow

# View with specific provider
spartan workflow view my-workflow --provider aws

# Output in different formats
spartan workflow view my-workflow --output json
spartan workflow view my-workflow --output yaml
```

**AWS Output Example:**
```json
{
  "name": "my-workflow",
  "arn": "arn:aws:states:us-east-1:123456789012:stateMachine:my-workflow",
  "status": "ACTIVE",
  "type": "STANDARD",
  "definition": {
    "Comment": "My workflow definition",
    "StartAt": "FirstState",
    "States": {
      "FirstState": {
        "Type": "Task",
        "Resource": "arn:aws:lambda:...",
        "End": true
      }
    }
  }
}
```

**GCP Output Example:**
```yaml
name: my-workflow
createTime: '2024-01-15T10:30:00Z'
revisionId: '000001-abc'
state: ACTIVE
sourceContents: |
  - step1:
      call: http.get
      args:
        url: https://api.example.com/data
      result: apiResponse
  - step2:
      return: ${apiResponse.body}
```

#### Run Workflow

Execute a workflow with optional input:

```bash
# Run workflow without input
spartan workflow run my-workflow

# Run with JSON input
spartan workflow run my-workflow --input '{"key": "value"}'

# Run with input from file
spartan workflow run my-workflow --input-file input.json

# Skip confirmation prompt (for automation)
spartan workflow run my-workflow --yes

# Run with specific provider
spartan workflow run my-workflow --provider gcp
```

**Output Example:**
```
✓ Workflow execution started successfully

Execution ID: abc123-def456-ghi789
Resource: arn:aws:states:us-east-1:123456789012:execution:my-workflow:abc123-def456-ghi789
Status: RUNNING
```

#### List Executions

View execution history for a workflow:

```bash
# List recent executions (default: 10)
spartan workflow executions my-workflow

# List more executions
spartan workflow executions my-workflow --limit 50

# Filter by status
spartan workflow executions my-workflow --status SUCCEEDED
spartan workflow executions my-workflow --status FAILED

# Different output formats
spartan workflow executions my-workflow --output json
```

**Output Example:**
```
┌──────────────────────┬───────────┬─────────────────────┬─────────────────────┐
│ Execution ID         │ Status    │ Start Time          │ End Time            │
├──────────────────────┼───────────┼─────────────────────┼─────────────────────┤
│ abc123-def456        │ SUCCEEDED │ 2024-01-15 10:30:00 │ 2024-01-15 10:31:00 │
│ xyz789-uvw012        │ FAILED    │ 2024-01-15 09:15:00 │ 2024-01-15 09:16:00 │
│ mno345-pqr678        │ RUNNING   │ 2024-01-15 10:35:00 │ -                   │
└──────────────────────┴───────────┴─────────────────────┴─────────────────────┘
```

#### View Execution Logs

View detailed logs and state transitions for a specific execution:

```bash
# View execution logs
spartan workflow execution logs abc123-def456

# View with specific provider
spartan workflow execution logs abc123-def456 --provider aws

# Stream logs in real-time (for running executions)
spartan workflow execution logs abc123-def456 --follow

# Output in different formats
spartan workflow execution logs abc123-def456 --output json
```

**Output Example:**
```
Execution: abc123-def456
Status: SUCCEEDED
Duration: 1m 23s

State Transitions:
┌─────────────────────┬────────────────┬─────────────────────┐
│ State               │ Event Type     │ Timestamp           │
├─────────────────────┼────────────────┼─────────────────────┤
│ ExecutionStarted    │ START          │ 2024-01-15 10:30:00 │
│ FirstState          │ TASK_STARTED   │ 2024-01-15 10:30:01 │
│ FirstState          │ TASK_SUCCEEDED │ 2024-01-15 10:30:45 │
│ SecondState         │ TASK_STARTED   │ 2024-01-15 10:30:46 │
│ SecondState         │ TASK_SUCCEEDED │ 2024-01-15 10:31:20 │
│ ExecutionSucceeded  │ END            │ 2024-01-15 10:31:23 │
└─────────────────────┴────────────────┴─────────────────────┘
```

### Authentication Setup

#### AWS Authentication

Configure AWS credentials using one of these methods:

**Option 1: AWS CLI Configuration**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option 2: AWS Profile**
```bash
# Use a specific AWS profile
spartan workflow list --profile my-profile
```

**Required AWS Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "states:ListStateMachines",
        "states:DescribeStateMachine",
        "states:StartExecution",
        "states:ListExecutions",
        "states:DescribeExecution",
        "states:GetExecutionHistory"
      ],
      "Resource": "*"
    }
  ]
}
```

#### GCP Authentication

Configure GCP credentials using one of these methods:

**Option 1: Application Default Credentials**
```bash
# Login with your user account
gcloud auth application-default login

# Or set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Option 2: Service Account Key**
```bash
# Download service account key from GCP Console
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id
```

**Required GCP Permissions:**
- `workflows.workflows.list`
- `workflows.workflows.get`
- `workflows.executions.create`
- `workflows.executions.list`
- `workflows.executions.get`

**GCP IAM Role:**
```bash
# Grant Workflows Admin role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/workflows.admin"
```

### Configuration Examples

#### AWS Configuration

```ini
# .spartan file for AWS
[default]
provider = aws
```

```bash
# Set AWS region (optional)
export AWS_DEFAULT_REGION=us-east-1

# Use specific AWS profile (optional)
export AWS_PROFILE=my-profile
```

#### GCP Configuration

```ini
# .spartan file for GCP
[default]
provider = gcp
```

```bash
# Set GCP project (required)
export GOOGLE_CLOUD_PROJECT=my-project-id

# Set GCP location (optional, defaults to us-central1)
export GOOGLE_CLOUD_LOCATION=us-central1

# Set service account credentials (if not using ADC)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Troubleshooting

#### Common Issues

**1. Credentials Not Configured**

**AWS Error:**
```
Error: AWS credentials not configured
Suggestion: Run 'aws configure' to set up your AWS credentials.
```

**Solution:**
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**GCP Error:**
```
Error: GCP credentials not configured
Suggestion: Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS.
```

**Solution:**
```bash
gcloud auth application-default login
# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**2. Permission Denied**

**Error:**
```
Error: Permission denied: User lacks required permissions
```

**Solution:**
- **AWS**: Ensure your IAM user/role has the required Step Functions permissions
- **GCP**: Ensure your service account has the Workflows Admin role or equivalent permissions

**3. Workflow Not Found**

**Error:**
```
Error: Workflow 'my-workflow' not found
```

**Solution:**
- Verify the workflow name is correct
- Check you're using the correct provider (`--provider aws` or `--provider gcp`)
- Verify you're in the correct region/project
- List all workflows to see available names: `spartan workflow list`

**4. Invalid JSON Input**

**Error:**
```
Error: Invalid JSON input: Expecting property name enclosed in double quotes
```

**Solution:**
- Ensure JSON is properly formatted with double quotes
- Use a JSON validator to check your input
- Consider using `--input-file` for complex JSON

**5. Rate Limiting**

**Error:**
```
Error: Rate limit exceeded. Please retry after a delay.
```

**Solution:**
- Wait a few seconds and retry
- Reduce the frequency of API calls
- Consider implementing exponential backoff in automation scripts

#### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set log level to debug
export SPARTAN_LOG_LEVEL=DEBUG

# Run command with verbose output
spartan workflow list -v
```

#### Getting Help

```bash
# Show help for workflow commands
spartan workflow --help

# Show help for specific command
spartan workflow list --help
spartan workflow run --help
```

### Advanced Usage

#### Automation Scripts

```bash
#!/bin/bash
# Example: Run workflow and wait for completion

# Run workflow
EXECUTION_ID=$(spartan workflow run my-workflow \
  --input '{"data": "value"}' \
  --yes \
  --output json | jq -r '.execution_id')

echo "Started execution: $EXECUTION_ID"

# Poll for completion
while true; do
  STATUS=$(spartan workflow execution logs $EXECUTION_ID \
    --output json | jq -r '.status')

  if [[ "$STATUS" == "SUCCEEDED" ]]; then
    echo "Execution completed successfully"
    break
  elif [[ "$STATUS" == "FAILED" ]]; then
    echo "Execution failed"
    exit 1
  fi

  sleep 5
done
```

#### Multi-Provider Workflows

```bash
# Run same workflow on both providers
spartan workflow run my-workflow --provider aws --input '{"env": "aws"}'
spartan workflow run my-workflow --provider gcp --input '{"env": "gcp"}'

# Compare execution times
spartan workflow executions my-workflow --provider aws --limit 1
spartan workflow executions my-workflow --provider gcp --limit 1
```

#### CI/CD Integration

```yaml
# GitHub Actions example
name: Deploy Workflow
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install Spartan
        run: pip install python-spartan

      - name: Configure AWS
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          spartan workflow run deployment-workflow \
            --input-file deploy-config.json \
            --yes
```

## 🔧 Handler Commands

Spartan CLI provides comprehensive serverless function management commands for both AWS Lambda and GCP Cloud Functions. The commands automatically adapt based on your configured cloud provider, allowing you to create, list, describe, and download serverless functions with a unified interface.

### Overview

The handler commands allow you to:
- Create handler files from templates with appropriate boilerplate
- List deployed serverless functions with filtering and sorting
- View detailed function configuration and metadata
- Download function source code for local development
- Delete local handler files

### Provider Support

- **AWS**: Manages AWS Lambda functions
- **GCP**: Manages Google Cloud Platform Cloud Functions (1st and 2nd generation)

The CLI automatically uses the provider configured in your `.spartan` file.

### Available Commands

#### Create Handler File

Create a new handler file from a template with appropriate boilerplate code:

```bash
# Create a basic handler (uses configured provider)
spartan handler create my-handler

# Create handler with HTTP trigger (GCP)
spartan handler create api-handler --subscribe http

# Create handler with Pub/Sub trigger (GCP)
spartan handler create event-handler --subscribe pubsub

# Create handler with Cloud Storage trigger (GCP)
spartan handler create storage-handler --subscribe storage

# Create handler with SQS trigger (AWS)
spartan handler create queue-handler --subscribe sqs

# Create handler with SNS trigger (AWS)
spartan handler create notification-handler --subscribe sns
```

**Output Example:**
```
✓ Handler file created successfully
  File: handlers/my_handler.py
  Template: GCP HTTP trigger
```

**Available Triggers:**

**GCP Triggers:**
- `http` - HTTP/HTTPS requests
- `pubsub` - Pub/Sub messages
- `storage` - Cloud Storage events
- `firestore` - Firestore document changes
- `scheduler` - Cloud Scheduler jobs

**AWS Triggers:**
- `sqs` - SQS queue messages
- `sns` - SNS topic notifications
- `s3` - S3 bucket events
- `api` - API Gateway requests
- And many more (see AWS Lambda documentation)

#### List Handlers

List all deployed serverless functions with filtering and sorting:

```bash
# List all functions (uses configured provider)
spartan handler list

# List with specific provider
spartan handler list --provider aws
spartan handler list --provider gcp

# Filter by name prefix
spartan handler list --prefix my-

# Filter by regex pattern
spartan handler list --match "^api-.*"

# Filter by runtime
spartan handler list --runtime python311

# Sort by different fields
spartan handler list --sort name --order asc
spartan handler list --sort memory --order desc
spartan handler list --sort modified --order desc

# Different output formats
spartan handler list --output json
spartan handler list --output yaml
spartan handler list --output table  # default
spartan handler list --output markdown
spartan handler list --output csv

# Limit results
spartan handler list --limit 10

# Show applied filters
spartan handler list --prefix api- --show-filters

# Save output to file
spartan handler list --output json --save-to functions.json
```

**Output Example (Table Format):**
```
┌──────────────────┬───────────┬────────┬─────────┬─────────────────────┐
│ Name             │ Runtime   │ Memory │ Timeout │ Last Modified       │
├──────────────────┼───────────┼────────┼─────────┼─────────────────────┤
│ api-handler      │ python311 │ 256 MB │ 60s     │ 2024-01-15 10:30:00 │
│ event-processor  │ python311 │ 512 MB │ 120s    │ 2024-01-14 15:20:00 │
│ data-transformer │ nodejs20  │ 1024MB │ 300s    │ 2024-01-13 09:45:00 │
└──────────────────┴───────────┴────────┴─────────┴─────────────────────┘
```

**Output Example (JSON Format):**
```json
[
  {
    "name": "api-handler",
    "runtime": "python311",
    "memory": 256,
    "timeout": 60,
    "modified": "2024-01-15 10:30:00",
    "description": "API request handler",
    "handler": "main.handler",
    "arn": "projects/my-project/locations/us-central1/functions/api-handler"
  }
]
```

#### Describe Handler

View detailed information about a specific function:

```bash
# Describe a function (uses configured provider)
spartan handler describe my-function

# Describe with specific provider
spartan handler describe my-function --provider aws
spartan handler describe my-function --provider gcp

# Different output formats
spartan handler describe my-function --output json
spartan handler describe my-function --output yaml
spartan handler describe my-function --output table  # default
spartan handler describe my-function --output text
spartan handler describe my-function --output markdown

# GCP-specific: specify project and location
spartan handler describe my-function --project-id my-project --location us-central1

# AWS-specific: specify region and profile
spartan handler describe my-function --region us-east-1 --profile production
```

**Output Example (AWS Lambda):**
```
Function Details: my-function
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Basic Information:
  Name:        my-function
  ARN:         arn:aws:lambda:us-east-1:123456789012:function:my-function
  Runtime:     python3.11
  Handler:     index.handler
  Description: My Lambda function

Configuration:
  Memory:      256 MB
  Timeout:     60 seconds
  Role:        arn:aws:iam::123456789012:role/lambda-role

Environment Variables:
  DATABASE_URL: ********
  API_KEY:      ********
  LOG_LEVEL:    INFO

Trigger Configuration:
  Type:        API Gateway
  Method:      POST
  Path:        /api/handler
```

**Output Example (GCP Cloud Function):**
```
Function Details: my-function
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Basic Information:
  Name:         my-function
  Resource:     projects/my-project/locations/us-central1/functions/my-function
  Runtime:      python311
  Entry Point:  handler
  Generation:   2nd gen
  State:        ACTIVE

Configuration:
  Memory:       256 MB
  Timeout:      60 seconds
  Service Acct: my-function@my-project.iam.gserviceaccount.com

Environment Variables:
  DATABASE_URL: ********
  API_KEY:      ********
  LOG_LEVEL:    INFO

Trigger Configuration:
  Type:         HTTP
  URL:          https://us-central1-my-project.cloudfunctions.net/my-function
  Ingress:      ALLOW_ALL

VPC Configuration:
  VPC Connector: projects/my-project/locations/us-central1/connectors/my-connector
```

#### Download Function

Download function source code for local development:

```bash
# Download function code (uses configured provider)
spartan handler download --name my-function

# Download with specific provider
spartan handler download --name my-function --provider aws
spartan handler download --name my-function --provider gcp

# Specify output path
spartan handler download --name my-function --output ./downloads/my-function.zip

# Extract ZIP file after download
spartan handler download --name my-function --extract

# Verify download integrity
spartan handler download --name my-function --check-integrity

# Save function configuration
spartan handler download --name my-function --include-config

# All options combined
spartan handler download \
  --name my-function \
  --output ./downloads/my-function.zip \
  --extract \
  --check-integrity \
  --include-config

# GCP-specific: specify project and location
spartan handler download \
  --name my-function \
  --project-id my-project \
  --location us-central1 \
  --extract

# AWS-specific: specify version and region
spartan handler download \
  --name my-function \
  --version $LATEST \
  --region us-east-1 \
  --extract
```

**Output Example:**
```
Downloading function: my-function
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Function code downloaded
  File: my-function.zip
  Size: 2.4 MB

✓ Integrity check passed
  SHA256: a1b2c3d4e5f6...

✓ Code extracted
  Directory: my-function/
  Files: 15

✓ Configuration saved
  File: my-function-config.json
```

#### Delete Handler File

Delete a local handler file:

```bash
# Delete handler file
spartan handler delete my-handler

# The command is provider-agnostic (deletes local file only)
```

**Output Example:**
```
✓ Handler file deleted successfully
  File: handlers/my_handler.py
```

### Authentication Setup

#### AWS Authentication

Configure AWS credentials using one of these methods:

**Option 1: AWS CLI Configuration**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option 2: AWS Profile**
```bash
# Use a specific AWS profile
spartan handler list --profile my-profile
```

**Required AWS Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:ListFunctions",
        "lambda:GetFunction",
        "lambda:GetFunctionConfiguration",
        "lambda:InvokeFunction"
      ],
      "Resource": "*"
    }
  ]
}
```

#### GCP Authentication

Configure GCP credentials using one of these methods:

**Option 1: Application Default Credentials**
```bash
# Login with your user account
gcloud auth application-default login

# Or set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Option 2: Service Account Key**
```bash
# Download service account key from GCP Console
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Set project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Set location (optional, defaults to us-central1)
export GOOGLE_CLOUD_REGION=us-central1
```

**Required GCP Permissions:**
- `cloudfunctions.functions.list`
- `cloudfunctions.functions.get`
- `cloudfunctions.functions.sourceCodeGet`
- `cloudfunctions.functions.call`

**GCP IAM Role:**
```bash
# Grant Cloud Functions Developer role to service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/cloudfunctions.developer"
```

### Configuration Examples

#### AWS Configuration

```ini
# .spartan file for AWS
[default]
provider = aws
```

```bash
# Set AWS region (optional)
export AWS_DEFAULT_REGION=us-east-1

# Use specific AWS profile (optional)
export AWS_PROFILE=my-profile
```

#### GCP Configuration

```ini
# .spartan file for GCP
[default]
provider = gcp
```

```bash
# Set GCP project (required)
export GOOGLE_CLOUD_PROJECT=my-project-id

# Set GCP location (optional, defaults to us-central1)
export GOOGLE_CLOUD_REGION=us-central1

# Set service account credentials (if not using ADC)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Handler File Templates

Spartan provides pre-built templates for different trigger types:

#### GCP Templates

**HTTP Trigger (`--subscribe http`):**
```python
import functions_framework
from flask import Request

@functions_framework.http
def handler(request: Request):
    """HTTP Cloud Function entry point."""
    request_json = request.get_json(silent=True)

    # Your handler logic here

    return {'status': 'success', 'message': 'Hello from GCP'}
```

**Pub/Sub Trigger (`--subscribe pubsub`):**
```python
import base64
import functions_framework

@functions_framework.cloud_event
def handler(cloud_event):
    """Pub/Sub Cloud Function entry point."""
    message_data = base64.b64decode(
        cloud_event.data["message"]["data"]
    ).decode()

    # Your handler logic here
    print(f"Received message: {message_data}")
```

**Cloud Storage Trigger (`--subscribe storage`):**
```python
import functions_framework

@functions_framework.cloud_event
def handler(cloud_event):
    """Cloud Storage Cloud Function entry point."""
    data = cloud_event.data
    bucket = data["bucket"]
    name = data["name"]

    # Your handler logic here
    print(f"File {name} in bucket {bucket}")
```

#### AWS Templates

**SQS Trigger (`--subscribe sqs`):**
```python
def handler(event, context):
    """AWS Lambda SQS trigger handler."""
    for record in event['Records']:
        message_body = record['body']

        # Your handler logic here
        print(f"Processing message: {message_body}")

    return {'statusCode': 200, 'body': 'Success'}
```

**API Gateway Trigger (`--subscribe api`):**
```python
import json

def handler(event, context):
    """AWS Lambda API Gateway handler."""
    body = json.loads(event.get('body', '{}'))

    # Your handler logic here

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Hello from Lambda'})
    }
```

### Troubleshooting

#### Common Issues

**1. Credentials Not Configured**

**AWS Error:**
```
Error: AWS credentials not configured
Suggestion: Run 'aws configure' to set up your AWS credentials.
```

**Solution:**
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**GCP Error:**
```
Error: GCP credentials not configured
Suggestion: Run 'gcloud auth application-default login' or set GOOGLE_APPLICATION_CREDENTIALS.
```

**Solution:**
```bash
gcloud auth application-default login
# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

**2. Project ID Not Set (GCP)**

**Error:**
```
Error: GCP project ID not provided
Suggestion: Set GOOGLE_CLOUD_PROJECT environment variable or pass --project-id parameter.
```

**Solution:**
```bash
export GOOGLE_CLOUD_PROJECT=my-project-id
# Or pass as parameter
spartan handler list --project-id my-project-id
```

**3. Permission Denied**

**Error:**
```
Error: Permission denied: User lacks required permissions
```

**Solution:**
- **AWS**: Ensure your IAM user/role has the required Lambda permissions
- **GCP**: Ensure your service account has the Cloud Functions Developer role or equivalent permissions

**4. Function Not Found**

**Error:**
```
Error: Function 'my-function' not found
```

**Solution:**
- Verify the function name is correct
- Check you're using the correct provider (`--provider aws` or `--provider gcp`)
- Verify you're in the correct region/location
- List all functions to see available names: `spartan handler list`

**5. Invalid Trigger Type**

**Error:**
```
Error: Invalid trigger type 'invalid-trigger'
```

**Solution:**
- Check the list of valid triggers for your provider
- GCP: http, pubsub, storage, firestore, scheduler
- AWS: sqs, sns, s3, api, and many more

#### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set log level to debug
export SPARTAN_LOG_LEVEL=DEBUG

# Run command with verbose output
spartan handler list -v
```

#### Getting Help

```bash
# Show help for handler commands
spartan handler --help

# Show help for specific command
spartan handler create --help
spartan handler list --help
spartan handler describe --help
spartan handler download --help
```

### Advanced Usage

#### Automation Scripts

```bash
#!/bin/bash
# Example: Download all functions for backup

# Get list of functions
FUNCTIONS=$(spartan handler list --output json | jq -r '.[].name')

# Download each function
for func in $FUNCTIONS; do
  echo "Downloading $func..."
  spartan handler download \
    --name "$func" \
    --output "backups/${func}.zip" \
    --include-config \
    --check-integrity
done

echo "Backup complete!"
```

#### Multi-Provider Development

```bash
# Create handlers for both providers
cat > .spartan << EOF
[default]
provider = aws
EOF

spartan handler create aws-handler --subscribe sqs

cat > .spartan << EOF
[default]
provider = gcp
EOF

spartan handler create gcp-handler --subscribe pubsub

# List functions from both providers
spartan handler list --provider aws
spartan handler list --provider gcp
```

#### CI/CD Integration

```yaml
# GitHub Actions example
name: Deploy Handler
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install Spartan
        run: pip install python-spartan

      - name: Configure GCP
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
          GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT_ID }}
        run: |
          # List deployed functions
          spartan handler list

          # Download function for testing
          spartan handler download --name my-function --extract
```

### Migration Guide

#### Migrating from AWS Lambda to GCP Cloud Functions

1. **Update Configuration:**
   ```bash
   # Change provider in .spartan
   cat > .spartan << EOF
   [default]
   provider = gcp
   EOF
   ```

2. **Create GCP Handler:**
   ```bash
   # Create new handler with GCP template
   spartan handler create my-function --subscribe http
   ```

3. **Adapt Handler Code:**
   - Change from Lambda signature to Cloud Functions signature
   - Update event handling for GCP trigger types
   - Adjust environment variable access
   - Update dependencies in requirements.txt

4. **Test Locally:**
   ```bash
   # Use Functions Framework for local testing
   pip install functions-framework
   functions-framework --target=handler --debug
   ```

5. **Deploy:**
   ```bash
   # Deploy using gcloud CLI
   gcloud functions deploy my-function \
     --runtime python311 \
     --trigger-http \
     --entry-point handler \
     --source .
   ```

#### Migrating from GCP Cloud Functions to AWS Lambda

1. **Update Configuration:**
   ```bash
   # Change provider in .spartan
   cat > .spartan << EOF
   [default]
   provider = aws
   EOF
   ```

2. **Create AWS Handler:**
   ```bash
   # Create new handler with AWS template
   spartan handler create my-function --subscribe api
   ```

3. **Adapt Handler Code:**
   - Change from Cloud Functions signature to Lambda signature
   - Update event handling for AWS trigger types
   - Adjust environment variable access
   - Update dependencies in requirements.txt

4. **Test Locally:**
   ```bash
   # Use SAM CLI for local testing
   sam local invoke MyFunction
   ```

5. **Deploy:**
   ```bash
   # Deploy using AWS CLI or SAM
   sam deploy --guided
   ```

## 📋 Table of Contents

- [Configuration](#-configuration)
- [Workflow Commands](#-workflow-commands)
- [Handler Commands](#-handler-commands)
- [Development Setup](#-development-setup)
- [Available Commands](#-available-commands)
- [Code Quality Tools](#-code-quality-tools)
- [Testing](#-testing)
- [Multi-Environment Testing with Tox](#-multi-environment-testing-with-tox)
- [Documentation](#-documentation)
- [Configuration Details](#-configuration-details)
- [Development Workflow](#-development-workflow)
- [CI/CD Integration](#-cicd-integration)
- [Contributing](#-contributing)

## 🛠️ Development Setup

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Git (for version control)

### Initial Setup

```bash
# 1. Install dependencies
make dev-install

# 2. Setup pre-commit hooks (recommended)
make setup-hooks

# 3. Verify installation
make demo
```

### Environment Information

```bash
# Show environment details
make env-info

# Show dependency tree
make deps-tree

# Generate requirements.txt
make requirements
```

## 🎯 Available Commands

### Development Workflow

| Command            | Description                                 |
| ------------------ | ------------------------------------------- |
| `make dev-install` | Install package in development mode         |
| `make run`         | Run the CLI application                     |
| `make demo`        | Run demo commands to showcase functionality |

### Code Quality & Formatting

| Command             | Description                      |
| ------------------- | -------------------------------- |
| `make format`       | Format code with black and isort |
| `make lint`         | Run linting with flake8          |
| `make check-format` | Check formatting without changes |
| `make quality`      | Run all code quality checks      |

### Testing

| Command                                | Description                         |
| -------------------------------------- | ----------------------------------- |
| `make test`                            | Run tests with pytest               |
| `make test-cov`                        | Run tests with coverage             |
| `make test-fast`                       | Run tests without coverage (faster) |
| `make test-watch`                      | Run tests in watch mode             |
| `make test-specific FILE=test_file.py` | Run specific test file              |

### Tox Multi-Environment Testing

| Command               | Description                   |
| --------------------- | ----------------------------- |
| `make tox`            | Run all tox environments      |
| `make tox-format`     | Format code via tox           |
| `make tox-lint`       | Run linting via tox           |
| `make tox-security`   | Run security checks via tox   |
| `make tox-type-check` | Run type checking via tox     |
| `make tox-docs`       | Build documentation via tox   |
| `make tox-coverage`   | Run coverage analysis via tox |
| `make tox-clean`      | Clean tox environments        |
| `make tox-list`       | List all tox environments     |

### Security & Audit

| Command         | Description                            |
| --------------- | -------------------------------------- |
| `make security` | Run security checks                    |
| `make audit`    | Audit dependencies for vulnerabilities |

### Build & Install

| Command              | Description             |
| -------------------- | ----------------------- |
| `make install-local` | Install package locally |

### Git & CI/CD

| Command               | Description                       |
| --------------------- | --------------------------------- |
| `make pre-commit`     | Run pre-commit checks             |
| `make pre-commit-run` | Run pre-commit hooks on all files |
| `make setup-hooks`    | Setup git pre-commit hooks        |
| `make ci`             | Run full CI pipeline              |
| `make ci-fast`        | Run fast CI pipeline              |

### Cleanup

| Command          | Description                                    |
| ---------------- | ---------------------------------------------- |
| `make clean`     | Clean build artifacts                          |
| `make clean-all` | Clean everything including virtual environment |

### Documentation

| Command           | Description                   |
| ----------------- | ----------------------------- |
| `make docs`       | Build Sphinx documentation    |
| `make docs-serve` | Serve documentation locally   |
| `make docs-clean` | Clean generated documentation |

### Utility & Info

| Command           | Description                   |
| ----------------- | ----------------------------- |
| `make size`       | Show project size information |
| `make list-todos` | List TODO items in code       |
| `make help`       | Show all available commands   |

## 🔧 Code Quality Tools

The project uses comprehensive code quality tools configured in `pyproject.toml`:

### Code Formatting

- **Black**: Code formatting (88 character line length, Python 3.11 target)
- **isort**: Import sorting (black-compatible profile)

### Linting & Type Checking

- **Flake8**: Style guide enforcement with plugins:
  - `flake8-docstrings`: Documentation style
  - `flake8-bugbear`: Bug detection
  - `flake8-comprehensions`: Comprehension improvements
- **MyPy**: Static type checking (lenient settings for gradual adoption)

### Security & Documentation

- **Bandit**: Security vulnerability scanning (practical exclusions for development)
- **pydocstyle**: Documentation style (Google convention, lenient for gradual adoption)

### Tool Configuration

All tools are configured consistently in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
known_first_party = ["spartan"]

[tool.mypy]
# Lenient settings for gradual adoption
ignore_missing_imports = true
disallow_untyped_defs = false

[tool.bandit]
# Security checks with practical exclusions
exclude_dirs = ["tests", "docs"]
skips = ["B101", "B110", "B311", "B324", "B404", "B603", "B607"]

[tool.pydocstyle]
convention = "google"
# Missing docstrings allowed for gradual adoption
add-ignore = ["D100", "D101", "D102", "D103", "D104", "D105", "D107"]
```

## 🧪 Testing

### Test Directory Structure

Tests are organized into two main categories for better maintainability and targeted test execution:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures for all tests
├── unit/                # Unit tests
│   ├── __init__.py
│   └── test_*.py        # Individual component tests
└── integration/         # Integration tests
    ├── __init__.py
    └── test_*.py        # Multi-component and CLI tests
```

### Unit Tests vs Integration Tests

**Unit Tests** (`tests/unit/`)
- Test individual components in isolation
- Mock external dependencies (file system, network, databases)
- Execute quickly (milliseconds)
- Focus on specific methods and functions
- Example: Testing a single service class with mocked dependencies

**Integration Tests** (`tests/integration/`)
- Test interactions between multiple components
- Test CLI initialization and command execution
- Test end-to-end workflows
- May use real file system operations (in temp directories)
- Example: Testing CLI command execution with real config files

### Running Tests by Category

```bash
# Run all tests
make test-fast

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run specific test file
pytest tests/unit/test_config_service.py

# Run with verbose output
pytest tests/unit -v

# Run with coverage
make test-cov

# Run unit tests with coverage
pytest tests/unit --cov=spartan --cov-report=term-missing
```

### Test Configuration

Tests are configured in `pyproject.toml` with pytest:

```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

### Coverage Configuration

Coverage is configured to focus on source code:

```toml
[tool.coverage.run]
source = ["spartan"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
]
```

### Running Tests

```bash
# Quick test run (all tests)
make test-fast

# Full tests with coverage
make test-cov

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Specific test file
make test-specific FILE=test_example.py

# Watch mode for development
make test-watch

# Run with verbose output
pytest -v

# Run unit tests with coverage
pytest tests/unit --cov=spartan --cov-report=html
```

### Writing New Tests

When creating a new test, place it in the appropriate directory:

**Place in `tests/unit/` if:**
- Testing a single component/class in isolation
- Mocking all external dependencies
- Testing utility functions or helper methods
- Testing data models and validation logic

**Place in `tests/integration/` if:**
- Testing CLI command execution
- Testing interactions between multiple services
- Testing file system operations with real files
- Testing configuration loading and initialization
- Testing end-to-end workflows

For more details on testing guidelines, see `.kiro/steering/testing-guidelines.md`.

## 🏗️ Multi-Environment Testing with Tox

Tox provides isolated testing environments for comprehensive validation:

### Available Tox Environments

```bash
# List all environments
make tox-list
```

**Testing Environments:**

- `py311`, `py312`, `py313` - Python version testing
- `lint` - Flake8 linting with all plugins
- `format` - Black and isort formatting
- `format-check` - Check formatting without changes
- `security` - Bandit security scanning
- `type-check` - MyPy static type checking
- `coverage` - Test coverage reporting
- `docs` - Sphinx documentation building
- `pre-commit` - Run all pre-commit hooks
- `clean` - Clean build artifacts

### Directory Exclusions

All tox environments properly exclude build and virtual environment directories:

- `.venv`, `.tox`, `.git`
- `__pycache__`, `build`, `dist`
- `.eggs`, `*.egg-info`

### Tox Usage Examples

```bash
# Run all environments
make tox

# Run specific environment
poetry run tox -e lint

# Run linting with proper exclusions
make tox-lint

# Check code formatting
make tox-format-check

# Run security scanning
make tox-security
```

## 📚 Documentation

### Building Documentation

The project uses Sphinx for documentation generation:

```bash
# Build documentation
make docs

# Serve documentation locally (http://localhost:8000)
make docs-serve

# Clean documentation
make docs-clean

# Build via tox (isolated environment)
make tox-docs
```

### Documentation Dependencies

```toml
# Documentation tools in pyproject.toml
sphinx = "^8.1.3"
sphinx-rtd-theme = "^3.0.2"
sphinx-autoapi = "^3.3.3"
myst-parser = "^4.0.0"
```

## ⚙️ Configuration Details

### Project Structure

```
spartan/
├── spartan/           # Main package
│   ├── __init__.py
│   ├── main.py        # CLI entry point
│   └── services/      # Service modules
├── tests/             # Test suite
├── docs/              # Sphinx documentation
├── pyproject.toml     # Main configuration
├── tox.ini           # Multi-environment testing
├── Makefile          # Development commands
└── README.md         # This file
```

### Dependencies

**Core Dependencies:**

- `typer`: CLI framework
- `rich`: Rich terminal output
- `boto3`: AWS SDK
- `pandas`: Data manipulation
- `pyarrow`: Parquet support

**Development Dependencies:**

- Testing: `pytest`, `pytest-cov`, `pytest-mock`, `faker`
- Code Quality: `black`, `isort`, `flake8`, `mypy`, `bandit`
- Documentation: `sphinx`, `sphinx-rtd-theme`
- Tools: `pre-commit`, `commitizen`, `tox`

### Configuration Files Alignment

All configuration files are aligned for consistency:

| Tool           | Configuration File | Settings Source             |
| -------------- | ------------------ | --------------------------- |
| **Black**      | `pyproject.toml`   | `[tool.black]`              |
| **isort**      | `pyproject.toml`   | `[tool.isort]`              |
| **Flake8**     | `pyproject.toml`   | Via tox/make commands       |
| **MyPy**       | `pyproject.toml`   | `[tool.mypy]`               |
| **Bandit**     | `pyproject.toml`   | `[tool.bandit]`             |
| **Pytest**     | `pyproject.toml`   | `[tool.pytest.ini_options]` |
| **Coverage**   | `pyproject.toml`   | `[tool.coverage.*]`         |
| **Commitizen** | `pyproject.toml`   | `[tool.commitizen]`         |

## 🔄 Development Workflow

### Daily Development

1. **Initial Setup** (first time):

   ```bash
   make dev-install
   make setup-hooks
   ```

2. **Code Development**:
   - Write code in `spartan/`
   - Write tests in `tests/`
   - Pre-commit hooks run automatically on commit

3. **Manual Quality Checks**:

   ```bash
   # Quick quality check
   make quality

   # Run tests
   make test-fast

   # Full quality + tests
   make pre-commit
   ```

4. **Multi-Environment Validation**:

   ```bash
   # Test across Python versions
   make tox

   # Specific environment testing
   make tox-lint
   make tox-security
   ```

### Command Equivalence

You can achieve the same results through different paths:

```bash
# Direct via Poetry
poetry run black spartan tests
poetry run flake8 spartan tests
poetry run mypy spartan

# Via tox (isolated environment)
poetry run tox -e format
poetry run tox -e lint
poetry run tox -e type-check

# Via make (convenient aliases)
make format
make lint
make tox-type-check
```

## 🚀 CI/CD Integration

### CI Pipeline Options

```bash
# Fast CI pipeline (for PRs)
make ci-fast
# Includes: dev-install + quality + test-fast

# Full CI pipeline (for main branch)
make ci
# Includes: dev-install + quality + test-cov

# Comprehensive testing (for releases)
make tox
# Tests across Python 3.11, 3.12, 3.13
```

### Pre-commit Integration

All quality tools are integrated into pre-commit hooks:

```bash
# Setup hooks (run once)
make setup-hooks

# Manual run of all hooks
make pre-commit-run

# Hooks run automatically on commit
git commit -m "Your commit message"
```

### Benefits of the Setup

✅ **Consistency**: All tools use the same configuration
✅ **Flexibility**: Run tools via Poetry, tox, or make
✅ **Isolation**: Tox provides clean environments
✅ **CI Integration**: Multiple testing strategies
✅ **Developer Experience**: Simple, memorable commands
✅ **Gradual Adoption**: Lenient settings for incremental improvement

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Set up development environment**: `make dev-install && make setup-hooks`
4. **Make your changes** with tests
5. **Run quality checks**: `make quality`
6. **Run tests**: `make test-cov`
7. **Optional: Run tox for comprehensive testing**: `make tox`
8. **Commit your changes** (pre-commit hooks will run automatically)
9. **Push to your fork**: `git push origin feature-name`
10. **Create a Pull Request**

### Code Quality Requirements

- All code must pass `make quality` (formatting + linting)
- All tests must pass `make test-cov`
- Coverage should be maintained or improved
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### Optional but Recommended

- Run `make tox` for multi-environment testing
- Check security with `make tox-security`
- Validate types with `make tox-type-check`

---

**Note**: This project follows a comprehensive development workflow with multiple layers of quality assurance. The configuration is designed to be both strict enough to ensure quality and flexible enough to support gradual adoption of best practices.
