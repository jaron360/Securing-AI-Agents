# Cybersecurity Incident Detection Agent

An AI-powered agent that monitors the internet for cybersecurity incidents, breaches, and vulnerabilities in the past 24 hours.

## Features

The agent checks multiple sources:
- **Hacker News** - Trending security stories and discussions
- **Reddit** - r/cybersecurity, r/netsec, r/security communities
- **NVD (National Vulnerability Database)** - Newly published CVEs
- **Security News Sites** - Bleeping Computer, The Hacker News RSS feeds

## How It Works

Uses AWS Bedrock (Claude 3.5 Haiku) with LangGraph to:
1. Query multiple security information sources
2. Filter for incidents from the past 24 hours
3. Analyze and summarize findings intelligently
4. Provide conversational responses to your questions

## Architecture

```
User Questions 
    ↓
LangGraph Agent (Claude 3.5 Haiku)
    ↓
Tool Selection & Execution
    ├─→ CheckHackerNews (web scraping)
    ├─→ CheckReddit (Reddit API)
    ├─→ CheckCVE (NVD API)
    └─→ CheckSecurityNews (RSS feeds)
    ↓
AI Analysis & Summary
    ↓
Conversational Response
```

## Setup

### Prerequisites
- Python 3.11+ (tested with Python 3.14)
- AWS account with Bedrock access
- AWS credentials configured

### Installation

```bash
cd security-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### AWS Configuration

```bash
# Option 1: AWS Profile
export AWS_PROFILE=your-profile

# Option 2: Access Keys
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_DEFAULT_REGION=us-west-2
```

### Enable Bedrock Model Access

1. Go to AWS Console → Bedrock → Model access
2. Request access to: `Claude 3.5 Haiku`
3. Wait for approval (usually instant)

You can check available models:
```bash
aws bedrock list-foundation-models --region us-west-2 --query 'modelSummaries[?contains(modelId, `claude`)].modelId'
```

## Usage

### Interactive Chat Mode (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the chat interface
python simple_chat.py
```

Then ask questions like:
- "What's the security news for today?"
- "Are there any new vulnerabilities?"
- "What incidents happened in the past 24 hours?"
- "Show me the latest CVEs"
- "What's trending on Hacker News about security?"

### Example Conversation

```
🔒 Security Incident Detection Agent
================================================================================

💬 You: What's the security news for today?

🤖 Agent: Let me check the latest sources for you...

📊 Based on the search results, here are some recent cybersecurity-related discussions:

HACKER NEWS HIGHLIGHTS:
- Discussion about AI security and prompt injection challenges
- New OSINT tool release for forensic analysis

REDDIT SECURITY COMMUNITIES:
- PHP 8 disable_functions bypass PoC discussion
- Container image security best practices

CVE VULNERABILITIES (Past 24 hours):
- CVE-2024-XXXXX: Critical RCE in Apache component (CVSS 9.8)
- CVE-2024-XXXXY: High severity authentication bypass (CVSS 8.1)

SECURITY NEWS:
- Bleeping Computer: New ransomware variant targeting healthcare
- The Hacker News: Supply chain attack on popular npm package

Would you like me to elaborate on any of these topics?

💬 You: Tell me more about the Apache vulnerability

🤖 Agent: Let me get more details...
```

## Configuration

### Model Settings

Located in `agent.py`:

```python
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-haiku-20241022-v1:0",  # Claude 3.5 Haiku
    region_name="us-west-2",
    model_kwargs={
        "temperature": 0.1,      # Low = more focused responses
        "max_tokens": 4096       # Maximum response length
    }
)
```

### Available Tools

The agent has access to these tools (defined in `agent.py`):

1. **CheckHackerNews** - Scrapes Hacker News for security keywords
2. **CheckReddit** - Queries Reddit security subreddits via API
3. **CheckCVE** - Fetches recent CVEs from NVD API
4. **CheckSecurityNews** - Parses RSS feeds from security news sites

### Customization

**Change the model:**
```python
# Use Claude 3 Haiku (faster, cheaper)
model_id="anthropic.claude-3-haiku-20240307-v1:0"

# Use Claude 3.7 Sonnet (more capable, requires inference profile)
model_id="anthropic.claude-3-7-sonnet-20250219-v1:0"
```

