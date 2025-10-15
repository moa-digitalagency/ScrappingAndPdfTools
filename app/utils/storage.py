import os

def cleanup_temp_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")
    return False
