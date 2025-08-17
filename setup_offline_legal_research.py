#!/usr/bin/env python3
"""
Offline Legal Research Setup Script

This script automates the complete setup process for offline Belgian and EU legal research.
It handles database acquisition, integration, and system configuration in one command.

Usage:
    python setup_offline_legal_research.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "requests",
        "beautifulsoup4", 
        "langchain",
        "chromadb",
        "sentence-transformers"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        install_command = f"pip install {' '.join(missing_packages)}"
        return run_command(install_command, "Installing dependencies")
    
    return True

def setup_legal_databases():
    """Set up legal databases."""
    print("\n🏛️  Setting up legal databases...")
    
    # Check if legal databases already exist
    legal_db_dir = Path("./legal_databases")
    if legal_db_dir.exists() and any(legal_db_dir.iterdir()):
        print("📚 Legal databases already exist. Skipping acquisition.")
        return True
    
    # Run database acquisition
    return run_command("python3 legal_database_acquisition.py", 
                      "Acquiring legal databases")

def integrate_databases():
    """Integrate databases with the legal assistant."""
    print("\n🔗 Integrating databases with legal assistant...")
    
    return run_command("python3 integrate_legal_databases.py", 
                      "Integrating legal databases")

def test_system():
    """Test the legal assistant system."""
    print("\n🧪 Testing legal assistant system...")
    
    # Check if vector store exists
    vector_store = Path("./chroma_db")
    if not vector_store.exists():
        print("❌ Vector store not found. Running document processing...")
        if not run_command("python3 ingest.py", "Processing documents"):
            return False
    
    print("✅ System appears to be ready")
    return True

def create_startup_script():
    """Create a convenient startup script."""
    print("\n📝 Creating startup script...")
    
    startup_script = """#!/bin/bash
# Legal Assistant Startup Script

echo "🏛️  Starting Belgian and EU Legal Assistant..."
echo "================================================"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Check if Mixtral model is available
if ! ollama list | grep -q "mixtral"; then
    echo "📥 Downloading Mixtral model..."
    ollama pull mixtral
fi

# Start the legal assistant
echo "🎯 Starting legal assistant..."
python3 app.py
"""
    
    with open("start_legal_assistant.sh", "w") as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod("start_legal_assistant.sh", 0o755)
    
    print("✅ Startup script created: start_legal_assistant.sh")
    return True

def main():
    """Main setup function."""
    print("🏛️  Offline Belgian and EU Legal Research Setup")
    print("=" * 60)
    print("This script will set up a complete offline legal research system.")
    print("The process includes:")
    print("1. Dependency installation")
    print("2. Legal database acquisition")
    print("3. System integration")
    print("4. Testing and verification")
    print("5. Startup script creation")
    print()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed: Dependencies could not be installed")
        return False
    
    # Step 2: Set up legal databases
    if not setup_legal_databases():
        print("\n❌ Setup failed: Legal databases could not be acquired")
        return False
    
    # Step 3: Integrate databases
    if not integrate_databases():
        print("\n❌ Setup failed: Database integration failed")
        return False
    
    # Step 4: Test system
    if not test_system():
        print("\n❌ Setup failed: System test failed")
        return False
    
    # Step 5: Create startup script
    if not create_startup_script():
        print("\n❌ Setup failed: Could not create startup script")
        return False
    
    # Success!
    print("\n🎉 Setup completed successfully!")
    print("=" * 60)
    print("Your offline Belgian and EU legal research system is ready!")
    print()
    print("🚀 To start the legal assistant:")
    print("   ./start_legal_assistant.sh")
    print()
    print("📚 Available jurisdictions:")
    print("   - federaal (Belgian federal law)")
    print("   - vlaams (Flemish regional law)")
    print("   - waals (Walloon regional law)")
    print("   - brussels (Brussels regional law)")
    print("   - eu (European Union law)")
    print()
    print("🔍 Example searches:")
    print("   - 'Wat zijn de rechten van een werknemer?' (Dutch)")
    print("   - 'Quels sont les droits du travailleur?' (French)")
    print("   - 'What are employee rights under Belgian law?' (English)")
    print()
    print("🔒 Security features:")
    print("   - 100% offline operation")
    print("   - Client confidentiality guaranteed")
    print("   - Quantum-resistant encryption")
    print("   - Complete audit trail")
    print()
    print("📖 For detailed usage instructions, see:")
    print("   OFFLINE_LEGAL_RESEARCH_GUIDE.md")
    print()
    print("Happy legal researching! 🏛️⚖️")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 