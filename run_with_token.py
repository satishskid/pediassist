#!/usr/bin/env python3
"""
Wrapper script to run final_complete_setup.py with pre-configured token
"""

import os
import subprocess
import sys

def main():
    # Set the API token from the provided token
    api_token = "jyt_RB4MI27f2f514327f6ec9f477357f545b58afM0L6aYJt0G7it31znnv5WBj3DIm6hhi"
    
    # Set environment variable
    os.environ['CLOUDFLARE_API_TOKEN'] = api_token
    
    print("🚀 Starting Cloudflare Zero Trust setup with provided token...")
    print(f"Account ID: edc37d3cfe6b6d9c7a6f6b5753b88d86")
    print(f"Zone ID: 27f2f514327f6ec9f477357f545b58af")
    
    # Run the setup script
    try:
        result = subprocess.run([sys.executable, 'final_complete_setup.py'], 
                                env=os.environ, 
                                capture_output=False, 
                                text=True)
        
        if result.returncode == 0:
            print("✅ Setup completed successfully!")
        else:
            print(f"❌ Setup failed with return code: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
    except Exception as e:
        print(f"❌ Error running setup: {e}")

if __name__ == "__main__":
    main()