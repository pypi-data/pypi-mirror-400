#!/usr/bin/env python3
"""
git-irm: Interactive remove for untracked files using fzf
Part of git-fzf-more package
"""
import subprocess
import sys
import os


def run_command(cmd, input_text=None, capture=True):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=capture,
            text=True,
            check=False
        )
        return result
    except FileNotFoundError:
        print(f"Error: {cmd[0]} not found. Is it installed?", file=sys.stderr)
        sys.exit(1)


def get_untracked_files():
    """Get list of untracked files."""
    result = run_command(['git', 'ls-files', '--others', '--exclude-standard'])
    
    if result.returncode != 0:
        print("Error: Not a git repository?", file=sys.stderr)
        sys.exit(1)
    
    files = result.stdout.strip()
    
    if not files:
        print("No untracked files found")
        sys.exit(0)
    
    return files


def select_with_fzf(files):
    """Use fzf to select files."""
    fzf_cmd = [
        'fzf',
        '--multi',
        '--preview', 'head -100 {}',
        '--preview-window', 'right:60%',
        '--header', 'Select untracked files to REMOVE (Tab to multi-select, Enter to confirm)',
        '--prompt', 'Remove> ',
        '--bind', 'ctrl-a:select-all,ctrl-d:deselect-all',
        '--color', 'header:italic:underline'
    ]
    
    result = run_command(fzf_cmd, input_text=files)
    
    if result.returncode != 0:
        # User cancelled
        print("Cancelled", file=sys.stderr)
        sys.exit(0)
    
    selected = result.stdout.strip()
    
    if not selected:
        print("No files selected")
        sys.exit(0)
    
    return selected.split('\n')


def confirm_removal(files):
    """Ask user to confirm removal."""
    print("\nFiles to be removed:")
    for f in files:
        print(f"  - {f}")
    
    print("\nRemove these files? [y/N]: ", end='', flush=True)
    
    try:
        response = input().strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled")
        sys.exit(0)
    
    return response in ['y', 'yes']


def remove_files(files, verbose=True):
    """Remove the selected files."""
    removed = []
    failed = []
    
    for filepath in files:
        try:
            os.remove(filepath)
            removed.append(filepath)
            if verbose:
                print(f"Removed: {filepath}")
        except OSError as e:
            failed.append((filepath, str(e)))
            print(f"Failed to remove {filepath}: {e}", file=sys.stderr)
    
    return removed, failed


def main():
    """Main entry point for git-irm."""
    # Check if we're in a git repository
    result = run_command(['git', 'rev-parse', '--git-dir'])
    if result.returncode != 0:
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    # Get untracked files
    files_text = get_untracked_files()
    
    # Select with fzf
    selected_files = select_with_fzf(files_text)
    
    # Confirm removal
    if not confirm_removal(selected_files):
        print("Cancelled")
        sys.exit(0)
    
    # Remove files
    removed, failed = remove_files(selected_files)
    
    # Summary
    print(f"\nRemoved {len(removed)} file(s)")
    
    if failed:
        print(f"Failed to remove {len(failed)} file(s)", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()