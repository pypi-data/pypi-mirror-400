# Complio - Compliance-as-Code

[![Version Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Style de Code](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Vérifié](https://img.shields.io/badge/type%20checked-mypy-blue)](https://mypy-lang.org/)

```
 ██████╗ ██████╗ ███╗   ███╗██████╗ ██╗     ██╗ ██████╗
██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██║██╔═══██╗
██║     ██║   ██║██╔████╔██║██████╔╝██║     ██║██║   ██║
██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██║██║   ██║
╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗██║╚██████╔╝
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝ ╚═════╝
```

**Tests de conformité ISO 27001 automatisés pour infrastructure AWS**

Conçu pour les équipes DevSecOps qui ont besoin d'une surveillance continue de la conformité sans le travail manuel.

---

## 🎯 Qu'est-ce que Complio ?

Complio automatise les tests de conformité pour l'infrastructure cloud, vous aidant à :

- ✅ **Réussir les audits plus rapidement** - Collecte automatisée de preuves avec signatures cryptographiques
- ✅ **Réduire le travail manuel** - Surveillance continue de la conformité au lieu de sprints trimestriels
- ✅ **Détecter les problèmes tôt** - Scan en temps réel avec étapes de remédiation détaillées
- ✅ **Mettre à l'échelle la conformité** - Tester des centaines de ressources en parallèle sur plusieurs régions

**Couverture Actuelle** : 40 tests de conformité ISO 27001:2022 Annexe A
**Statut** : Couverture complète sur le chiffrement, le réseau, l'identité et la journalisation

---

## 🚀 Installation

### Via pip (Recommandé)

```bash
pip install complio
```

---

## ⚡ Démarrage Rapide

### 1. Configurer les Identifiants AWS

```bash
# Configuration interactive des identifiants (chiffrés avec AES-256)
complio configure

# Ou utiliser AWS CLI
aws configure
```

### 2. Activer la Licence

```bash
# Obtenir une licence Early Access sur https://compl.io/early-access
complio activate --license-key VOTRE-CLE-LICENCE

# Vérifier le statut de la licence
complio license
```

### 3. Lancer un Scan de Conformité

```bash
# Scanner tous les tests
complio scan

# Scanner un test spécifique
complio scan --test s3_encryption

# Scanner une région spécifique
complio scan --region eu-west-3

# Sauvegarder le rapport
complio scan --output rapport.json --format json
complio scan --output rapport.md --format markdown
```

**Exemple de Sortie :**

```
╔════════════════════════════════════════════════════════╗
║           Scan de Conformité Terminé                   ║
╚════════════════════════════════════════════════════════╝

Résumé
───────────────────────────────────────────────────────
Score Global :    92%  ✅ CONFORME
Total Tests :     40
Réussis :         ✅ 37
Échoués :         ❌ 3
Temps d'Exécution : 4.2s

Résultats par Catégorie
───────────────────────────────────────────────────────
🔐 Chiffrement & Sécurité des Données  (12/12) 100%  ✅
🌐 Sécurité Réseau                     (9/11)  82%   ⚠️
👤 Gestion Identité & Accès            (7/7)   100%  ✅
📊 Journalisation & Surveillance       (9/10)  90%   ✅
```

---

## 📦 Fonctionnalités

### Capacités Principales

- 🔒 **Gestion Sécurisée des Identifiants** - Stockage chiffré AES-256 avec dérivation de clé PBKDF2
- 🔍 **Tests de Conformité** - 40 tests automatisés ISO 27001:2022 Annexe A
- 📊 **Rapports de Preuves** - Rapports JSON et Markdown avec preuves signées SHA-256
- ⚡ **Exécution Parallèle** - Exécuter plusieurs tests simultanément (10x plus rapide)
- 🎨 **CLI Enrichie** - Belle sortie terminal avec barres de progression
- 🌍 **Multi-Région** - Scanner sur plusieurs régions AWS
- 👥 **Multi-Profil** - Gérer plusieurs comptes AWS
- 🛡️ **Sécurité Entreprise** - Licences signées HMAC, prévention traversée de chemin, limitation de débit

### Couverture Complète des Tests (40 Tests)

#### 🔐 Chiffrement & Sécurité des Données (12 tests)

| # | Test | Contrôle ISO 27001 | Description |
|---|------|-------------------|-------------|
| 1 | **Chiffrement Bucket S3** | A.8.2 | Valide le chiffrement des buckets S3 (AES-256, KMS) |
| 2 | **Versioning S3** | A.8.13 | Vérifie le versioning des buckets S3 pour la récupération de données |
| 3 | **Chiffrement Volume EBS** | A.8.2 | Vérifie le chiffrement au repos des volumes EBS |
| 4 | **Chiffrement Instance RDS** | A.8.2 | Valide le chiffrement des bases de données RDS |
| 5 | **Chiffrement DynamoDB** | A.8.2 | Vérifie le chiffrement des tables DynamoDB (KMS) |
| 6 | **Chiffrement ElastiCache** | A.8.24 | Vérifie le chiffrement Redis/Memcached au repos et en transit |
| 7 | **Chiffrement Redshift** | A.8.24 | Valide le chiffrement des clusters Redshift |
| 8 | **Chiffrement EFS** | A.8.11 | Vérifie le chiffrement des systèmes de fichiers EFS |
| 9 | **Chiffrement Backup** | A.8.24 | Vérifie le chiffrement des coffres AWS Backup |
| 10 | **Chiffrement Secrets Manager** | A.8.2 | Valide le chiffrement KMS de Secrets Manager |
| 11 | **Chiffrement Topic SNS** | A.8.24 | Vérifie le chiffrement des topics SNS avec KMS |
| 12 | **Chiffrement Logs CloudWatch** | A.8.24 | Vérifie le chiffrement des groupes de logs CloudWatch |

#### 🌐 Sécurité Réseau (11 tests)

| # | Test | Contrôle ISO 27001 | Description |
|---|------|-------------------|-------------|
| 13 | **Groupes de Sécurité EC2** | A.8.20 | Détecte les règles trop permissives (SSH, RDP, bases de données) |
| 14 | **ACLs Réseau** | A.8.20 | Valide la configuration des règles NACL et bonnes pratiques |
| 15 | **Sécurité NACL** | A.8.5 | Validation supplémentaire de sécurité NACL |
| 16 | **Logs de Flux VPC** | A.8.15 | Vérifie que les logs de flux VPC sont activés pour la surveillance réseau |
| 17 | **Blocage Accès Public S3** | A.8.22 | Vérifie les paramètres de blocage d'accès public des buckets S3 |
| 18 | **Sécurité ALB/NLB** | A.8.22 | Valide la configuration HTTPS/TLS des load balancers |
| 19 | **Configuration WAF** | A.8.20 | Vérifie les règles WAF WebACL et la journalisation |
| 20 | **HTTPS CloudFront** | A.8.24 | Force HTTPS pour les distributions CloudFront |
| 21 | **Sécurité API Gateway** | A.8.22 | Valide l'authentification, la limitation et WAF d'API Gateway |
| 22 | **Sécurité VPN** | A.8.22 | Vérifie le chiffrement et la configuration des tunnels VPN |
| 23 | **Sécurité Transit Gateway** | A.8.22 | Valide les paramètres de sécurité Transit Gateway |
| 24 | **Sécurité Endpoints VPC** | A.8.22 | Vérifie les politiques des endpoints VPC et DNS Privé |
| 25 | **Network Firewall** | A.8.20 | Vérifie le déploiement d'AWS Network Firewall |
| 26 | **Sécurité Direct Connect** | A.8.22 | Vérifie le chiffrement MACsec de Direct Connect |

#### 👤 Gestion Identité & Accès (7 tests)

| # | Test | Contrôle ISO 27001 | Description |
|---|------|-------------------|-------------|
| 27 | **Politique Mot de Passe IAM** | A.9.4.3 | Valide les exigences de mot de passe (longueur, complexité, expiration) |
| 28 | **Application MFA** | A.9.4.3 | Vérifie que MFA est activé pour les utilisateurs IAM |
| 29 | **Protection Compte Root** | A.9.2.1 | Vérifie le MFA du compte root et la rotation des clés d'accès |
| 30 | **Rotation Clés d'Accès IAM** | A.9.2.4 | Valide l'âge des clés d'accès IAM (max 90 jours) |
| 31 | **Rotation Clés KMS** | A.8.24 | Vérifie la rotation des clés KMS gérées par le client |

#### 📊 Journalisation & Surveillance (10 tests)

| # | Test | Contrôle ISO 27001 | Description |
|---|------|-------------------|-------------|
| 32 | **Journalisation CloudTrail** | A.8.15 | Vérifie que CloudTrail multi-région est activé |
| 33 | **Validation Logs CloudTrail** | A.8.16 | Vérifie que la validation des fichiers de logs CloudTrail est activée |
| 34 | **Chiffrement CloudTrail** | A.8.24 | Valide le chiffrement des logs CloudTrail avec KMS |
| 35 | **Rétention Logs CloudWatch** | A.8.15 | S'assure que les groupes de logs ont des politiques de rétention (90+ jours) |
| 36 | **Alarmes CloudWatch** | A.8.16 | Vérifie la configuration des alarmes CloudWatch |
| 37 | **AWS Config Activé** | A.8.16 | Vérifie qu'AWS Config enregistre les changements de configuration |
| 38 | **GuardDuty Activé** | A.8.16 | Vérifie la détection de menaces GuardDuty (S3, EKS, Malware) |
| 39 | **Security Hub Activé** | A.8.16 | Valide Security Hub pour la surveillance sécurité centralisée |
| 40 | **Règles EventBridge** | A.8.16 | Vérifie les règles EventBridge pour les événements de sécurité critiques |

**Tous les tests mappés aux contrôles ISO 27001:2022 (A.8.x, A.9.x)**

### Récemment Complété

- ✅ **Phase 3 (20 tests)** : Tests de conformité avancés complétés
  - Sécurité réseau (WAF, API Gateway, VPN, Transit Gateway)
  - Chiffrement avancé (Backup, SNS, CloudWatch Logs)
  - Surveillance (GuardDuty, Security Hub, EventBridge)
  - Stockage (versioning S3, ElastiCache, Redshift)

### Prochainement

- 📊 **Rapports PDF** - Résumés exécutifs avec graphiques et analyse de tendances
- 📧 **Notifications Email** - Scans planifiés avec alertes automatisées
- 🛡️ **Framework SOC 2** - Tests de conformité Type I et Type II
- 📉 **Tendances Historiques** - Suivre les scores de conformité dans le temps
- 🔄 **Intégration CI/CD** - Plugins GitHub Actions, GitLab CI, Jenkins
- 🌍 **Multi-Cloud** - Support Azure et GCP

---

## 💰 Tarification

### Early Access - Limité à 50 Fondateurs

|  | Early Access (Fondateur) | Prix Regular |
|---|------------------------|---------------|
| **Mensuel** | €99 | €299 |
| **Annuel** | €1,188 | €3,588 |
| **Économies** | **€2,400/an** | — |

### Ce Qui Est Inclus

✅ Tous les 40 tests de conformité ISO 27001:2022
✅ Toutes les fonctionnalités sortant dans les 6 prochaines semaines
✅ Comptes AWS illimités
✅ Exécutions de tests illimitées
✅ Rapports JSON, Markdown et PDF
✅ Support prioritaire

### Avantages Fondateurs 🏆

- 💰 **Prix verrouillé à €99/mois pendant 6 mois**
- 🏆 **Badge fondateur** sur votre profil
- 🎯 **Demandes de fonctionnalités prioritaires** - Influence directe sur la roadmap
- 💬 **Canal Slack direct** avec l'équipe


### Obtenir l'Early Access

📧 **Email** : andy.piquionne@complio.tech
🌐 **Site Web** : https://complio.tech/

Limité aux **5 premiers clients** seulement. Le prix passe à €299/mois après le lancement.

---

## 🔐 Sécurité

Complio est construit avec des principes de sécurité d'abord :

- **Chiffré au Repos** : Chiffrement AES-256 pour tous les identifiants
- **Dérivation de Clé** : PBKDF2 avec 480 000 itérations (recommandé OWASP)
- **Permissions Sécurisées** : Tous les fichiers de config configurés à `chmod 600` (propriétaire uniquement)
- **Zéro Journalisation** : Les identifiants ne sont jamais journalisés, filtrés de toutes les sorties
- **Lecture Seule** : Nécessite seulement des permissions de lecture sur les ressources AWS
- **Preuves Signées** : Signatures cryptographiques SHA-256 pour détection de falsification
- **Prévention Traversée de Chemin** : Validation stricte sur toutes les opérations de fichiers
- **Limitation de Débit** : Protection côté client contre les attaques par force brute
- **Vérification HMAC** : Vérification cryptographique pour validation de licence (intégration backend en attente)

**Audit de Sécurité** : Toutes les vulnérabilités critiques corrigées (3 CRITIQUE, 2 MOYEN résolus)

---

## 📚 Documentation

- **[Guide d'Installation](docs/INSTALLATION.md)** - Instructions d'installation détaillées
- **[Démarrage Rapide](QUICKSTART.md)** - Commencer en 5 minutes
- **[Guide de Tests](TESTING_GUIDE.md)** - Documentation de tests complète
- **[Guide de Licence](docs/LICENSING.md)** - Activation et gestion de licence
- **[Guide de Développement](docs/DEVELOPMENT.md)** - Contribution et MODE DEV
- **[Audit de Sécurité](SECURITY_AUDIT.md)** - Évaluation et corrections de sécurité
- **[Audit de Dépendances](DEPENDENCY_AUDIT.md)** - Revue de sécurité des dépendances

---

## 📊 Statut du Développement

**Phase Actuelle** : Semaine 5/10 - 40 Tests Complétés ✅
**Statut** : ✅ Couverture complète des tests de conformité ISO 27001:2022 opérationnelle

### Jalons Complétés

- ✅ **Semaine 1** : Chiffrement et stockage sécurisés des identifiants
- ✅ **Semaine 2** : CLI interactive avec sortie terminal enrichie
- ✅ **Semaine 3** : Connecteur AWS avec intégration boto3
- ✅ **Semaine 4** :
  - 4 tests de conformité initiaux (S3, EC2, IAM, CloudTrail)
  - Exécuteur de tests avec exécution parallèle
  - Génération de rapports (JSON et Markdown)
  - CLI enrichie avec barres de progression
  - Système de licence Early Access
- ✅ **Semaine 5** :
  - **Phase 1** : 4 tests fondamentaux
  - **Phase 2** : 8 tests principaux (stockage, sécurité, identité)
  - **Phase 3** : 20 tests avancés (réseau, chiffrement, surveillance)
  - **Total** : 40 tests de conformité ISO 27001:2022
  - Audit de sécurité et corrections de vulnérabilités critiques
  - Suite de tests complète (160+ tests)

**Couverture de Tests** : 160+ tests réussis (40 conformité + 33 sécurité + tests unitaires/intégration)

### Roadmap

- **Semaine 6** : Génération de rapports PDF avec graphiques
- **Semaine 7** : Notifications email et planification
- **Semaine 8** : Framework de conformité SOC 2
- **Semaine 9** : Analyse de tendances historiques
- **Semaine 10** : Intégration CI/CD et support multi-cloud

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

---

## 🙏 Support

- **Email** : andy.piquonne@complio.tech

---

## ⭐ Montrez Votre Soutien

Si vous trouvez Complio utile, vous pouvez :

- ⭐ Mettre une étoile au dépôt
- 🐦 Partager sur les réseaux sociaux
- 📝 Écrire un article de blog ou tutoriel
- 🎯 Devenir un fondateur Early Access

