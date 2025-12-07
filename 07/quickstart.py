"""
Quick Start Guide - AutoGen Web Info Agent
Run this to get started quickly!
"""

import subprocess
import sys
import os
from pathlib import Path

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(number, title):
    """Print a formatted step"""
    print(f"\n📍 Step {number}: {title}")

def run_command(command, description):
    """Run a command and report status"""
    print(f"  Running: {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ {description} - Success!")
            return True
        else:
            print(f"  ❌ {description} - Failed!")
            print(f"  Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error running command: {str(e)}")
        return False

def main():
    """Main setup function"""
    
    print_section("🤖 AutoGen Web Info Agent - Quick Start Setup")
    
    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    print(f"\nProject Directory: {current_dir}")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
    else:
        print(f"  ❌ Python 3.8+ required. Current: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    # Step 2: Check if .env exists
    print_step(2, "Checking Environment Configuration")
    env_file = current_dir / ".env"
    env_template = current_dir / ".env.template"
    
    if env_file.exists():
        print("  ✅ .env file found")
    else:
        print("  ⚠️  .env file not found")
        if env_template.exists():
            print("  📋 Creating .env from template...")
            try:
                import shutil
                shutil.copy(env_template, env_file)
                print("  ✅ .env created from template")
                print(f"  ⚠️  Please edit {env_file} and add your OpenAI API key!")
                print("\n  📝 Edit your .env file with:")
                print("     OPENAI_API_KEY=your_key_here")
                print("     Or configure OAI_CONFIG_LIST")
            except Exception as e:
                print(f"  ❌ Failed to create .env: {str(e)}")
        else:
            print("  ❌ .env.template not found")
    
    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies")
    requirements_file = current_dir / "requirements.txt"
    
    if requirements_file.exists():
        if run_command(
            f"{sys.executable} -m pip install -r \"{requirements_file}\"",
            "Installing packages"
        ):
            print("\n  📦 Installed packages:")
            print("     - autogen-agentchat")
            print("     - streamlit")
            print("     - python-dotenv")
            print("     - requests")
            print("     - beautifulsoup4")
            print("     - lxml")
            print("     - aiohttp")
        else:
            print("  ⚠️  Installation completed with warnings")
    else:
        print("  ❌ requirements.txt not found")
        sys.exit(1)
    
    # Step 4: Verify installation
    print_step(4, "Verifying Installation")
    
    packages_to_check = [
        ("autogen", "AutoGen"),
        ("streamlit", "Streamlit"),
        ("dotenv", "python-dotenv"),
    ]
    
    all_ok = True
    for module, name in packages_to_check:
        try:
            __import__(module)
            print(f"  ✅ {name} installed")
        except ImportError:
            print(f"  ❌ {name} not installed")
            all_ok = False
    
    if not all_ok:
        print("\n  ⚠️  Some packages failed to install. Please run:")
        print(f"     {sys.executable} -m pip install -r requirements.txt")
        return False
    
    # Step 5: Configuration verification
    print_step(5, "Verifying Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    config_list = os.getenv("OAI_CONFIG_LIST")
    
    if api_key or config_list:
        print("  ✅ API configuration found")
    else:
        print("  ❌ No API configuration found")
        print("  Please set OPENAI_API_KEY or OAI_CONFIG_LIST in .env")
        return False
    
    # Step 6: Create working directory
    print_step(6, "Setting Up Work Directory")
    
    work_dir = current_dir / "work_dir"
    if not work_dir.exists():
        try:
            work_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Work directory created: {work_dir}")
        except Exception as e:
            print(f"  ❌ Failed to create work directory: {str(e)}")
            return False
    else:
        print(f"  ✅ Work directory exists: {work_dir}")
    
    # Final summary
    print_section("✅ Setup Complete!")
    
    print("""
🚀 To start the application, run:

    streamlit run app.py

📝 Configuration:
   - API Key: configured
   - Working Directory: ./work_dir
   - Log File: agent.log

📖 First Steps:
   1. Open the Streamlit app in your browser
   2. Click "Initialize Agent" in the sidebar
   3. Choose a task type (Paper Analysis, Stock Market, etc.)
   4. Enter your query and execute

📚 Documentation:
   - README.md - Full documentation
   - IMPROVEMENTS.md - What was improved
   - .env.template - Configuration options

❓ Need Help?
   - Check README.md for troubleshooting
   - Review agent.log for detailed logs
   - Check .env configuration
    """)
    
    print("="*60)
    print("  Happy coding! 🎉")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
