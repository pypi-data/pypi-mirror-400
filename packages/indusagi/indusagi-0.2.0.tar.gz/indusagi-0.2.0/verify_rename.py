"""Verification script for indusagi rename."""
import sys

def main():
    print("=" * 60)
    print("INDUSAGI RENAME VERIFICATION")
    print("=" * 60)

    # Test import
    try:
        import indusagi
        print(f"[OK] Package import: {indusagi.__version__}")
    except ImportError as e:
        print(f"[FAIL] Package import failed: {e}")
        return 1

    # Test classes
    try:
        from indusagi import Agent, AgentConfig, Agency
        print("[OK] Core classes imported")
    except ImportError as e:
        print(f"[FAIL] Classes import failed: {e}")
        return 1

    # Test CLI
    import subprocess
    try:
        # Use full path to the CLI executable
        cli_path = r"C:\Users\Varun israni\AppData\Roaming\Python\Python313\Scripts\indusagi.exe"
        result = subprocess.run([cli_path, "--help"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("[OK] CLI command works")
        else:
            print("[FAIL] CLI command failed")
            return 1
    except Exception as e:
        print(f"[FAIL] CLI test failed: {e}")
        return 1

    print("=" * 60)
    print("[SUCCESS] ALL VERIFICATIONS PASSED")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
