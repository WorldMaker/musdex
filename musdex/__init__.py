"""
musdex
------

musdex is a VCS-aware zip archive tool

Current documentation site: http://pythonhosted.org/musdex/
"""

if __name__ == '__main__':
    import os
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from musdex.__main__ import main
    main()
