# Vercel entry point for PediAssist
import sys
import os

# Add the parent directory to the path so we can import pediassist modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import and run the web app
from pediassist.web_app import app

# Vercel requires the app to be named "app"
application = app