#!/usr/bin/env python3
"""
Build and publish script for Corebrum Python package.
"""

import os
import sys
import subprocess
import shutil


def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result.returncode == 0


def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_remove = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_remove:
        if os.path.exists(pattern):
            if os.path.isdir(pattern):
                shutil.rmtree(pattern)
            else:
                os.remove(pattern)
    
    # Remove __pycache__ directories
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))


def build_package():
    """Build the package."""
    print("Building package...")
    if not run_command("python -m build"):
        print("Build failed!")
        return False
    return True


def run_tests():
    """Run tests."""
    print("Running tests...")
    if not run_command("pytest"):
        print("Tests failed!")
        return False
    return True


def publish_to_testpypi():
    """Publish to TestPyPI."""
    print("Publishing to TestPyPI...")
    if not run_command("python -m twine upload --repository testpypi dist/*"):
        print("Publish to TestPyPI failed!")
        return False
    return True


def publish_to_pypi():
    """Publish to PyPI."""
    print("Publishing to PyPI...")
    if not run_command("python -m twine upload dist/*"):
        print("Publish to PyPI failed!")
        return False
    return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and publish Corebrum package")
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--test', action='store_true', help='Run tests')
    parser.add_argument('--build', action='store_true', help='Build package')
    parser.add_argument('--publish-test', action='store_true', help='Publish to TestPyPI')
    parser.add_argument('--publish', action='store_true', help='Publish to PyPI')
    parser.add_argument('--all', action='store_true', help='Do everything')
    
    args = parser.parse_args()
    
    if args.all:
        args.clean = True
        args.test = True
        args.build = True
    
    if args.clean:
        clean_build()
    
    if args.test:
        if not run_tests():
            sys.exit(1)
    
    if args.build:
        if not build_package():
            sys.exit(1)
    
    if args.publish_test:
        if not publish_to_testpypi():
            sys.exit(1)
    
    if args.publish:
        if not publish_to_pypi():
            sys.exit(1)
    
    if not any([args.clean, args.test, args.build, args.publish_test, args.publish, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
