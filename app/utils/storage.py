import os
import time
import shutil

def cleanup_temp_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")
    return False

def cleanup_old_temp_files(temp_folder, max_age_seconds=3600):
    """Nettoie les fichiers temporaires plus vieux que max_age_seconds (défaut: 1 heure)"""
    cleaned_count = 0
    try:
        current_time = time.time()
        
        if not os.path.exists(temp_folder):
            return cleaned_count
            
        for item in os.listdir(temp_folder):
            item_path = os.path.join(temp_folder, item)
            
            try:
                if os.path.isfile(item_path):
                    file_age = current_time - os.path.getmtime(item_path)
                    if file_age > max_age_seconds:
                        os.remove(item_path)
                        cleaned_count += 1
                elif os.path.isdir(item_path):
                    dir_age = current_time - os.path.getmtime(item_path)
                    if dir_age > max_age_seconds:
                        shutil.rmtree(item_path)
                        cleaned_count += 1
            except Exception as e:
                print(f"Error cleaning {item_path}: {e}")
                
    except Exception as e:
        print(f"Error cleaning temp folder: {e}")
    
    return cleaned_count
