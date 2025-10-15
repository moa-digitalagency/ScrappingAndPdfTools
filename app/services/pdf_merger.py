import os
import zipfile
import uuid
import logging
from datetime import datetime
from pypdf import PdfWriter, PdfReader
from app.services.pdf_analyzer import analyze_pdfs_and_create_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_pdfs_from_zip(zip_path, temp_folder):
    temp_dir = os.path.join(temp_folder, str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    
    extract_dir = os.path.join(temp_dir, 'extracted')
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        return {'success': False, 'error': f'Erreur lors de l\'extraction du ZIP: {str(e)}'}
    
    pdf_files = []
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    pdf_files.sort()
    
    if not pdf_files:
        return {'success': False, 'error': 'Aucun fichier PDF trouvé dans le ZIP'}
    
    merger = PdfWriter()
    pdf_metadata = []
    total_pages = 0
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        try:
            reader = PdfReader(pdf_file)
            num_pages = len(reader.pages)
            total_pages += num_pages
            
            for page in reader.pages:
                merger.add_page(page)
            
            pdf_metadata.append({
                'index': idx,
                'filename': os.path.basename(pdf_file),
                'pages': num_pages,
                'path': pdf_file
            })
            
        except Exception as e:
            pdf_metadata.append({
                'index': idx,
                'filename': os.path.basename(pdf_file),
                'pages': 0,
                'error': str(e)
            })
    
    unique_id = str(uuid.uuid4())[:8]
    pdf_filename = f'merged_{unique_id}.pdf'
    pdf_path = os.path.join(temp_folder, pdf_filename)
    
    with open(pdf_path, 'wb') as output_pdf:
        merger.write(output_pdf)
    
    merger.close()
    
    logger.info(f"Début de l'analyse intelligente de {len(pdf_files)} PDFs")
    analysis_result = analyze_pdfs_and_create_database(pdf_files, temp_folder)
    
    if not analysis_result.get('success'):
        logger.warning(f"Analyse intelligente échouée: {analysis_result.get('error')}")
        excel_path = None
        excel_filename = None
    else:
        excel_path = analysis_result['excel_path']
        excel_filename = analysis_result['excel_filename']
        logger.info(f"Analyse intelligente terminée: {excel_filename}")
    
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            try:
                os.rmdir(os.path.join(root, dir))
            except:
                pass
    try:
        os.rmdir(temp_dir)
    except:
        pass
    
    result = {
        'success': True,
        'pdf_path': pdf_path,
        'pdf_filename': pdf_filename,
        'total_pdfs': len(pdf_files),
        'total_pages': total_pages
    }
    
    if excel_path and excel_filename:
        result['excel_path'] = excel_path
        result['excel_filename'] = excel_filename
        result['has_analysis'] = True
    else:
        result['has_analysis'] = False
    
    return result
