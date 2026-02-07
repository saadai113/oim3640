#!/usr/bin/env python3
"""
Scans the Downloads folder for files larger than 100,000 KB (100 MB)
and displays them with their sizes, then opens them in file explorer.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_downloads_folder():
    """Get the Downloads folder path for the current user."""
    home = Path.home()
    downloads = home / "Downloads"
    
    if not downloads.exists():
        raise FileNotFoundError(f"Downloads folder not found at: {downloads}")
    
    return downloads

def get_file_size_kb(filepath):
    """Get file size in kilobytes."""
    try:
        size_bytes = os.path.getsize(filepath)
        return size_bytes / 1024
    except (OSError, PermissionError):
        return None

def format_size(size_kb):
    """Format size in human-readable format."""
    if size_kb >= 1024 * 1024:  # GB
        return f"{size_kb / (1024 * 1024):.2f} GB"
    elif size_kb >= 1024:  # MB
        return f"{size_kb / 1024:.2f} MB"
    else:
        return f"{size_kb:.2f} KB"

def scan_large_files(folder_path, size_threshold_kb=100000):
    """
    Scan folder for files larger than threshold.
    
    Args:
        folder_path: Path to scan
        size_threshold_kb: Minimum file size in KB (default 100,000 KB = 100 MB)
    
    Returns:
        List of tuples (filepath, size_kb)
    """
    large_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                size_kb = get_file_size_kb(filepath)
                
                if size_kb is not None and size_kb >= size_threshold_kb:
                    large_files.append((filepath, size_kb))
    except PermissionError as e:
        print(f"Permission denied accessing some folders: {e}")
    
    return large_files

def create_shortcuts_folder(large_files):
    """
    Create a temporary folder with shortcuts to all large files.
    
    Args:
        large_files: List of tuples (filepath, size_kb)
    
    Returns:
        Path to the shortcuts folder, or None if failed
    """
    import tempfile
    import shutil
    
    system = platform.system()
    
    try:
        # Create temp folder
        temp_dir = tempfile.mkdtemp(prefix="large_files_")
        print(f"\nCreating shortcuts folder: {temp_dir}")
        
        if system == "Windows":
            # Create .lnk shortcuts on Windows
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                
                for filepath, size_kb in large_files:
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        shortcut_path = os.path.join(temp_dir, f"{filename}.lnk")
                        shortcut = shell.CreateShortCut(shortcut_path)
                        shortcut.Targetpath = filepath
                        shortcut.save()
            except ImportError:
                print("Warning: win32com not available. Creating text file with paths instead.")
                create_text_file_list(temp_dir, large_files)
        
        elif system == "Darwin":  # macOS
            # Create aliases on macOS
            for filepath, size_kb in large_files:
                if os.path.exists(filepath):
                    filename = os.path.basename(filepath)
                    alias_path = os.path.join(temp_dir, filename)
                    try:
                        os.symlink(filepath, alias_path)
                    except OSError:
                        pass
        
        else:  # Linux and others
            # Create symlinks
            for filepath, size_kb in large_files:
                if os.path.exists(filepath):
                    filename = os.path.basename(filepath)
                    link_path = os.path.join(temp_dir, filename)
                    try:
                        os.symlink(filepath, link_path)
                    except OSError:
                        pass
        
        # Also create a text file with the full list
        create_text_file_list(temp_dir, large_files)
        
        return temp_dir
    
    except Exception as e:
        print(f"Error creating shortcuts folder: {e}")
        return None

def create_text_file_list(folder_path, large_files):
    """Create a text file listing all large files with their paths."""
    list_file = os.path.join(folder_path, "large_files_list.txt")
    with open(list_file, 'w', encoding='utf-8') as f:
        f.write("Large Files (>100 MB) Found in Downloads\n")
        f.write("=" * 80 + "\n\n")
        for filepath, size_kb in large_files:
            size_mb = size_kb / 1024
            f.write(f"{size_mb:.2f} MB - {filepath}\n")

def open_folder_in_explorer(folder_path):
    """Open a folder in the system file explorer."""
    system = platform.system()
    
    try:
        if system == "Windows":
            os.startfile(folder_path)
        elif system == "Darwin":  # macOS
            subprocess.run(['open', folder_path], check=False)
        else:  # Linux
            subprocess.run(['xdg-open', folder_path], check=False)
        return True
    except Exception as e:
        print(f"Error opening folder: {e}")
        return False

def select_files_to_delete(large_files):
    """
    Allow user to select which files to delete.
    
    Args:
        large_files: List of tuples (filepath, size_kb)
    
    Returns:
        List of filepaths to delete
    """
    print("\nSelect files to delete:")
    print("Enter the numbers of files you want to delete (comma-separated), or 'all' for all files, or 'none' to cancel.")
    print()
    
    # Display numbered list
    for i, (filepath, size_kb) in enumerate(large_files, 1):
        print(f"{i}. [{format_size(size_kb)}] {filepath}")
    
    print()
    
    while True:
        try:
            response = input("Enter selection: ").strip().lower()
            
            if response == 'none' or response == '':
                return []
            
            if response == 'all':
                return [fp for fp, _ in large_files]
            
            # Parse comma-separated numbers
            selected_indices = []
            for part in response.split(','):
                part = part.strip()
                if '-' in part:
                    # Handle ranges like "1-5"
                    start, end = part.split('-')
                    selected_indices.extend(range(int(start), int(end) + 1))
                else:
                    selected_indices.append(int(part))
            
            # Validate indices
            if all(1 <= idx <= len(large_files) for idx in selected_indices):
                return [large_files[idx - 1][0] for idx in selected_indices]
            else:
                print(f"Invalid selection. Please enter numbers between 1 and {len(large_files)}.")
        
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas, or 'all', or 'none'.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return []

def delete_files(filepaths):
    """
    Delete the specified files with confirmation.
    
    Args:
        filepaths: List of file paths to delete
    
    Returns:
        Tuple of (successful_deletes, failed_deletes)
    """
    if not filepaths:
        return 0, 0
    
    print(f"\n⚠️  WARNING: You are about to PERMANENTLY DELETE {len(filepaths)} file(s).")
    print("This cannot be undone.\n")
    
    for fp in filepaths:
        print(f"  - {fp}")
    
    print()
    confirmation = input("Type 'DELETE' (in all caps) to confirm: ").strip()
    
    if confirmation != 'DELETE':
        print("Deletion cancelled.")
        return 0, 0
    
    successful = 0
    failed = 0
    
    print("\nDeleting files...")
    for filepath in filepaths:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✓ Deleted: {filepath}")
                successful += 1
            else:
                print(f"✗ File not found: {filepath}")
                failed += 1
        except PermissionError:
            print(f"✗ Permission denied: {filepath}")
            failed += 1
        except Exception as e:
            print(f"✗ Error deleting {filepath}: {e}")
            failed += 1
    
    return successful, failed

def main():
    """Main execution function."""
    try:
        downloads_folder = get_downloads_folder()
        print(f"Scanning: {downloads_folder}")
        print(f"Threshold: 100,000 KB (100 MB)\n")
        
        large_files = scan_large_files(downloads_folder)
        
        if not large_files:
            print("No files found above 100,000 KB.")
            return
        
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Found {len(large_files)} file(s) above 100,000 KB:\n")
        print(f"{'Size':<15} {'File Path'}")
        print("-" * 80)
        
        total_size = 0
        for filepath, size_kb in large_files:
            print(f"{format_size(size_kb):<15} {filepath}")
            total_size += size_kb
        
        print("-" * 80)
        print(f"Total size: {format_size(total_size)}\n")
        
        # Main menu
        while True:
            print("\nOptions:")
            print("1. Open folder with shortcuts to view files")
            print("2. Delete selected files")
            print("3. Exit")
            
            try:
                choice = input("\nEnter your choice (1-3): ").strip()
                
                if choice == '1':
                    shortcuts_folder = create_shortcuts_folder(large_files)
                    if shortcuts_folder:
                        print(f"\nOpening: {shortcuts_folder}")
                        open_folder_in_explorer(shortcuts_folder)
                        print("\nNote: This temporary folder will be deleted when you restart your computer.")
                        print("The shortcuts point to the original files in your Downloads folder.")
                
                elif choice == '2':
                    files_to_delete = select_files_to_delete(large_files)
                    if files_to_delete:
                        successful, failed = delete_files(files_to_delete)
                        print(f"\nDeletion complete: {successful} succeeded, {failed} failed.")
                        
                        # Update the list
                        large_files = [(fp, size) for fp, size in large_files if fp not in files_to_delete]
                        if not large_files:
                            print("All files have been deleted.")
                            break
                    else:
                        print("No files selected for deletion.")
                
                elif choice == '3':
                    print("Exiting.")
                    break
                
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            
            except KeyboardInterrupt:
                print("\n\nExiting.")
                break
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
