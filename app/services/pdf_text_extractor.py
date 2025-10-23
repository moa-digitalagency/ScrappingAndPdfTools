"""
PdfTools
MOA Digital Agency LLC
Service d'extraction de texte depuis des PDFs
"""

import os
import logging
from pypdf import PdfReader
from typing import Dict, List

logger = logging.getLogger(__name__)

class PdfTextExtractor:
    """Service pour extraire le texte de fichiers PDF"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Dict:
        """
        Extrait le texte d'un fichier PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Dict avec le texte extrait, nombre de pages, et métadonnées
        """
        try:
            reader = PdfReader(pdf_path)
            
            # Extraire le texte de toutes les pages
            full_text = ""
            page_texts = []
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                page_texts.append({
                    'page_number': i + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
                full_text += page_text + "\n\n"
            
            # Récupérer les métadonnées
            metadata = {}
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', ''),
                    'creation_date': reader.metadata.get('/CreationDate', ''),
                }
            
            return {
                'success': True,
                'text': full_text.strip(),
                'page_count': len(reader.pages),
                'pages': page_texts,
                'metadata': metadata,
                'total_chars': len(full_text),
                'total_words': len(full_text.split())
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de texte de {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def extract_text_from_multiple_pdfs(pdf_paths: List[str]) -> List[Dict]:
        """
        Extrait le texte de plusieurs fichiers PDF
        
        Args:
            pdf_paths: Liste des chemins vers les fichiers PDF
            
        Returns:
            Liste de dictionnaires avec les résultats d'extraction
        """
        results = []
        
        for pdf_path in pdf_paths:
            result = PdfTextExtractor.extract_text_from_pdf(pdf_path)
            result['file_path'] = pdf_path
            result['file_name'] = os.path.basename(pdf_path)
            results.append(result)
        
        return results
    
    @staticmethod
    def save_text_to_file(text: str, output_path: str) -> bool:
        """
        Sauvegarde le texte extrait dans un fichier
        
        Args:
            text: Texte à sauvegarder
            output_path: Chemin du fichier de sortie
            
        Returns:
            True si réussi, False sinon
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du texte: {e}")
            return False
