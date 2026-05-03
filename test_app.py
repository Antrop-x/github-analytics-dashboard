#!/usr/bin/env python
try:
    import app
    print("SUCCESS: App imports without errors")
except Exception as e:
    print(f"ERROR: {str(e)}")