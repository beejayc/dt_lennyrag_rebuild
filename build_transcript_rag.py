"""
Legacy sequential indexing script.
DEPRECATED: Use setup_rag.py instead.
"""

import sys
from setup_rag import RAGSetup

if __name__ == "__main__":
    print("⚠️  This script is deprecated")
    print("Use: python setup_rag.py")
    print()

    setup = RAGSetup()
    success = setup.run(quick=False, parallel=False, workers=1)
    sys.exit(0 if success else 1)
