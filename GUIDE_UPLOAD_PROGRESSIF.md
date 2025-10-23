# Guide d'Utilisation - Upload Progressif Jurisprudence

## 🎯 Nouvelle Méthode d'Upload

Pour éviter l'erreur 413 "Request Entity Too Large", nous avons implémenté un système d'**upload progressif par lots**.

## ✨ Comment ça fonctionne

### Étape 1: Configuration de la session

1. Accédez à `/jurisprudence`
2. Entrez le **nombre total de PDFs** que vous souhaitez analyser (ex: 100)
3. Donnez un **nom à votre session** (optionnel, ex: "Jurisprudence Mars 2024")
4. Cliquez sur **"Démarrer la session"**

Le système vous donne un **ID de session** que vous pouvez noter pour reprendre plus tard.

### Étape 2: Upload par lots

1. Sélectionnez **un ou plusieurs PDFs** à uploader
2. Cliquez sur **"Ajouter ces PDFs"**
3. Les fichiers sont uploadés **un par un automatiquement**
4. Une **barre de progression** vous montre l'avancement

**Avantages:**
- ✅ Pas de limite de taille de fichier unique
- ✅ Upload fichier par fichier (évite l'erreur 413)
- ✅ Vous pouvez uploader par petits lots
- ✅ Progression sauvegardée en temps réel

### Étape 3: Reprendre une session (optionnel)

Si vous fermez la page ou devez interrompre:

1. Notez votre **ID de session**
2. Plus tard, retournez sur `/jurisprudence`
3. Entrez l'ID dans **"Reprendre une session existante"**
4. Cliquez sur **"Reprendre"**
5. Continuez à uploader là où vous vous étiez arrêté

### Étape 4: Lancer l'analyse

1. Quand tous vos PDFs sont uploadés, le bouton **"Terminer et lancer l'analyse"** s'active
2. Vous pouvez aussi lancer l'analyse **avant d'atteindre le nombre total** si vous changez d'avis
3. L'analyse démarre et traite tous les PDFs uploadés
4. Téléchargez les résultats en **Excel** ou **CSV**

## 📊 Exemple Pratique

**Scénario:** Vous avez 200 PDFs de jurisprudence à analyser

```
1. Créer session: "200 PDFs total, nom: Jurisprudence 2024"
   → ID session: abc-123-xyz

2. Premier lot: Uploader 50 PDFs
   → Progression: 50/200 (25%)

3. Deuxième lot: Uploader 50 PDFs
   → Progression: 100/200 (50%)

4. Pause: Fermer la page, noter l'ID session

5. Reprendre: Entrer abc-123-xyz
   → Progression: 100/200 (50%)

6. Troisième lot: Uploader 50 PDFs
   → Progression: 150/200 (75%)

7. Quatrième lot: Uploader 50 PDFs
   → Progression: 200/200 (100%)

8. Terminer: Lancer l'analyse
   → Traitement de 200 PDFs
   → Télécharger Excel/CSV
```

## 🔐 Sécurité

- Chaque fichier reçoit un **nom unique** (UUID) pour éviter les collisions
- Les **fichiers temporaires** sont nettoyés après l'analyse
- Les **sessions** sont stockées en mémoire serveur

## ⚠️ Important

### Configuration requise

Pour que la fonctionnalité fonctionne, vous devez configurer la clé API OpenRouter:

1. **Sur Replit:** Onglet "Secrets" (icône cadenas)
   - Clé: `OPENROUTER_API_KEY`
   - Valeur: Votre clé API OpenRouter

2. **Sur VPS:** Fichier `.env`
   ```env
   OPENROUTER_API_KEY=sk-or-v1-votre-cle-ici
   ```

### Obtenir une clé API

1. Visitez [openrouter.ai](https://openrouter.ai)
2. Créez un compte gratuit
3. Générez une clé API
4. Ajoutez-la dans les secrets/env

## 🆚 Ancienne vs Nouvelle Méthode

| Ancienne Méthode | Nouvelle Méthode |
|------------------|------------------|
| Upload 1 gros fichier ZIP | Upload PDFs un par un |
| Limite 500 MB (erreur 413) | Aucune limite pratique |
| Tout ou rien | Upload progressif |
| Pas de reprise possible | Session récupérable |
| Upload unique | Upload par lots |

## 🎉 Avantages

1. **Plus de limite de taille**: Uploadez autant de PDFs que vous voulez
2. **Flexibilité**: Uploadez à votre rythme, par petits lots
3. **Récupération**: Reprenez où vous vous êtes arrêté
4. **Transparence**: Voir la progression en temps réel
5. **Fiabilité**: Pas d'erreur 413, upload stable

---

**Créé par:** MOA Digital Agency LLC  
**Contact:** moa@myoneart.com  
**Web:** www.myoneart.com
