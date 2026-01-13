#!/usr/bin/env python3
"""
git-irm: Interactive remove for untracked files using fzf
Part of git-fzf-more package
"""
import subprocess
import sys
import os
import argparse


# Global debug flag
DEBUG = False


def debug_print(*args, **kwargs):
    """Print debug information if DEBUG is enabled."""
    if DEBUG:
        print("[DEBUG]", *args, file=sys.stderr, **kwargs)


def run_command(cmd, input_text=None, capture=True):
    """Run a command and return result."""
    debug_print(f"Running command: {' '.join(cmd)}")
    if input_text:
        debug_print(f"Input text length: {len(input_text)} chars")
    
    try:
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=capture,
            text=True,
            check=False
        )
        debug_print(f"Command exit code: {result.returncode}")
        if result.stdout:
            debug_print(f"Stdout length: {len(result.stdout)} chars")
        if result.stderr:
            debug_print(f"Stderr: {result.stderr.strip()}")
        return result
    except FileNotFoundError:
        print(f"Error: {cmd[0]} not found. Is it installed?", file=sys.stderr)
        sys.exit(1)


def get_untracked_files():
    """Get list of untracked files."""
    debug_print("Getting untracked files...")
    result = run_command(['git', 'ls-files', '--others', '--exclude-standard'])
    
    if result.returncode != 0:
        print("Error: Not a git repository?", file=sys.stderr)
        sys.exit(1)
    
    files = result.stdout.strip()
    
    if not files:
        debug_print("No untracked files found")
        print("No untracked files found")
        sys.exit(0)
    
    file_list = files.split('\n')
    debug_print(f"Found {len(file_list)} untracked file(s)")
    if DEBUG:
        for f in file_list:
            debug_print(f"  - {f}")
    
    return files


def select_with_fzf(files):
    """Use fzf to select files."""
    debug_print("Starting fzf selection...")
    fzf_cmd = [
        'fzf',
        '--multi',
        '--header', 'Select untracked files to REMOVE (Tab to multi-select, Enter to confirm)',
        '--prompt', 'Remove> ',
        '--bind', 'ctrl-a:select-all,ctrl-d:deselect-all',
        '--color', 'header:italic:underline'
    ]
    
    debug_print(f"fzf command: {' '.join(fzf_cmd)}")
    
    try:
        # CRITICAL FIX: Don't capture stderr - fzf needs it for drawing UI!
        result = subprocess.run(
            fzf_cmd,
            input=files,
            stdout=subprocess.PIPE,  # Capture selection output
            stderr=None,  # Let fzf draw to terminal!
            text=True,
            check=False
        )
    except FileNotFoundError:
        print("Error: fzf not found. Is it installed?", file=sys.stderr)
        print("  brew install fzf  (macOS)", file=sys.stderr)
        print("  apt install fzf   (Ubuntu)", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        debug_print(f"fzf error: {e}")
        print(f"Error running fzf: {e}", file=sys.stderr)
        sys.exit(1)
    
    debug_print(f"fzf exit code: {result.returncode}")
    
    if result.returncode != 0:
        # User cancelled
        debug_print(f"fzf cancelled (exit code {result.returncode})")
        print("Cancelled", file=sys.stderr)
        sys.exit(0)
    
    selected = result.stdout.strip()
    
    if not selected:
        debug_print("No files selected")
        print("No files selected")
        sys.exit(0)
    
    selected_list = selected.split('\n')
    debug_print(f"Selected {len(selected_list)} file(s)")
    
    return selected_list


def confirm_removal(files):
    """Ask user to confirm removal."""
    debug_print("Showing files for confirmation...")
    print("\nFiles to be removed:")
    for f in files:
        print(f"  - {f}")
    
    print("\nRemove these files? [y/N]: ", end='', flush=True)
    
    try:
        response = input().strip().lower()
        debug_print(f"User response: '{response}'")
    except (KeyboardInterrupt, EOFError):
        debug_print("User interrupted input")
        print("\nCancelled")
        sys.exit(0)
    
    return response in ['y', 'yes']


def remove_files(files, verbose=True):
    """Remove the selected files."""
    removed = []
    failed = []
    
    debug_print(f"Removing {len(files)} file(s)...")
    
    for filepath in files:
        try:
            debug_print(f"Removing: {filepath}")
            os.remove(filepath)
            removed.append(filepath)
            if verbose:
                print(f"Removed: {filepath}")
        except OSError as e:
            debug_print(f"Failed to remove {filepath}: {e}")
            failed.append((filepath, str(e)))
            print(f"Failed to remove {filepath}: {e}", file=sys.stderr)
    
    return removed, failed


def main():
    """Main entry point for git-irm."""
    global DEBUG
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Interactive remove for untracked files using fzf',
        prog='git-irm'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    DEBUG = args.debug
    
    debug_print("Debug mode enabled")
    debug_print(f"Python: {sys.version}")
    debug_print(f"CWD: {os.getcwd()}")
    
    # Check if we're in a git repository
    debug_print("Checking if in git repository...")
    result = run_command(['git', 'rev-parse', '--git-dir'])
    if result.returncode != 0:
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)
    
    debug_print(f"Git dir: {result.stdout.strip()}")
    
    # Get untracked files
    files_text = get_untracked_files()
    
    # Select with fzf
    selected_files = select_with_fzf(files_text)
    
    # Confirm removal
    debug_print("Asking for confirmation...")
    if not confirm_removal(selected_files):
        debug_print("User declined confirmation")
        print("Cancelled")
        sys.exit(0)
    
    # Remove files
    debug_print("Removing files...")
    removed, failed = remove_files(selected_files)
    
    # Summary
    print(f"\nRemoved {len(removed)} file(s)")
    
    if failed:
        print(f"Failed to remove {len(failed)} file(s)", file=sys.stderr)
        sys.exit(1)
    
    debug_print("Done!")
    sys.exit(0)


if __name__ == '__main__':
    main()