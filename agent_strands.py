"""
Security Incident Detection Agent
Uses AWS Bedrock with LangChain to check for cyber attacks/incidents from public sources
"""
import boto3
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from langchain_aws import ChatBedrock
from langchain_core.tools import Tool

# Initialize Bedrock LLM
llm = ChatBedrock(
    model_id="anthropic.claude-3-5-haiku-20241022-v1:0",  # Claude 3.5 Haiku
    region_name="us-west-2",
    model_kwargs={
        "temperature": 0.1,
        "max_tokens": 4096"""
Security Incident Detection Agent - Built with AWS Strands SDK
Monitors internet sources for cybersecurity incidents in the past 24 hours
"""
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from strands import Agent

# Tool functions remain the same but simplified
def check_hacker_news():
    """Scrape Hacker News for cybersecurity incidents in the past 24 hours"""
    try:
        incidents = []
        urls = ['https://news.ycombinator.com/', 'https://news.ycombinator.com/newest']
        
        security_keywords = [
            'breach', 'hack', 'vulnerability', 'exploit', 'ransomware',
            'malware', 'attack', 'security', 'CVE', 'zero-day',
            'data leak', 'compromise', 'phishing', 'ddos'
        ]
        
        for url in urls:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            stories = soup.find_all('span', class_='titleline')
            
            for story in stories[:30]:
                link = story.find('a')
                if link:
                    title = link.get_text().lower()
                    if any(keyword in title for keyword in security_keywords):
                        incidents.append({
                            'title': link.get_text(),
                            'url': link.get('href'),
                            'source': 'Hacker News'
                        })
        
        if not incidents:
            return "No cybersecurity incidents found on Hacker News"
        
        return json.dumps(incidents[:10], indent=2)
    
    except Exception as e:
        return f"Error checking Hacker News: {str(e)}"


def check_reddit_security():
    """Check Reddit r/cybersecurity and r/netsec for recent incidents"""
    try:
        incidents = []
        subreddits = ['cybersecurity', 'netsec', 'security']
        
        for subreddit in subreddits:
            url = f'https://www.reddit.com/r/{subreddit}/new.json'
            headers = {'User-Agent': 'SecurityBot/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            for post in data['data']['children'][:20]:
                post_data = post['data']
                created = datetime.fromtimestamp(post_data['created_utc'])
                
                if datetime.now() - created < timedelta(days=1):
                    incidents.append({
                        'title': post_data['title'],
                        'url': f"https://reddit.com{post_data['permalink']}",
                        'subreddit': subreddit,
                        'score': post_data['score'],
                        'time': created.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        if not incidents:
            return "No recent cybersecurity posts on Reddit"
        
        incidents.sort(key=lambda x: x['score'], reverse=True)
        return json.dumps(incidents[:10], indent=2)
    
    except Exception as e:
        return f"Error checking Reddit: {str(e)}"


def check_cve_recent():
    """Check recent CVE vulnerabilities from NVD"""
    try:
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000')
        
        params = {
            'pubStartDate': yesterday,
            'resultsPerPage': 20
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'vulnerabilities' not in data or not data['vulnerabilities']:
            return "No new CVEs published in the past 24 hours"
        
        cves = []
        for vuln in data['vulnerabilities'][:10]:
            cve_data = vuln['cve']
            cves.append({
                'cve_id': cve_data['id'],
                'description': cve_data['descriptions'][0]['value'][:200],
                'published': cve_data['published'],
                'severity': cve_data.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseSeverity', 'Unknown')
            })
        
        return json.dumps(cves, indent=2)
    
    except Exception as e:
        return f"Error checking CVE database: {str(e)}"


def check_security_news_sites():
    """Check major security news sites for recent incidents"""
    try:
        incidents = []
        
        # Check Bleeping Computer RSS
        try:
            response = requests.get('https://www.bleepingcomputer.com/feed/', timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:10]
            
            for item in items:
                pub_date = datetime.strptime(item.pubDate.text, '%a, %d %b %Y %H:%M:%S %z')
                if datetime.now(pub_date.tzinfo) - pub_date < timedelta(days=1):
                    incidents.append({
                        'title': item.title.text,
                        'url': item.link.text,
                        'source': 'Bleeping Computer',
                        'published': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        except:
            pass
        
        # Check The Hacker News RSS
        try:
            response = requests.get('https://feeds.feedburner.com/TheHackersNews', timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:10]
            
            for item in items:
                pub_date = datetime.strptime(item.pubDate.text, '%a, %d %b %Y %H:%M:%S %Z')
                if datetime.now() - pub_date.replace(tzinfo=None) < timedelta(days=1):
                    incidents.append({
                        'title': item.title.text,
                        'url': item.link.text,
                        'source': 'The Hacker News',
                        'published': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        except:
            pass
        
        if not incidents:
            return "No recent security news articles found"
        
        return json.dumps(incidents[:15], indent=2)
    
    except Exception as e:
        return f"Error checking security news sites: {str(e)}"


# Create the agent with Strands SDK
agent = Agent(
    model="anthropic.claude-3-5-haiku-20241022-v1:0",  # Remove "bedrock/" prefix
    system_prompt="""You are a cybersecurity news analyst AI agent. Your job is to help users 
    stay informed about the latest cybersecurity incidents, breaches, and vulnerabilities.
    
    When a user asks about security news or incidents:
    1. Use your available tools to check relevant sources
    2. Summarize the most important findings
    3. Provide context and severity information
    4. Be conversational and helpful
    
    Always focus on incidents from the past 24 hours.""",
    tools=[
        check_hacker_news,
        check_reddit_security,
        check_cve_recent,
        check_security_news_sites
    ]
)


def chat():
    """Interactive chat with the security agent"""
    print("=" * 80)
    print("🔒 Security Incident Detection Agent (Strands SDK)")
    print("=" * 80)
    print("\nAsk me about today's cybersecurity news and incidents!")
    print("\nExamples:")
    print("  • What's the security news for today?")
    print("  • Are there any new vulnerabilities?")
    print("  • What incidents happened in the past 24 hours?")
    print("  • Show me the latest CVEs")
    print("\nType 'exit' or 'quit' to stop.\n")
    print("=" * 80)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent: Checking sources...\n")
            
            # Run the agent
            response = agent(user_input)
            
            print(f"📊 {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    chat()

    }
)

def check_hacker_news(query=""):
    """Scrape Hacker News for cybersecurity incidents in the past 24 hours"""
    try:
        incidents = []
        
        # Check Hacker News front page and new stories
        urls = [
            'https://news.ycombinator.com/',
            'https://news.ycombinator.com/newest'
        ]
        
        security_keywords = [
            'breach', 'hack', 'vulnerability', 'exploit', 'ransomware',
            'malware', 'attack', 'security', 'CVE', 'zero-day',
            'data leak', 'compromise', 'phishing', 'ddos'
        ]
        
        for url in urls:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all story titles
            stories = soup.find_all('span', class_='titleline')
            
            for story in stories[:30]:  # Check top 30 stories
                link = story.find('a')
                if link:
                    title = link.get_text().lower()
                    
                    # Check if title contains security keywords
                    if any(keyword in title for keyword in security_keywords):
                        incidents.append({
                            'title': link.get_text(),
                            'url': link.get('href'),
                            'source': 'Hacker News'
                        })
        
        if not incidents:
            return "No cybersecurity incidents found on Hacker News"
        
        return json.dumps(incidents[:10], indent=2)  # Return top 10
    
    except Exception as e:
        return f"Error checking Hacker News: {str(e)}"

def check_reddit_security(query=""):
    """Check Reddit r/cybersecurity and r/netsec for recent incidents"""
    try:
        incidents = []
        
        subreddits = ['cybersecurity', 'netsec', 'security']
        
        for subreddit in subreddits:
            url = f'https://www.reddit.com/r/{subreddit}/new.json'
            headers = {'User-Agent': 'SecurityBot/1.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            for post in data['data']['children'][:20]:
                post_data = post['data']
                created = datetime.fromtimestamp(post_data['created_utc'])
                
                # Only get posts from last 24 hours
                if datetime.now() - created < timedelta(days=1):
                    incidents.append({
                        'title': post_data['title'],
                        'url': f"https://reddit.com{post_data['permalink']}",
                        'subreddit': subreddit,
                        'score': post_data['score'],
                        'time': created.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        if not incidents:
            return "No recent cybersecurity posts on Reddit"
        
        # Sort by score
        incidents.sort(key=lambda x: x['score'], reverse=True)
        
        return json.dumps(incidents[:10], indent=2)
    
    except Exception as e:
        return f"Error checking Reddit: {str(e)}"

def check_cve_recent(query=""):
    """Check recent CVE vulnerabilities from NVD"""
    try:
        # NVD API endpoint
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
        # Get CVEs from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.000')
        
        params = {
            'pubStartDate': yesterday,
            'resultsPerPage': 20
        }
        
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if 'vulnerabilities' not in data or not data['vulnerabilities']:
            return "No new CVEs published in the past 24 hours"
        
        cves = []
        for vuln in data['vulnerabilities'][:10]:
            cve_data = vuln['cve']
            cves.append({
                'cve_id': cve_data['id'],
                'description': cve_data['descriptions'][0]['value'][:200],
                'published': cve_data['published'],
                'severity': cve_data.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseSeverity', 'Unknown')
            })
        
        return json.dumps(cves, indent=2)
    
    except Exception as e:
        return f"Error checking CVE database: {str(e)}"

def check_security_news_sites(query=""):
    """Check major security news sites for recent incidents"""
    try:
        incidents = []
        
        # Check Bleeping Computer RSS
        try:
            response = requests.get('https://www.bleepingcomputer.com/feed/', timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')[:10]
            for item in items:
                pub_date = datetime.strptime(item.pubDate.text, '%a, %d %b %Y %H:%M:%S %z')
                
                if datetime.now(pub_date.tzinfo) - pub_date < timedelta(days=1):
                    incidents.append({
                        'title': item.title.text,
                        'url': item.link.text,
                        'source': 'Bleeping Computer',
                        'published': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        except:
            pass
        
        # Check The Hacker News RSS
        try:
            response = requests.get('https://feeds.feedburner.com/TheHackersNews', timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')[:10]
            for item in items:
                pub_date = datetime.strptime(item.pubDate.text, '%a, %d %b %Y %H:%M:%S %Z')
                
                if datetime.now() - pub_date.replace(tzinfo=None) < timedelta(days=1):
                    incidents.append({
                        'title': item.title.text,
                        'url': item.link.text,
                        'source': 'The Hacker News',
                        'published': pub_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        except:
            pass
        
        if not incidents:
            return "No recent security news articles found"
        
        return json.dumps(incidents[:15], indent=2)
    
    except Exception as e:
        return f"Error checking security news sites: {str(e)}"

def generate_incident_summary(findings_data):
    """Generate a comprehensive incident summary"""
    summary = f"""
    Security Incident Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Analysis Period: Past 24 hours
    
    {findings_data}
    
    Recommendation: Review all high/critical findings immediately.
    """
    return summary

# Define tools for the agent
tools = [
    Tool(
        name="CheckHackerNews",
        func=check_hacker_news,
        description="Check Hacker News for cybersecurity incidents, breaches, and vulnerabilities discussed in the past 24 hours. Use this to find trending security stories."
    ),
    Tool(
        name="CheckReddit",
        func=check_reddit_security,
        description="Check Reddit cybersecurity communities (r/cybersecurity, r/netsec, r/security) for recent security incidents and discussions in the past 24 hours."
    ),
    Tool(
        name="CheckCVE",
        func=check_cve_recent,
        description="Check the National Vulnerability Database (NVD) for newly published CVE vulnerabilities in the past 24 hours. Use this to find the latest security vulnerabilities."
    ),
    Tool(
        name="CheckSecurityNews",
        func=check_security_news_sites,
        description="Check major security news sites (Bleeping Computer, The Hacker News) for recent cybersecurity incidents and news articles in the past 24 hours."
    )
]

# Create agent using LangGraph
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, tools)

def run_security_check():
    """Run the security incident check"""
    query = """
    Check all available sources for cybersecurity incidents and attacks in the past 24 hours.
    Provide a comprehensive report including:
    1. Trending security stories on Hacker News
    2. Recent discussions on Reddit security communities
    3. Newly published CVE vulnerabilities
    4. Latest security news articles
    
    Summarize the most critical incidents, their severity, and potential impact.
    """
    
    result = agent_executor.invoke({"input": query})
    return result['output']

def chat_with_agent():
    """Interactive chat with the security agent"""
    print("=" * 80)
    print("Security Incident Detection Agent")
    print("=" * 80)
    print("\nAsk me about today's cybersecurity news and incidents!")
    print("Examples:")
    print("  - What's the security news for today?")
    print("  - Are there any new vulnerabilities?")
    print("  - What incidents happened in the past 24 hours?")
    print("  - Show me the latest CVEs")
    print("\nType 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nGoodbye!")
                break
            
            if not user_input:
                continue
            
            print("\nAgent: Checking sources...")
            
            # Run the agent with user's question
            result = agent_executor.invoke({"messages": [("human", user_input)]})
            
            # Extract the final message
            final_message = result['messages'][-1].content
            print(f"\n{final_message}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    chat_with_agent()
