"""
Simple chat interface for the Strands-based security agent
"""
from agent_strands import agent

def main():
    print("=" * 80)
    print("🔒 Security Incident Detection Agent (AWS Strands SDK)")
    print("=" * 80)
    print("\nAsk me about today's cybersecurity news and incidents!")
    print("\nExamples:")
    print("  • What's the security news for today?")
    print("  • Are there any new vulnerabilities?")
    print("  • What incidents happened in the past 24 hours?")
    print("  • Show me the latest CVEs")
    print("  • What's trending on Hacker News about security?")
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
            
            print("\n🤖 Agent: Let me check the latest sources for you...\n")
            
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
    main()
