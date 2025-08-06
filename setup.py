#!/usr/bin/env python3
"""
Setup script for the AI Pipeline project.
Helps with installation and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🤖 AI Pipeline Setup")
    print("=" * 50)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install project dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n🔧 Setting up environment variables...")
    
    env_template = "env_example.txt"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env file creation")
            return True
    
    if os.path.exists(env_template):
        shutil.copy(env_template, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys")
        return True
    else:
        print("❌ env_example.txt not found")
        return False

def check_api_keys():
    """Check if API keys are set"""
    print("\n🔑 Checking API keys...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = [
        "GEMINI_API_KEY",
        "OPENWEATHER_API_KEY",
        "LANGSMITH_API_KEY",
        "QDRANT_URL",
        "QDRANT_API_KEY"
    ]
    
    missing_keys = []
    
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
        else:
            print(f"✅ {key}")
    
    if missing_keys:
        print(f"\n❌ Missing API keys: {', '.join(missing_keys)}")
        print("\n📋 Please set the following API keys in your .env file:")
        print("1. GEMINI_API_KEY - Get from https://makersuite.google.com/app/apikey")
        print("2. OPENWEATHER_API_KEY - Get from https://openweathermap.org/api")
        print("3. LANGSMITH_API_KEY - Get from https://smith.langchain.com/")
        print("4. QDRANT_URL - Get from https://cloud.qdrant.io/")
        print("5. QDRANT_API_KEY - Get from https://cloud.qdrant.io/")
        return False
    
    print("✅ All API keys are set")
    return True

def run_tests():
    """Run project tests"""
    print("\n🧪 Running tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_ai_pipeline.py", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def create_sample_pdf():
    """Create a sample PDF for testing"""
    print("\n📄 Creating sample PDF...")
    
    try:
        # Try to create a simple PDF using reportlab
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            pdf_path = "sample_document.pdf"
            c = canvas.Canvas(pdf_path, pagesize=letter)
            
            # Read sample document
            with open("sample_document.txt", "r") as f:
                content = f.read()
            
            # Split into lines and add to PDF
            lines = content.split('\n')
            y = 750
            
            for line in lines:
                if line.strip():
                    c.drawString(50, y, line)
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = 750
            
            c.save()
            print(f"✅ Created sample PDF: {pdf_path}")
            return True
            
        except ImportError:
            print("⚠️  reportlab not available, skipping PDF creation")
            print("💡 Install reportlab with: pip install reportlab")
            return True
            
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
        return False

def show_next_steps():
    """Show next steps after setup"""
    print("\n🎉 Setup completed!")
    print("\n📝 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run the demo: python demo.py")
    print("3. Start the UI: streamlit run streamlit_app.py")
    print("4. Run tests: python run_tests.py")
    print("\n📚 Documentation:")
    print("- README.md - Complete project documentation")
    print("- Check LangSmith dashboard for evaluation metrics")
    print("- Upload PDFs in the Streamlit UI for RAG functionality")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create .env file
    if not create_env_file():
        return 1
    
    # Check API keys
    if not check_api_keys():
        print("\n⚠️  Please set your API keys and run setup again")
        return 1
    
    # Create sample PDF
    create_sample_pdf()
    
    # Run tests
    if not run_tests():
        print("\n⚠️  Tests failed, but setup can continue")
    
    # Show next steps
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 