**Adjust time window:**
```python
# In each tool function, change:
if datetime.now() - created < timedelta(days=1):  # 24 hours
# To:
if datetime.now() - created < timedelta(hours=12):  # 12 hours
```

**Add more sources:**
```python
def check_custom_source(query=""):
    """Your custom security source"""
    # Implementation
    return json.dumps(results)

# Add to tools list
tools.append(Tool(
    name="CheckCustomSource",
    func=check_custom_source,
    description="Description for the agent"
))
```

### Deploy to Lambda

```bash
# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package
zip -r function.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc"

# Create Lambda function
aws lambda create-function \
  --function-name security-incident-agent \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --timeout 300 \
  --memory-size 512
```

### Schedule with EventBridge

```bash
# Create rule to run daily at 8 AM UTC
aws events put-rule \
  --name daily-security-check \
  --schedule-expression "cron(0 8 * * ? *)"

# Add Lambda as target
aws events put-targets \
  --rule daily-security-check \
  --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:security-incident-agent"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
  --function-name security-incident-agent \
  --statement-id AllowEventBridge \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:REGION:ACCOUNT:rule/daily-security-check
```

## Sample Output

```
SECURITY INCIDENT REPORT
================================================================================

Analysis Period: Past 24 hours

HACKER NEWS HIGHLIGHTS:
- Major data breach at XYZ Corp affecting 10M users
- New zero-day vulnerability in popular web framework
- Ransomware attack on healthcare provider

REDDIT DISCUSSIONS:
- Active discussion on recent supply chain attack
- New phishing campaign targeting developers

CVE VULNERABILITIES:
- CVE-2024-XXXXX: Critical RCE in Apache component (CVSS 9.8)
- CVE-2024-XXXXY: High severity SQL injection (CVSS 8.1)

SECURITY NEWS:
- Bleeping Computer: Nation-state APT group targets financial sector
- The Hacker News: New malware strain discovered in the wild

SUMMARY:
Critical incidents detected in the past 24 hours. Immediate attention required
for CVE-2024-XXXXX. Monitor ongoing discussions about supply chain attacks.
```

## Security Considerations

### Built-in Protections

1. **Claude's Constitutional AI** - Inherent resistance to prompt injection
2. **Tool-calling architecture** - Agent can only use predefined, read-only tools
3. **Limited scope** - Tools only perform web scraping, no file system or database access

### Known Limitations

1. **Output echoing** - Agent may repeat sensitive data from user input
2. **Resource exhaustion** - No built-in rate limiting
3. **Indirect injection** - Malicious content from scraped sources could influence behavior

### Security Enhancements Available

A `security_layer.py` module is included with:
- Input validation and sanitization
- Output redaction (API keys, credentials)
- Prompt injection detection
- Rate limiting framework

To integrate security layer, see the implementation guide in the file.

### Recommended for Production

1. **Add AWS Bedrock Guardrails** for content filtering
2. **Implement rate limiting** (per user/IP)
3. **Enable CloudWatch logging** for audit trails
4. **Deploy in VPC** with private subnets
5. **Use API Gateway** with authentication
6. **Add WAF rules** to block malicious requests

## File Structure

```
security-agent/
├── agent.py              # Main agent logic and configuration
├── simple_chat.py        # Interactive chat interface
├── security_layer.py     # Security guardrails (optional)
├── lambda_handler.py     # AWS Lambda wrapper
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── terraform/           # Infrastructure as Code
    ├── main.tf          # Terraform configuration
    └── variables.tf     # Terraform variables
```

## Deploy to AWS Lambda

### Package the Function

```bash
# Install dependencies in current directory
pip install -r requirements.txt -t .

# Create deployment package
zip -r function.zip . -x "*.git*" -x "*__pycache__*" -x "*.pyc" -x "venv/*" -x "terraform/*"
```

### Create Lambda Function

```bash
aws lambda create-function \
  --function-name security-incident-agent \
  --runtime python3.11 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables={SNS_TOPIC_ARN=arn:aws:sns:REGION:ACCOUNT:security-incidents}
```

### IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:security-incidents"
    }
  ]
}
```
