#!/usr/bin/env python3
"""
Compile translation files for Flask-Babel
"""

import os
import subprocess
import sys

def compile_translations():
    """Compile all translation files."""
    print("🌐 Compiling translation files...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Compile translations for each language
    languages = ['nl', 'fr', 'en', 'de']
    
    for lang in languages:
        po_file = os.path.join(script_dir, 'translations', lang, 'LC_MESSAGES', 'messages.po')
        mo_file = os.path.join(script_dir, 'translations', lang, 'LC_MESSAGES', 'messages.mo')
        
        if os.path.exists(po_file):
            try:
                # Compile .po to .mo
                result = subprocess.run([
                    'pybabel', 'compile', 
                    '-d', os.path.join(script_dir, 'translations'),
                    '-l', lang
                ], capture_output=True, text=True, cwd=script_dir)
                
                if result.returncode == 0:
                    print(f"✅ Compiled translations for {lang}")
                else:
                    print(f"❌ Failed to compile translations for {lang}: {result.stderr}")
                    
            except FileNotFoundError:
                print(f"❌ pybabel not found. Please install Flask-Babel: pip install Flask-Babel")
                return False
        else:
            print(f"⚠️  Translation file not found for {lang}: {po_file}")
    
    print("🎉 Translation compilation completed!")
    return True

def extract_messages():
    """Extract messages from source files."""
    print("📝 Extracting messages from source files...")
    
    try:
        result = subprocess.run([
            'pybabel', 'extract', 
            '-F', 'babel.cfg',
            '-k', '_',
            '-o', 'messages.pot',
            '.'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Messages extracted to messages.pot")
            return True
        else:
            print(f"❌ Failed to extract messages: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pybabel not found. Please install Flask-Babel: pip install Flask-Babel")
        return False

def update_translations():
    """Update existing translation files with new messages."""
    print("🔄 Updating translation files...")
    
    languages = ['nl', 'fr', 'en', 'de']
    
    for lang in languages:
        try:
            result = subprocess.run([
                'pybabel', 'update',
                '-i', 'messages.pot',
                '-d', 'translations',
                '-l', lang
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Updated translations for {lang}")
            else:
                print(f"❌ Failed to update translations for {lang}: {result.stderr}")
                
        except FileNotFoundError:
            print("❌ pybabel not found. Please install Flask-Babel: pip install Flask-Babel")
            return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "extract":
            extract_messages()
        elif command == "update":
            update_translations()
        elif command == "compile":
            compile_translations()
        elif command == "all":
            extract_messages()
            update_translations()
            compile_translations()
        else:
            print("Usage: python compile_translations.py [extract|update|compile|all]")
    else:
        # Default: just compile
        compile_translations() 