"""
Script de test pour l'extraction de jurisprudence
"""
import os
from app.services.pdf_jurisprudence_extractor_rule_based import JurisprudenceExtractor

# Tester avec le PDF fourni
pdf_path = "attached_assets/document_000001(1)_1761257159351.pdf"

if os.path.exists(pdf_path):
    print(f"📄 Test d'extraction sur: {pdf_path}")
    print("=" * 80)
    
    # Extraire le texte
    text = JurisprudenceExtractor.extract_text_from_pdf(pdf_path)
    if text:
        print(f"✓ Texte extrait: {len(text)} caractères")
        print("\nPremières lignes du texte:")
        print(text[:500])
        print("\n" + "=" * 80)
        
        # Extraire les données structurées
        data = JurisprudenceExtractor.extract_jurisprudence_data(text, os.path.basename(pdf_path))
        
        print("\n📊 DONNÉES EXTRAITES:")
        print("=" * 80)
        for key, value in data.items():
            if len(str(value)) > 200:
                print(f"{key}: {str(value)[:200]}...")
            else:
                print(f"{key}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ Extraction terminée avec succès!")
        
        # Créer un fichier Excel de test
        temp_folder = "tmp"
        os.makedirs(temp_folder, exist_ok=True)
        
        result = JurisprudenceExtractor.extract_from_single_pdf(
            pdf_path,
            temp_folder,
            os.path.basename(pdf_path),
            'excel'
        )
        
        if result['success']:
            print(f"\n📁 Fichier Excel créé: {result['filename']}")
            print(f"📍 Chemin: {result['output_path']}")
        else:
            print(f"\n❌ Erreur création Excel: {result.get('error')}")
    else:
        print("❌ Erreur: Impossible d'extraire le texte du PDF")
else:
    print(f"❌ Fichier non trouvé: {pdf_path}")
