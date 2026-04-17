"""
Legacy quick test script.
DEPRECATED: Use setup_rag.py --quick instead.
"""

import sys
from setup_rag import RAGSetup

if __name__ == "__main__":
    print("⚠️  This script is deprecated")
    print("Use: python setup_rag.py --quick")
    print()

    setup = RAGSetup()
    success = setup.run(quick=True, parallel=False, workers=1)
    sys.exit(0 if success else 1)
