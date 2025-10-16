"""
ScrappingAndPdfTools
Developed : MOA Digital Agency LLC
Par : Aisance KALONJI
Mail : moa@myoneart.com
Siteweb : www.myoneart.com
"""

import os
import requests
import zipfile
import uuid
import time
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.utils.progress import progress_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_single_pdf(url, idx, temp_dir, max_retries=3):
    """Télécharge un seul PDF avec retry logic et gestion robuste des erreurs"""
    for attempt in range(max_retries):
        response = None
        try:
            logger.info(f"Téléchargement {idx}: {url[:100]}... (tentative {attempt + 1}/{max_retries})")
            
            response = requests.get(
                url, 
                timeout=(30, 300),
                stream=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/pdf,*/*'
                },
                allow_redirects=True
            )
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"Document {idx} n'est pas un PDF (type: {content_type})")
                return {'success': False, 'url': url, 'error': f'Type non-PDF: {content_type}'}
            
            filename = f'document_{str(idx).zfill(6)}.pdf'
            if url.split('/')[-1]:
                try:
                    url_filename = url.split('/')[-1].split('?')[0]
                    if url_filename:
                        filename = secure_filename(url_filename)
                        if not filename.lower().endswith('.pdf'):
                            filename += '.pdf'
                        filename = f"{str(idx).zfill(6)}_{filename}"
                except Exception as e:
                    logger.debug(f"Nom de fichier par défaut pour {idx}: {e}")
            
            file_path = os.path.join(temp_dir, filename)
            
            total_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            if total_size < 100:
                os.remove(file_path)
                return {'success': False, 'url': url, 'error': 'Fichier trop petit (probablement vide)'}
            
            logger.info(f"Téléchargement {idx} réussi: {filename} ({total_size} bytes)")
            return {'success': True, 'url': url, 'filename': filename, 'size': total_size}
            
        except requests.exceptions.Timeout:
            error_msg = 'Timeout de connexion'
            logger.warning(f"Timeout pour {idx}: {url[:100]}")
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 10)
                logger.info(f"Nouvelle tentative dans {wait_time}s")
                time.sleep(wait_time)
            else:
                return {'success': False, 'url': url, 'error': error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f'Erreur réseau: {str(e)[:100]}'
            logger.warning(f"Erreur réseau pour {idx}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 10)
                time.sleep(wait_time)
            else:
                return {'success': False, 'url': url, 'error': error_msg}
                
        except Exception as e:
            error_msg = f'Erreur: {str(e)[:100]}'
            logger.error(f"Erreur inattendue pour {idx}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = min(2 ** attempt, 10)
                time.sleep(wait_time)
            else:
                return {'success': False, 'url': url, 'error': error_msg}
        finally:
            if response:
                response.close()
    
    return {'success': False, 'url': url, 'error': 'Max retries atteint'}

def download_pdfs_and_zip(urls, temp_folder, max_workers=5, batch_size=20, session_id=None):
    """Télécharge des PDFs en parallèle avec batching optimisé pour 1000+ documents"""
    temp_dir = os.path.join(temp_folder, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    successful = 0
    failed = 0
    failed_urls = []
    total_urls = len(urls)
    total_batches = (total_urls + batch_size - 1) // batch_size
    
    if session_id:
        progress_manager.update(session_id, 
            status='downloading',
            total=total_urls,
            batch_total=total_batches,
            message=f'Téléchargement de {total_urls} PDFs en {total_batches} lots de {batch_size}...'
        )
    
    logger.info(f"Début du téléchargement de {total_urls} PDFs avec {max_workers} workers, batch_size={batch_size}")
    logger.info(f"Traitement en {total_batches} batchs")
    
    for batch_start in range(0, total_urls, batch_size):
        batch_end = min(batch_start + batch_size, total_urls)
        batch_urls = urls[batch_start:batch_end]
        batch_num = batch_start // batch_size + 1
        
        if session_id:
            progress_manager.update(session_id,
                batch_current=batch_num,
                message=f'Traitement du lot {batch_num}/{total_batches} (URLs {batch_start+1} à {batch_end})'
            )
        
        logger.info(f"Traitement batch {batch_num}: URLs {batch_start+1} à {batch_end}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(download_single_pdf, url, idx, temp_dir): (url, idx) 
                for idx, url in enumerate(batch_urls, batch_start + 1)
            }
            
            for future in as_completed(future_to_url):
                result = future.result()
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                    failed_urls.append({'url': result['url'], 'error': result.get('error', 'Unknown error')})
                
                if session_id:
                    progress_manager.update(session_id,
                        current=successful + failed,
                        successful=successful,
                        failed=failed
                    )
        
        logger.info(f"Batch terminé: {successful} succès, {failed} échecs sur {batch_end} URLs traitées")
    
    if successful == 0:
        if session_id:
            progress_manager.update(session_id,
                status='error',
                message=f'Aucun PDF téléchargé avec succès. {failed} échecs.'
            )
        return {
            'success': False,
            'error': f'Aucun PDF téléchargé avec succès. {failed} échecs.'
        }
    
    if session_id:
        progress_manager.update(session_id,
            status='compressing',
            message=f'Compression de {successful} PDFs en fichier ZIP...'
        )
    
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
    
    if session_id:
        progress_manager.update(session_id,
            status='completed',
            message=f'Terminé! {successful} PDFs téléchargés avec succès, {failed} échecs.'
        )
    
    return {
        'success': True,
        'zip_path': zip_path,
        'filename': zip_filename,
        'total': len(urls),
        'successful': successful,
        'failed': failed,
        'failed_urls': failed_urls
    }
