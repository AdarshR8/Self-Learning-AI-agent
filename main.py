#!/usr/bin/env python3
"""
Self-Learning AI Agent
Interactive CLI Demonstration (Inspired by Dave Ebbelaar's Tutorial)
"""

import sys
import logging
import warnings

# Suppress harmless optional feature warnings from dependencies
warnings.filterwarnings("ignore")
logging.getLogger("mem0").setLevel(logging.ERROR)
logging.getLogger("qdrant_client").setLevel(logging.ERROR)

from src.config import Config

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    rich_available = True
    console = Console()
except ImportError:
    rich_available = False

def print_message(title: str, text: str, style: str = "cyan"):
    if rich_available:
        console.print(Panel(Markdown(text), title=title, border_style=style))
    else:
        print(f"\n--- {title} ---\n{text}\n" + "-" * 30)

def main():
    Config.validate()
    
    # Delayed import so configuration checks happen first
    try:
        from src.agent import SelfLearningAIAgent
    except ImportError as e:
        print(f"[!] Missing dependencies: {e}")
        print("    Please run: pip install -r requirements.txt")
        sys.exit(1)

    print("=" * 65)
    print("      🧠 SELF-LEARNING AI AGENT WITH PERSISTENT MEMORY 🧠      ")
    print("        Reference: Dave Ebbelaar's Mem0 Agent Architecture     ")
    print("=" * 65)
    print("Commands:")
    print("  /memories  - View everything the agent has learned about you")
    print("  /reset     - Wipe all stored memories and start clean")
    print("  /exit      - Quit the session\n")

    user_id = input(f"Enter user ID (Press Enter for default: '{Config.DEFAULT_USER_ID}'): ").strip()
    if not user_id:
        user_id = Config.DEFAULT_USER_ID

    print(f"\n[+] Initializing agent for user: '{user_id}'...")
    agent = SelfLearningAIAgent(user_id=user_id)
    print("[✓] Agent ready. Start chatting below!\n")

    while True:
        try:
            user_input = input(f"\n[{user_id}] > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["/exit", "exit", "quit", ":q"]:
                print("[*] Goodbye!")
                break

            elif user_input.lower() == "/memories":
                memories = agent.get_known_memories()
                if memories:
                    mem_list = "\n".join(f"- {m}" for m in memories)
                    print_message("Learned Memories", mem_list, style="yellow")
                else:
                    print_message("Learned Memories", "No memories stored yet.", style="yellow")
                continue

            elif user_input.lower() == "/reset":
                confirm = input("Are you sure you want to delete all memories? (y/N): ").strip().lower()
                if confirm == "y":
                    agent.reset_memory()
                    print("[✓] All memories cleared successfully.")
                continue

            # Process chat and self-learning
            reply = agent.chat(user_input)
            print_message("AI Agent", reply, style="green")

        except KeyboardInterrupt:
            print("\n[*] Exiting session.")
            break
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
