import os
import requests
import zipfile
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

def download_pdfs_and_zip(urls, temp_folder):
    temp_dir = os.path.join(temp_folder, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    successful = 0
    failed = 0
    failed_urls = []
    
    for idx, url in enumerate(urls, 1):
        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                failed += 1
                failed_urls.append({'url': url, 'error': 'Not a PDF file'})
                continue
            
            filename = f'document_{idx}.pdf'
            if url.split('/')[-1]:
                try:
                    filename = secure_filename(url.split('/')[-1])
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'
                except:
                    pass
            
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            successful += 1
            
        except Exception as e:
            failed += 1
            failed_urls.append({'url': url, 'error': str(e)})
    
    if successful == 0:
        return {
            'success': False,
            'error': f'Aucun PDF téléchargé avec succès. {failed} échecs.'
        }
    
    unique_id = str(uuid.uuid4())[:8]
    zip_filename = f'pdfs_{unique_id}.zip'
    zip_path = os.path.join(temp_folder, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
    
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(temp_dir)
    
    return {
        'success': True,
        'zip_path': zip_path,
        'filename': zip_filename,
        'total': len(urls),
        'successful': successful,
        'failed': failed,
        'failed_urls': failed_urls
    }
