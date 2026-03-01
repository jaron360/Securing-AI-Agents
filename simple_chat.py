"""
Simple chat interface for the security agent
Run this for an interactive conversation
"""
from agent import agent_executor

def main():
    print("=" * 80)
    print("🔒 Security Incident Detection Agent")
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
            
            # Run the agent with user's question
            result = agent_executor.invoke({"messages": [("human", user_input)]})
            
            # Extract the final message
            final_message = result['messages'][-1].content
            print(f"📊 {final_message}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()
