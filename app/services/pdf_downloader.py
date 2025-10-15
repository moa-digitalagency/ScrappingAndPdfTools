import os
import requests
import zipfile
import uuid
import time
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_single_pdf(url, idx, temp_dir, max_retries=3):
    """Télécharge un seul PDF avec retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Téléchargement {idx}: {url} (tentative {attempt + 1}/{max_retries})")
            
            response = requests.get(
                url, 
                timeout=300,
                stream=True,
                headers={'User-Agent': 'Mozilla/5.0 PDF Downloader'}
            )
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                return {'success': False, 'url': url, 'error': 'Not a PDF file'}
            
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
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Téléchargement {idx} réussi: {filename}")
            return {'success': True, 'url': url, 'filename': filename}
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Erreur téléchargement {idx}, nouvelle tentative dans {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                logger.error(f"Échec téléchargement {idx} après {max_retries} tentatives: {str(e)}")
                return {'success': False, 'url': url, 'error': str(e)}
    
    return {'success': False, 'url': url, 'error': 'Max retries reached'}

def download_pdfs_and_zip(urls, temp_folder, max_workers=10):
    """Télécharge des PDFs en parallèle avec support pour 10,000+ documents"""
    temp_dir = os.path.join(temp_folder, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    successful = 0
    failed = 0
    failed_urls = []
    
    logger.info(f"Début du téléchargement de {len(urls)} PDFs avec {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(download_single_pdf, url, idx, temp_dir): (url, idx) 
            for idx, url in enumerate(urls, 1)
        }
        
        for future in as_completed(future_to_url):
            result = future.result()
            if result['success']:
                successful += 1
            else:
                failed += 1
                failed_urls.append({'url': result['url'], 'error': result.get('error', 'Unknown error')})
    
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
