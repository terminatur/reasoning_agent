"""
File: main.py
Purpose: Main entry point for the AI Research Agent with command line interface and example usage
Functionality: Provides CLI interface, example research queries, and basic agent interaction
Update Trigger: When CLI options change, new example queries are added, or user interface is modified
Last Modified: 2024-06-24
"""
import sys
import argparse
from typing import Optional

from ai_research_agent.agent import research_agent
from ai_research_agent.config import config

def run_research(query: str, strategy: str = "decomposition_first", export_format: str = "markdown") -> None:
    """
    Run a research query and display results.
    
    Args:
        query: Research question or topic
        strategy: Planning strategy to use
        export_format: Format for exporting results
    """
    print("=" * 80)
    print("🔬 AI RESEARCH AGENT")
    print("=" * 80)
    
    try:
        # Run the research
        report = research_agent.research(query, strategy)
        
        # Display results
        print("\n" + "=" * 80)
        print("📊 RESEARCH RESULTS")
        print("=" * 80)
        
        print(f"📄 **Executive Summary:**")
        print(report.executive_summary)
        print()
        
        print(f"🔍 **Key Findings:**")
        print(report.detailed_findings[:500] + "..." if len(report.detailed_findings) > 500 else report.detailed_findings)
        print()
        
        print(f"💡 **Conclusions:**")
        print(report.conclusions)
        print()
        
        print(f"📚 **Citations:** {len(report.citations)} sources")
        for i, citation in enumerate(report.citations[:5], 1):
            print(f"  {i}. {citation.title}")
            if citation.source_url:
                print(f"     {citation.source_url}")
        
        if len(report.citations) > 5:
            print(f"     ... and {len(report.citations) - 5} more sources")
        
        print(f"\n📈 **Report Statistics:**")
        print(f"  - Word Count: {report.word_count}")
        print(f"  - Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  - Methodology: {report.methodology[:100]}...")
        
        # Get execution summary
        summary = research_agent.get_execution_summary()
        if "total_steps" in summary:
            print(f"  - Steps Executed: {summary['total_steps']}")
            print(f"  - Success Rate: {summary['success_rate']:.1%}")
            print(f"  - Total Time: {summary['total_execution_time']:.1f}s")
        
    except Exception as e:
        print(f"❌ Research failed: {e}")
        print("\n🛠️  Troubleshooting:")
        print("1. Check that required API keys are set in .env file")
        print("2. Ensure internet connection is available")
        print("3. Verify that all dependencies are installed")

def run_interactive_mode() -> None:
    """Run the agent in interactive mode."""
    print("🤖 AI Research Agent - Interactive Mode")
    print("Type 'quit' to exit, 'status' for agent status, 'help' for commands\n")
    
    while True:
        try:
            user_input = input("Research Query: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye! 👋")
                break
            elif user_input.lower() == 'status':
                status = research_agent.get_status()
                print(f"Agent Status: {status}")
                continue
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("  - Enter any research question to start research")
                print("  - 'status' - Show agent status")
                print("  - 'quit' or 'exit' - Exit interactive mode")
                continue
            elif user_input.lower() == 'clear':
                research_agent.clear_session()
                print("Session cleared")
                continue
            elif not user_input:
                continue
            
            # Run research
            run_research(user_input)
            print("\n" + "-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_examples() -> None:
    """Run example research queries."""
    examples = [
        "What are the latest developments in quantum computing?",
        "How is artificial intelligence being used in healthcare?",
        "What are the environmental impacts of cryptocurrency mining?",
        "Analyze the current state of renewable energy adoption globally"
    ]
    
    print("🎯 Running Example Research Queries")
    print("=" * 50)
    
    for i, example in enumerate(examples, 1):
        print(f"\n📝 Example {i}: {example}")
        user_input = input("Run this example? (y/n/skip all): ").strip().lower()
        
        if user_input == 'n':
            continue
        elif user_input in ['skip all', 'skip']:
            break
        else:
            run_research(example)
            input("\nPress Enter to continue to next example...")

def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="AI Research Agent - Autonomous research with citations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "What is machine learning?"
  python main.py --interactive
  python main.py --examples
  python main.py "Climate change impacts" --strategy interleaved
        """
    )
    
    parser.add_argument(
        "query", 
        nargs="?", 
        help="Research query to investigate"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--examples", "-e",
        action="store_true",
        help="Run example research queries"
    )
    
    parser.add_argument(
        "--strategy", "-s",
        choices=["decomposition_first", "interleaved"],
        default="decomposition_first",
        help="Planning strategy to use (default: decomposition_first)"
    )
    
    parser.add_argument(
        "--export", "-x",
        choices=["markdown", "text"],
        default="markdown",
        help="Export format for results (default: markdown)"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show agent status and exit"
    )
    
    args = parser.parse_args()
    
    # Check configuration
    try:
        config.validate_required_keys()
    except ValueError as e:
        print(f"⚠️  Configuration Warning: {e}")
        print("Some features may not work without proper API keys.")
        print("See .env.example for required environment variables.\n")
    
    # Handle different modes
    if args.status:
        status = research_agent.get_status()
        print("🤖 Agent Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    if args.interactive:
        run_interactive_mode()
        return
    
    if args.examples:
        run_examples()
        return
    
    if args.query:
        run_research(args.query, args.strategy, args.export)
        return
    
    # No arguments provided, show help
    parser.print_help()
    print("\n💡 Quick start:")
    print('  python main.py "Your research question here"')
    print("  python main.py --interactive")

if __name__ == "__main__":
    main()
