"""
Legacy parallel indexing script.
DEPRECATED: Use setup_rag.py --parallel --workers N instead.
"""

import sys
from setup_rag import RAGSetup

if __name__ == "__main__":
    print("⚠️  This script is deprecated")
    print("Use: python setup_rag.py --parallel --workers 5")
    print()

    setup = RAGSetup()
    success = setup.run(quick=False, parallel=True, workers=5)
    sys.exit(0 if success else 1)
