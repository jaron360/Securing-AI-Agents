# Cybersecurity News Summarization Agent

An AI-powered agent built with **AWS Strands SDK** that monitors the internet for cybersecurity incidents, breaches, and vulnerabilities in the past 24 hours.

## Features

The agent checks multiple sources:
- **Hacker News** - Trending security stories and discussions
- **Reddit** - r/cybersecurity, r/netsec, r/security communities
- **NVD (National Vulnerability Database)** - Newly published CVEs
- **Security News Sites** - Bleeping Computer, The Hacker News RSS feeds

## Why AWS Strands SDK?

This agent is built with AWS Strands Agents SDK, Amazon's open-source framework for building AI agents:

- **Minimal code** - ~170 lines vs 250+ with LangChain
- **AWS-native** - Built specifically for AWS Bedrock
- **Model-driven** - LLM handles planning and tool selection
- **Simple API** - Just define model, system prompt, and tools
- **Production-ready** - Used by AWS customers in production

## How It Works

```
User Question
    ↓
Strands Agent (Claude 3.5 Haiku)
    ↓
Agentic Loop (automatic)
    ├─→ Model decides which tools to use
    ├─→ Executes tools (web scraping, API calls)
    ├─→ Processes results
    └─→ Repeats until answer is complete
    ↓
Conversational Response
```

## Architecture

```python
from strands import Agent

agent = Agent(
    model="anthropic.claude-3-5-haiku-20241022-v1:0",
    system_prompt="You are a cybersecurity analyst...",
    tools=[check_hacker_news, check_reddit, check_cve, check_news]
)

response = agent("What's the security news today?")
```

That's it! Strands handles the agentic loop automatically.

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

### Run the Agent

```bash
# Activate virtual environment
source venv/bin/activate

# Run the agent (standalone)
python agent_strands.py

# Or run via the chat wrapper
python simple_chat_strands.py
```

### Example Conversation

```
🔒 Security Incident Detection Agent (AWS Strands SDK)
================================================================================

💬 You: What's the security news for today?

🤖 Agent: Checking sources...

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
```

## Configuration

### Model Settings

Located in `agent_strands.py`:

```python
agent = Agent(
    model="anthropic.claude-3-5-haiku-20241022-v1:0",  # Model ID
    system_prompt="...",  # Agent instructions
    tools=[...]  # Available tools
)
```

### Change the Model

```python
# Use Claude 3 Haiku (older, but works)
model="anthropic.claude-3-haiku-20240307-v1:0"

# Use Claude 3.5 Haiku (current)
model="anthropic.claude-3-5-haiku-20241022-v1:0"
```

### Adjust Time Window

In each tool function:
```python
# From 24 hours to 12 hours
if datetime.now() - created < timedelta(hours=12):
```

### Add Custom Tools

```python
def check_custom_source():
    """Your custom security source"""
    # Implementation
    return json.dumps(results)

# Add to agent
agent = Agent(
    model="...",
    system_prompt="...",
    tools=[
        check_hacker_news,
        check_reddit_security,
        check_cve_recent,
        check_security_news_sites,
        check_custom_source  # Your new tool
    ]
)
```



## Strands SDK vs LangChain Comparison

| Feature | Strands SDK | LangChain + LangGraph |
|---------|-------------|----------------------|
| Lines of code | ~170 | ~250 |
| Dependencies | 1 (strands-agents) | 3 (langchain, langchain-aws, langchain-community) |
| Agent creation | `Agent(model, system_prompt, tools)` | `create_react_agent(llm, tools, prompt)` |
| Invocation | `agent(input)` | `agent_executor.invoke({"messages": [...]})` |
| AWS integration | Native | Via langchain-aws |
| Agentic loop | Automatic | Manual configuration |

## Security Considerations

### Built-in Protections

1. **Claude's Constitutional AI** - Inherent resistance to prompt injection
2. **Tool-calling architecture** - Agent can only use predefined, read-only tools
3. **Limited scope** - Tools only perform web scraping, no file system or database access
4. **Strands SDK safety** - Built-in guardrails and observability

### Known Limitations

1. **Output echoing** - Agent may repeat sensitive data from user input
2. **Resource exhaustion** - No built-in rate limiting
3. **Indirect injection** - Malicious content from scraped sources could influence behavior
4. **Security Features** - No input validation or santization included apart from source LLM defaults


## Resources

- [AWS Strands Agents SDK Documentation](https://strandsagents.com/)
- [AWS Blog: Introducing Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents/)
- [Strands GitHub Repository](https://github.com/awslabs/strands)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
