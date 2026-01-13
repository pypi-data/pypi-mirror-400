"""Script to update imports from my_agent_framework to indusagi."""
import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update imports in a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace imports
        content = content.replace('from my_agent_framework', 'from indusagi')
        content = content.replace('import my_agent_framework', 'import indusagi')
        content = content.replace('from indus_agents', 'from indusagi')
        content = content.replace('import indus_agents', 'import indusagi')

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def update_directory(directory):
    """Update all Python files in a directory."""
    updated_count = 0
    for root, dirs, files in os.walk(directory):
        # Skip .venv, .git, __pycache__
        dirs[:] = [d for d in dirs if d not in ['.venv', '.git', '__pycache__', 'build', 'dist']]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    updated_count += 1
    return updated_count

def main():
    base_dir = Path(__file__).parent

    print("=" * 60)
    print("UPDATING IMPORTS: my_agent_framework -> indusagi")
    print("=" * 60)

    directories_to_update = [
        base_dir / 'src' / 'indusagi',
        base_dir / 'tests',
        base_dir / 'examples',
        base_dir / 'agents',
        base_dir / 'activity-tracker-agent',
        base_dir / 'src' / 'test_agents',
    ]

    # Also update root-level Python files
    total_updated = 0

    # Update directories
    for directory in directories_to_update:
        if directory.exists():
            print(f"\nProcessing: {directory}")
            count = update_directory(directory)
            total_updated += count
            print(f"  Updated {count} files")
        else:
            print(f"\nSkipping (not found): {directory}")

    # Update root-level Python files
    print(f"\nProcessing root-level Python files...")
    root_count = 0
    for file_path in base_dir.glob('*.py'):
        if file_path.name != 'update_imports.py':  # Skip this script
            if update_imports_in_file(file_path):
                root_count += 1
    total_updated += root_count
    print(f"  Updated {root_count} files")

    print("\n" + "=" * 60)
    print(f"TOTAL FILES UPDATED: {total_updated}")
    print("=" * 60)

if __name__ == '__main__':
    main()
