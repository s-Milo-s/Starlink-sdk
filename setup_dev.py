#!/usr/bin/env python3
"""
Setup script for development environment.
Run this after cloning the repository.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and handle errors."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python_version():
    """Check if Python version meets requirements."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("Error: Python 3.10 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} meets requirements")


def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")
    
    # Determine activation script path
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    print(f"✅ Virtual environment created")
    print(f"To activate: {activate_script}")
    
    return pip_path


def install_dependencies(pip_path=None):
    """Install development dependencies."""
    if pip_path is None:
        pip_path = "pip"
    
    print("Installing dependencies...")
    
    # Install the package in development mode
    run_command(f"{pip_path} install -e .[dev]")
    
    print("✅ Dependencies installed")


def setup_env_file():
    """Set up environment file from example."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your actual API credentials")
    else:
        print("⚠️  No .env.example file found")


def run_tests():
    """Run basic tests to verify setup."""
    print("Running basic tests...")
    
    try:
        # Test imports
        result = run_command("python -c \"from starlink_sdk import StarlinkClient; print('✅ SDK imports successfully')\"", check=False)
        if result.returncode == 0:
            print("✅ Basic import test passed")
        else:
            print("⚠️  Import test failed - dependencies may not be fully installed")
    
    except Exception as e:
        print(f"⚠️  Test failed: {e}")


def main():
    """Main setup function."""
    print("🚀 Setting up Starlink SDK development environment...\n")
    
    # Check Python version
    check_python_version()
    
    # Set up virtual environment
    pip_path = setup_virtual_environment()
    
    # Install dependencies
    install_dependencies(pip_path)
    
    # Set up environment file
    setup_env_file()
    
    # Run basic tests
    run_tests()
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Activate your virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("2. Edit .env file with your API credentials")
    print("3. Run examples:")
    print("   python examples/basic_fleet_health.py")
    print("4. Start developing!")


if __name__ == "__main__":
    main()
