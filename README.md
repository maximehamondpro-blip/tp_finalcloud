# ☁️ Projet Final Cloud & DevOps : Convertisseur d'Images Serverless

Ce dépôt contient l'infrastructure complète et le code source d'une application Cloud orientée événements (Event-Driven), déployée sur Amazon Web Services (AWS) via Terraform et GitHub Actions.

## 🌟 Architecture du Projet

L'objectif de cette infrastructure est de fournir un service de conversion d'images (vers PDF) entièrement **Serverless**, hautement disponible et sécurisé.

1. **Source S3** : L'utilisateur dépose une image (`.png` ou `.jpg`) dans un bucket AWS S3.
2. **Déclencheur (Trigger)** : Cet événement déclenche automatiquement une fonction AWS Lambda.
3. **AWS Lambda (Python)** : La fonction récupère l'image, la traite entièrement en mémoire via un script natif (sans dépendances lourdes comme `Pillow` pour supprimer le "Cold Start"), et génère un fichier PDF.
4. **Destination S3** : Le PDF résultant est sauvegardé dans un bucket de destination séparé.

## 🛠️ Stack Technique & Choix DevOps

* **Infrastructure as Code (IaC)** : Terraform gère l'intégralité du cycle de vie des ressources cloud.
* **Remote Backend S3** : L'état Terraform (`terraform.tfstate`) est stocké sur un bucket S3 dédié, ce qui permet à la pipeline CI/CD d'être "Stateful" et de ne pas recréer l'architecture à chaque exécution.
* **Continuous Deployment (CI/CD)** : GitHub Actions orchestre le linting, l'analyse de sécurité (SAST avec Checkov), le packaging du code (via `zip`), et le déploiement sur AWS.
* **Sécurité Dynamique (IAM)** : L'authentification GitHub -> AWS se fait via le principe d'AssumeRole (`sts:AssumeRole`) en passant par l'action aws-credentials, ce qui garantit qu'aucune clé ou ARN n'est codé en dur dans les fichiers Terraform.

## 📂 Structure du Répertoire

.
├── .github/workflows/   # Définition de la pipeline CI/CD (main.yml)
├── ansible/             # Scripts de configuration et linting
├── src/                 # Code source Python de la fonction Lambda (handler.py)
├── terraform/           # Fichiers de déclaration d'infrastructure
│   ├── modules/         # Modules Terraform réutilisables (s3, lambda)
│   ├── main.tf          # Point d'entrée orchestrant les modules
│   ├── providers.tf     # Configuration du provider AWS et Remote Backend
│   └── variables.tf     # Variables paramétrables (Noms de buckets, région)
├── README.md            # Ce fichier
├── guide_soutenance.md  # Guide pas à pas pour la présentation orale
├── explication_fichiers.md # Détail technique du rôle de chaque fichier
└── presentation_technique.md # Cheat-Sheet pour justifier les choix d'architecture

## 🚀 Comment déployer manuellement ?

Si vous souhaitez déployer cette infrastructure depuis votre poste de travail (après vous être authentifié sur l'AWS CLI) :

cd terraform
# 1. Initialiser le projet et lier le Remote Backend S3
terraform init

# 2. Prévisualiser les modifications
terraform plan

# 3. Appliquer le déploiement
terraform apply -auto-approve

## 🧪 Comment tester l'architecture ?

# Uploader une image de test dans le bucket source
aws s3 cp mon_image.png s3://ynov-iac-2025-source-mh/

# Vérifier quelques secondes plus tard la présence du PDF converti
aws s3 ls s3://ynov-iac-2025-dest-mh/

# Télécharger le résultat
aws s3 cp s3://ynov-iac-2025-dest-mh/mon_image.pdf .

---
*Projet réalisé dans le cadre de l'évaluation Cloud & IAC (Infrastructure as Code).*
