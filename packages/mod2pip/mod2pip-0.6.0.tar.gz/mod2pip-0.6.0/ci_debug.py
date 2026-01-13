#!/usr/bin/env python3
"""
Debug script for CI environments to help identify issues.
"""
import sys
import os
import subprocess
import importlib.util
import traceback

def check_environment():
    """Check the Python environment and key dependencies."""
    print("=== Environment Debug Information ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Check if mod2pip can be imported
    try:
        import mod2pip
        print(f"✅ mod2pip imported successfully, version: {mod2pip.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import mod2pip: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing mod2pip: {e}")
        traceback.print_exc()
        return False
    
    # Check key dependencies
    dependencies = ['yarg', 'docopt', 'requests', 'nbconvert', 'ipython']
    missing_deps = []
    
    for dep in dependencies:
        try:
            spec = importlib.util.find_spec(dep)
            if spec is not None:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {dep}: {version}")
            else:
                print(f"❌ {dep}: not found")
                missing_deps.append(dep)
        except Exception as e:
            print(f"❌ {dep}: error - {e}")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {missing_deps}")
        # Don't fail for missing ipython as it's optional for some tests
        critical_missing = [dep for dep in missing_deps if dep != 'ipython']
        if critical_missing:
            print(f"❌ Critical dependencies missing: {critical_missing}")
            return False
    
    return True

def run_basic_tests():
    """Run basic functionality tests."""
    print("\n=== Basic Functionality Tests ===")
    
    try:
        # Test basic import detection
        from mod2pip.mod2pip import get_all_imports
        
        # Create a simple test file
        test_content = """
import os
import sys
import requests
"""
        test_file = 'test_imports_debug.py'
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        imports = get_all_imports('.')
        print(f"✅ Import detection works, found {len(imports)} imports")
        
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def check_test_environment():
    """Check if the test environment is properly set up."""
    print("\n=== Test Environment Check ===")
    
    try:
        # Check if tests directory exists
        if not os.path.exists('tests'):
            print("❌ Tests directory not found")
            return False
        
        # Check if test files exist
        test_files = [f for f in os.listdir('tests') if f.startswith('test_') and f.endswith('.py')]
        if not test_files:
            print("❌ No test files found")
            return False
        
        print(f"✅ Found {len(test_files)} test files: {test_files}")
        
        # Try to import the test module
        sys.path.insert(0, 'tests')
        try:
            import test_mod2pip
            print("✅ Test module imported successfully")
        except Exception as e:
            print(f"⚠️  Could not import test module: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test environment check failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    print("Starting CI Debug Script...")
    print("=" * 50)
    
    success = True
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        success = False
    
    # Check basic functionality
    if not run_basic_tests():
        print("❌ Basic functionality check failed")
        success = False
    
    # Check test environment
    if not check_test_environment():
        print("❌ Test environment check failed")
        success = False
    
    print("=" * 50)
    if success:
        print("✅ All debug checks passed!")
        return 0
    else:
        print("❌ Some debug checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())