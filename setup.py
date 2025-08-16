#!/usr/bin/env python3
"""
Complete Setup Script for Secure Offline Legal Assistant

This script provides a complete setup experience including:
- Dependency installation
- Sample document creation
- System verification
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print the setup header."""
    print("=" * 70)
    print("🔒 SECURE OFFLINE LEGAL ASSISTANT - COMPLETE SETUP")
    print("=" * 70)
    print("This script will set up your Secure Offline Legal Assistant system.")
    print("=" * 70)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_ollama():
    """Check if Ollama is installed and running."""
    print("\n🔍 Checking Ollama installation...")
    
    # Check if ollama command exists
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama installed: {result.stdout.strip()}")
        else:
            print("❌ Ollama not found")
            print("Please install Ollama from https://ollama.ai")
            return False
    except FileNotFoundError:
        print("❌ Ollama not found")
        print("Please install Ollama from https://ollama.ai")
        return False
    
    # Check if Ollama server is running
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print("❌ Ollama server not responding")
            print("Please start Ollama: ollama serve")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Ollama server: {e}")
        print("Please start Ollama: ollama serve")
        return False

def pull_mixtral_model():
    """Pull the Mixtral model."""
    print("\n🤖 Pulling Mixtral model (this may take several minutes)...")
    try:
        # Check if model already exists
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "mixtral" in result.stdout.lower():
            print("✅ Mixtral model already available")
            return True
        
        # Pull the model
        subprocess.check_call(["ollama", "pull", "mixtral"])
        print("✅ Mixtral model pulled successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to pull Mixtral model: {e}")
        return False

def create_sample_documents():
    """Create sample legal documents for testing."""
    print("\n📄 Creating sample legal documents...")
    try:
        # Import and run the sample document creator
        from create_sample_document import create_sample_legal_document
        
        # Ensure directory exists
        os.makedirs("source_documents", exist_ok=True)
        
        # Create sample document
        create_sample_legal_document()
        print("✅ Sample documents created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample documents: {e}")
        return False

def run_system_test():
    """Run the system test."""
    print("\n🧪 Running system test...")
    try:
        subprocess.check_call([sys.executable, "test_setup.py"])
        return True
    except subprocess.CalledProcessError:
        print("❌ System test failed")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 70)
    print("🎉 SETUP COMPLETE!")
    print("=" * 70)
    print("Your Secure Offline Legal Assistant is ready to use!")
    print("\nNext steps:")
    print("1. Add your legal PDF documents to the 'source_documents/' directory")
    print("2. Run: python ingest.py")
    print("3. Run: python app.py")
    print("\nExample usage:")
    print("Ask a legal question: What are the requirements for filing a motion to dismiss?")
    print("\nSecurity features:")
    print("✅ Complete offline operation")
    print("✅ Local data processing")
    print("✅ Source verification")
    print("✅ Client confidentiality")
    print("=" * 70)

def main():
    """Main setup function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Check Ollama
    if not check_ollama():
        print("\n❌ Setup failed at Ollama check")
        print("Please install and start Ollama, then run this script again")
        sys.exit(1)
    
    # Pull Mixtral model
    if not pull_mixtral_model():
        print("\n❌ Setup failed at model download")
        sys.exit(1)
    
    # Create sample documents
    if not create_sample_documents():
        print("\n⚠️  Warning: Failed to create sample documents")
        print("You can add your own PDF documents to the source_documents/ directory")
    
    # Run system test
    if not run_system_test():
        print("\n⚠️  Warning: System test failed")
        print("You may need to troubleshoot the installation")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 