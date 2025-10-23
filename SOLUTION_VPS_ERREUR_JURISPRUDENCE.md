# Solution pour l'erreur JSON sur VPS - Extraction Jurisprudence

## Problème
Lors de l'analyse de 200 PDFs de jurisprudence, vous obtenez l'erreur:
```
Erreur de connexion: Unexpected token '<', "<html> <h"... is not valid JSON
```

Cette erreur signifie que l'API OpenRouter renvoie du HTML (une page d'erreur) au lieu de JSON, car vous atteignez les **limites de taux** (rate limits).

## Solution 1: Réduire le nombre de requêtes parallèles (RAPIDE ✅)

Sur votre VPS, modifiez le fichier `app/services/pdf_jurisprudence_extractor.py`:

**Ligne 337** - Changez:
```python
with ThreadPoolExecutor(max_workers=3) as executor:
```

En:
```python
with ThreadPoolExecutor(max_workers=1) as executor:
```

Cela réduira les requêtes parallèles de 3 à 1, évitant ainsi de surcharger l'API.

## Solution 2: Ajouter des délais entre les requêtes (RECOMMANDÉ ✅✅)

Dans le fichier `app/services/pdf_jurisprudence_extractor.py`:

**En haut du fichier** (après les autres imports, vers ligne 20), ajoutez:
```python
import time
```

**Ligne 160** (juste après `jurisprudence_data = extract_jurisprudence_data_with_ai(...)`), ajoutez:
```python
jurisprudence_data = extract_jurisprudence_data_with_ai(text, filename, api_key, pdf_path, num_pages)

# NOUVEAU: Ajouter un délai pour éviter de surcharger l'API
time.sleep(2)  # Pause de 2 secondes entre chaque requête

return {
```

## Solution 3: Améliorer la gestion d'erreur (TRÈS RECOMMANDÉ ✅✅✅)

Dans `app/services/pdf_jurisprudence_extractor.py`, **remplacez les lignes 91-100** par:

```python
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90
        )
        response.raise_for_status()
        
        # Vérifier si la réponse est du JSON valide
        try:
            result = response.json()
        except json.JSONDecodeError:
            # La réponse n'est pas du JSON (probablement du HTML)
            error_preview = response.text[:500] if len(response.text) > 500 else response.text
            logger.error(f"Réponse non-JSON de l'API: {error_preview}")
            raise Exception(f"L'API a renvoyé une réponse invalide (HTML au lieu de JSON). Cela indique probablement une limite de taux atteinte. Essayez de réduire le nombre de PDFs analysés simultanément ou ajoutez des délais entre les requêtes.")
        
        # Vérifier que la structure de la réponse est correcte
        if 'choices' not in result or not result['choices']:
            error_msg = result.get('error', {}).get('message', 'Structure de réponse invalide')
            raise Exception(f"Erreur de l'API OpenRouter: {error_msg}")
        
        ai_response = result['choices'][0]['message']['content']
```

## Solution 4: Traiter par lots plus petits (MEILLEURE PRATIQUE ✅✅✅)

Au lieu d'analyser 200 PDFs d'un coup, faites plusieurs sessions:
- Session 1: 50 PDFs → Analyser → Télécharger le résultat
- Session 2: 50 PDFs → Analyser → Télécharger le résultat
- Session 3: 50 PDFs → Analyser → Télécharger le résultat
- Session 4: 50 PDFs → Analyser → Télécharger le résultat

Ensuite, fusionnez les 4 fichiers Excel/CSV.

## Solution Combinée ULTIME 🎯

Pour de meilleurs résultats, combinez les solutions:

1. ✅ Réduisez `max_workers` à 1 (ligne 337)
2. ✅ Ajoutez `time.sleep(2)` après chaque extraction (ligne 160)
3. ✅ Améliorez la gestion d'erreur (lignes 91-100)
4. ✅ Traitez par lots de 30-50 PDFs maximum

## Comment appliquer les changements sur votre VPS

1. **Connectez-vous à votre VPS via SSH**

2. **Naviguez vers le dossier de votre application**
```bash
cd /chemin/vers/votre/application
```

3. **Éditez le fichier**
```bash
nano app/services/pdf_jurisprudence_extractor.py
```

4. **Appliquez les modifications** (Solutions 1, 2 et 3 ci-dessus)

5. **Sauvegardez** (Ctrl+O puis Entrée, puis Ctrl+X pour quitter nano)

6. **Redémarrez votre application**
```bash
# Si vous utilisez systemd
sudo systemctl restart votre-app

# Ou si vous utilisez PM2
pm2 restart votre-app

# Ou si vous utilisez gunicorn directement
pkill gunicorn
gunicorn --bind 0.0.0.0:votre-port main:app
```

## Vérification des crédits OpenRouter

Il est aussi possible que vous ayez épuisé votre quota/crédit API:

1. Allez sur https://openrouter.ai/
2. Connectez-vous à votre compte
3. Vérifiez votre solde et vos limites
4. Rechargez votre compte si nécessaire

## Résumé

L'erreur vient du fait que vous envoyez **trop de requêtes trop rapidement** à l'API OpenRouter. La solution est de:
- Réduire les workers parallèles (1 au lieu de 3)
- Ajouter des pauses entre les requêtes (2 secondes)
- Traiter par lots plus petits (30-50 PDFs au lieu de 200)

Avec ces changements, vous devriez pouvoir analyser vos PDFs sans erreur.
