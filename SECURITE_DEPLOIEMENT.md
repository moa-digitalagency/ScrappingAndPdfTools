# 🔒 Guide de Déploiement Sécurisé

## ⚠️ IMPORTANT: Sécurité des Clés API

**NE JAMAIS** mettre vos clés API directement dans les scripts ou les fichiers commités dans Git!

## 📋 Instructions de Déploiement

### 1. Sur votre VPS, clonez le projet

```bash
git clone <votre-repo-url>
cd <nom-du-projet>
```

### 2. Exécutez le script de déploiement

```bash
chmod +x deploy_vps.sh
./deploy_vps.sh
```

### 3. Configurez le fichier .env

Le script créera un fichier `.env`. Vous DEVEZ le modifier avec vos vraies clés:

```bash
nano .env
```

Remplacez `VOTRE_CLE_API_ICI` par votre vraie clé OpenRouter:

```
OPENROUTER_API_KEY=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
```

### 4. Relancez le déploiement

```bash
./deploy_vps.sh
```

## 🔐 Pourquoi cette approche est sécurisée?

1. **Le fichier .env n'est PAS commité dans Git** (grâce au .gitignore)
2. **Chaque environnement a sa propre configuration** (dev, staging, production)
3. **Les clés restent sur le serveur** et ne sont jamais exposées dans le code
4. **Vous pouvez partager le code** sans exposer vos secrets

## 📝 Checklist de Sécurité

- [ ] Le fichier `.env` est dans `.gitignore`
- [ ] Les clés API ne sont jamais dans le code
- [ ] Chaque environnement a son propre fichier `.env`
- [ ] Les clés sont générées avec des permissions appropriées
- [ ] Le fichier `.env` a les bonnes permissions: `chmod 600 .env`

## 🚀 Déploiement Automatique (CI/CD)

Si vous utilisez un système CI/CD (GitHub Actions, GitLab CI, etc.), utilisez les secrets du système:

- **GitHub**: Settings > Secrets and variables > Actions
- **GitLab**: Settings > CI/CD > Variables
- **Replit**: Utiliser Replit Secrets

## 📞 Besoin d'aide?

Consultez la documentation de votre service:
- OpenRouter: https://openrouter.ai/docs
- Flask: https://flask.palletsprojects.com/
