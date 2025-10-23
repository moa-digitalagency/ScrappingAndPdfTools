# Correction de l'erreur JSON lors de l'analyse de jurisprudence

## Problème identifié

Lors de l'analyse de 200 PDFs de jurisprudence sur votre VPS, vous avez rencontré l'erreur suivante:

```
Erreur de connexion : jeton inattendu « < », « <html> » <h>... n'est pas un JSON valide
```

## Cause du problème

Cette erreur se produit lorsque l'API OpenRouter renvoie du HTML au lieu de JSON. Cela arrive généralement dans les cas suivants:

1. **Limite de taux atteinte** - Trop de requêtes en peu de temps
2. **Quota API dépassé** - Crédit épuisé ou limite mensuelle atteinte
3. **Erreur serveur** - L'API rencontre un problème temporaire
4. **Requête mal formée** - La requête n'est pas acceptée par l'API

Dans votre cas, avec 200 PDFs analysés, il est très probable que vous ayez atteint une **limite de taux** ou un **quota API**.

## Solution mise en place

J'ai amélioré la gestion des erreurs dans le fichier `app/services/pdf_jurisprudence_extractor.py`:

### Modifications apportées:

1. **Détection de réponses HTML**
   - Vérification si la réponse de l'API est du JSON valide avant de la parser
   - Si la réponse est du HTML, affichage d'un message d'erreur clair

2. **Validation de la structure de réponse**
   - Vérification que la réponse contient bien les champs attendus (`choices`, etc.)
   - Extraction des messages d'erreur fournis par l'API

3. **Messages d'erreur améliorés**
   - Les erreurs affichent maintenant un aperçu de la réponse HTML
   - Indication claire que le problème peut être lié au quota ou aux limites de taux

## Comment éviter ce problème à l'avenir

### 1. Limiter le nombre de requêtes parallèles

Dans `pdf_jurisprudence_extractor.py`, la ligne 337 limite déjà les workers à 3:

```python
with ThreadPoolExecutor(max_workers=3) as executor:
```

Vous pouvez réduire ce nombre à 1 ou 2 pour des traitements plus lents mais plus stables:

```python
with ThreadPoolExecutor(max_workers=1) as executor:
```

### 2. Ajouter des pauses entre les requêtes

Vous pouvez ajouter un délai entre chaque requête en modifiant la fonction `extract_jurisprudence_data_with_ai`:

```python
import time

# Ajouter après la requête (ligne 100)
time.sleep(1)  # Pause d'1 seconde entre chaque requête
```

### 3. Vérifier vos crédits API

- Connectez-vous à votre compte OpenRouter
- Vérifiez votre quota et vos limites de taux
- Assurez-vous d'avoir suffisamment de crédit

### 4. Traiter par lots plus petits

Au lieu de traiter 200 PDFs d'un coup, divisez-les en lots de 20-50 PDFs:
- Upload 50 PDFs → Analyser
- Upload 50 PDFs suivants → Analyser
- Etc.

## Que faire si l'erreur se reproduit

1. **Vérifier votre quota API OpenRouter**
   - Peut-être besoin de recharger votre compte
   - Ou attendre la réinitialisation du quota mensuel

2. **Réduire le nombre de workers parallèles** (voir ci-dessus)

3. **Ajouter des délais entre les requêtes** (voir ci-dessus)

4. **Traiter par plus petits lots** (20-50 PDFs à la fois)

5. **Contacter le support OpenRouter** si le problème persiste

## État actuel du système

✅ L'application est maintenant configurée et fonctionnelle sur Replit
✅ La gestion des erreurs est améliorée pour mieux identifier les problèmes
✅ Le workflow est démarré et l'application écoute sur le port 5000

L'erreur affichera maintenant un message clair expliquant qu'il peut s'agir d'un problème de quota ou de limite de taux, avec un aperçu de la réponse de l'API.
