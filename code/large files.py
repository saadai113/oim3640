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
        
        # Ask user if they want to open folder with shortcuts
        try:
            response = input("Open folder with shortcuts to these files? (y/n): ").lower().strip()
            if response == 'y' or response == 'yes':
                shortcuts_folder = create_shortcuts_folder(large_files)
                if shortcuts_folder:
                    print(f"\nOpening: {shortcuts_folder}")
                    open_folder_in_explorer(shortcuts_folder)
                    print("\nNote: This temporary folder will be deleted when you restart your computer.")
                    print("The shortcuts/symlinks point to the original files in your Downloads folder.")
        except KeyboardInterrupt:
            print("\n\nCancelled.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
