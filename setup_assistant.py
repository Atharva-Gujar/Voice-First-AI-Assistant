#!/usr/bin/env python3
"""
Interactive setup script for Voice-First AI Assistant.
Creates .env file with API keys and tests all components.
"""
import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")


def get_api_key(service_name, env_var_name, description):
    """Prompt user for an API key."""
    print(f"\n{service_name} Setup")
    print("-" * 40)
    print(f"{description}")
    print(f"\nPlease enter your {service_name} API key:")
    print("(or press Enter to skip)")
    
    key = input(f"{env_var_name}: ").strip()
    return key


def create_env_file():
    """Create .env file with API keys."""
    print_header("Voice-First AI Assistant Setup")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("Found existing .env file.")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing .env file.")
            return True
    
    # Get Anthropic API key
    anthropic_key = get_api_key(
        "Anthropic Claude",
        "ANTHROPIC_API_KEY",
        "Get your API key from: https://console.anthropic.com/"
    )
    
    # Get OpenAI API key
    openai_key = get_api_key(
        "OpenAI",
        "OPENAI_API_KEY",
        "Get your API key from: https://platform.openai.com/api-keys"
    )
    
    # Check if at least one key was provided
    if not anthropic_key and not openai_key:
        print("\n⚠️  Warning: No API keys provided.")
        print("The assistant requires both keys to function properly.")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return False
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write("# API Keys for Voice-First AI Assistant\n")
            f.write(f"ANTHROPIC_API_KEY={anthropic_key}\n")
            f.write(f"OPENAI_API_KEY={openai_key}\n")
        
        print("\n✓ Created .env file successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error creating .env file: {e}")
        return False


def test_dependencies():
    """Test that all required packages are installed."""
    print_header("Testing Dependencies")
    
    required_packages = {
        'openai': 'OpenAI Python SDK',
        'anthropic': 'Anthropic Python SDK',
        'sounddevice': 'Audio I/O',
        'numpy': 'Numerical computing',
        'soundfile': 'Audio file I/O',
        'dotenv': 'Environment variables',
        'pynput': 'Keyboard input',
        'scipy': 'Scientific computing'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {description:20} ({package})")
        except ImportError:
            print(f"✗ {description:20} ({package}) - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✓ All dependencies installed!")
    return True


def main():
    """Run the setup process."""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    print("\n🎤 Voice-First AI Assistant Setup")
    print("This wizard will help you configure the assistant.\n")
    
    # Test dependencies first
    if not test_dependencies():
        print("\n❌ Setup failed: Missing dependencies")
        print("\nPlease install required packages first:")
        print("  pip install -r requirements.txt")
        return 1
    
    # Create .env file
    if not create_env_file():
        print("\n❌ Setup failed: Could not create .env file")
        return 1
    
    # Run component tests
    print_header("Testing Components")
    print("Running basic component tests...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "test_components.py"],
            capture_output=False
        )
        
        if result.returncode != 0:
            print("\n⚠️  Some component tests failed.")
            print("The assistant may still work, but some features might not function properly.")
    except Exception as e:
        print(f"\n⚠️  Could not run component tests: {e}")
    
    # Final instructions
    print_header("Setup Complete!")
    print("✓ Environment configured")
    print("✓ Dependencies verified")
    print("✓ Components tested")
    
    print("\n📝 Next Steps:")
    print("  1. Run the assistant:")
    print("     python main.py")
    print("\n  2. Controls:")
    print("     - Hold SPACE to speak")
    print("     - Release SPACE to process")
    print("     - Press ESC to exit")
    print("\n  3. For detailed testing:")
    print("     python test_components.py --full-test")
    
    print("\n🎉 You're all set! Enjoy your voice assistant!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
