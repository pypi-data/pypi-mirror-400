"""
KmBiT CLI - Command line interface to the kernel.

Usage:
    kmbit which "review this code"
    kmbit ls /agents
    kmbit tree
    kmbit stats
"""

import sys
from .kernel import Kernel


def main():
    """CLI entry point."""
    kernel = Kernel()

    if len(sys.argv) < 2:
        print("KmBiT Kernel - The AI Filesystem")
        print()
        print("Usage:")
        print("  kmbit which <query>  - Route a query")
        print("  kmbit ls [path]      - List contents")
        print("  kmbit stat <path>    - Show metadata")
        print("  kmbit tree [path]    - Tree view")
        print("  kmbit stats          - Kernel stats")
        print("  kmbit routes         - List routes")
        return

    # Join all args as command
    command = " ".join(sys.argv[1:])
    result = kernel.execute(command)
    print(result)


if __name__ == "__main__":
    main()
