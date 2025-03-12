#!/usr/bin/env python3
"""
Demo script for the Agentic Support Bot.
This script demonstrates the bot's capabilities with different documents and queries.
"""

import os
import sys
import argparse
import logging
import colorama
from colorama import Fore, Style

# Import our modules
from support_bot import SupportBotAgent, DocumentProcessor
from feedback_simulator import FeedbackSimulator

# Initialize colorama
colorama.init()

def setup_logging(verbose=False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        filename='support_bot_log.txt',
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Also log to console if verbose
    if verbose:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

def print_header():
    """Print a fancy header for the demo."""
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 30} AGENTIC SUPPORT BOT {'=' * 30}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}An intelligent bot that learns from documents and improves through feedback{Style.RESET_ALL}\n")

def print_section(title):
    """Print a section header."""
    print(f"\n{Fore.GREEN}{'-' * 40}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{title}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'-' * 40}{Style.RESET_ALL}\n")

def interactive_mode(bot):
    """Run the bot in interactive mode, allowing the user to ask questions."""
    print_section("Interactive Mode")
    print("Type your questions and get answers from the support bot.")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")
    
    query_history = []
    
    while True:
        try:
            query = input(f"{Fore.BLUE}Your question: {Style.RESET_ALL}")
            
            if query.lower() in ['exit', 'quit', 'q']:
                break
                
            if not query.strip():
                continue
                
            # Add to history
            query_history.append(query)
            
            # Process the query
            print(f"{Fore.YELLOW}Thinking...{Style.RESET_ALL}")
            response = bot.answer_query(query)
            
            # Display the response
            print(f"\n{Fore.WHITE}Answer: {response['answer']}{Style.RESET_ALL}")
            
            # Get feedback
            feedback = bot.get_feedback(query, response)
            print(f"{Fore.MAGENTA}Simulated Feedback: {feedback['feedback_type']}{Style.RESET_ALL}")
            
            if feedback['feedback_type'] != "good":
                print(f"{Fore.YELLOW}Improving response...{Style.RESET_ALL}")
                improved_response = bot.adjust_response(query, response, feedback)
                print(f"\n{Fore.GREEN}Improved Answer: {improved_response['answer']}{Style.RESET_ALL}")
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
    
    return query_history

def demo_mode(bot):
    """Run a demonstration with predefined queries."""
    print_section("Demo Mode")
    
    demo_queries = [
        "What is this World?",
        "What's the refund policy?",
        "How do I track my order?",
        "Do you offer international shipping?",
        "How do I update my device software?",
        "What happens if my device breaks after warranty?",
        "How do I contact customer support?",
        "Can I return a product after opening it?"
    ]
    
    print(f"Running demo with {len(demo_queries)} sample queries...\n")
    bot.run(demo_queries)

def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description='Agentic Support Bot Demo')
    parser.add_argument('--document', '-d', type=str, default='faq.txt',
                        help='Path to the document file (PDF or TXT)')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Print header
    print_header()
    
    # Check if document exists
    if not os.path.exists(args.document):
        print(f"{Fore.RED}Error: Document '{args.document}' not found.{Style.RESET_ALL}")
        return 1
    
    # Print document info
    print(f"Using document: {args.document}")
    
    try:
        # Initialize the support bot
        print(f"\n{Fore.YELLOW}Initializing support bot...{Style.RESET_ALL}")
        bot = SupportBotAgent(args.document)
        
        # Run in the selected mode
        if args.interactive:
            query_history = interactive_mode(bot)
            
            # Print summary at the end
            if query_history:
                print_section("Session Summary")
                print(f"You asked {len(query_history)} questions in this session.")
                print(f"Feedback stats: {bot.feedback_stats}")
        else:
            demo_mode(bot)
        
        print(f"\n{Fore.CYAN}Thank you for using the Agentic Support Bot!{Style.RESET_ALL}\n")
        return 0
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 