from pathlib import Path
import os

def is_safe_path(path: str) -> bool:
    if not path:
        return False
    if os.path.isabs(path):
        return False
    if ".." in path:
        return False
    return True


def read_file(path: str) -> str:
    """Read a file and return its contents"""
    file_path = Path(path)
 
    if not file_path.exists():
     return f"Error: File '{path}' does not exist."
 
    return file_path.read_text()


def list_files(path:str = ".")-> str:
    if not is_safe_path(path):
        return "Error: Unsafe path detected."
    
    full_path = os.path.join(os.getcwd(), path)
    
    if not os.path.exists(full_path):
        return "❌ Path does not exist."

    if not os.path.isdir(full_path):
        return "❌ Path is not a directory."
    
    try:
        items = os.listdir(full_path)
        if not items:
            return "📂 Directory is empty."
        
        return "\n".join(sorted(items))
    except Exception as e:
        return f"❌ Error reading directory: {str(e)}"
    
def write_file(path: str, content: str) -> str:
    if not is_safe_path(path):
        return "❌ Invalid path."

    full_path = os.path.join(os.getcwd(), path)

    # Prevent overwriting existing files (for now)
    if os.path.exists(full_path):
        return "❌ File already exists. Overwrite not allowed."

    parent = os.path.dirname(full_path)
    if parent and not os.path.exists(parent):
        return "❌ Parent directory does not exist."

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File written: {path}"
    except Exception:
        return "❌ Failed to write file."

def create_dir(path: str)-> str:
    if not is_safe_path(path):
        return "❌ Invalid path."
    full_path = os.path.join(os.getcwd(), path)
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"✅ Directory created: {path}"
    except Exception:
        return "❌ Failed to create directory."