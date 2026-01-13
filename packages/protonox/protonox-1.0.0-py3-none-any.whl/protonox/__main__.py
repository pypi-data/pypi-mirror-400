"""
Main entry point for the Protonox CLI.
"""

import sys
import os

# Add the project root to the path so we can import protonox_workflow
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from protonox_workflow import main

if __name__ == "__main__":
    main()