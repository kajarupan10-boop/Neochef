# NeoChef PWA - Product Requirements Document

## Projet
Migration de l'application NeoChef PWA de gestion de restaurant vers Emergent Platform.

## Date de migration
7 Mars 2026

## Stack Technique
- **Frontend**: React Native/Expo (build web statique)
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB (fourni par Emergent)
- **Serveur statique**: Express.js

## Architecture
```
/app/
├── backend/
│   ├── server.py         # API FastAPI complète (560K lignes)
│   ├── dist/             # Build Expo statique (copié aussi dans frontend/build)
│   ├── models/           # Modèles MongoDB
│   ├── routes/           # Routes additionnelles
│   └── uploads/          # Fichiers uploadés
├── frontend/
│   ├── serve-static.js   # Serveur Express pour fichiers statiques
│   └── build/            # Build Expo statique
```

## Fonctionnalités Principales
1. ✅ Gestion de menus (Food/Drink)
2. ✅ Système de réservations
3. ✅ Génération de factures/devis PDF
4. ✅ Gestion multi-restaurants (Holding)
5. ✅ Menu public QR code
6. ✅ Système de permissions utilisateurs

## Ce qui a été implémenté
- [x] Clonage du repo GitHub
- [x] Installation des dépendances Python
- [x] Configuration du serveur Express pour servir le build Expo
- [x] Proxy des requêtes /api vers le backend FastAPI
- [x] Tests de validation (100% passés)

## URL de Production
https://017b3938-5597-48e9-b176-182bc317a58f.preview.emergentagent.com

## Tests effectués
- ✅ API /api/health - MongoDB connecté
- ✅ Page d'accueil avec 3 boutons principaux
- ✅ Fichiers statiques servis correctement
- ✅ Navigation fonctionnelle
- ✅ PWA configurée (Service Worker, Manifest)
- ✅ Responsive design

## Backlog / Améliorations futures
- P1: Déploiement sur environnement de production .emergent.host
- P2: Tests automatisés des flux utilisateurs complets
- P3: Monitoring et alertes

## Notes techniques
- Le frontend Emergent par défaut a été remplacé par un serveur Express qui sert le build Expo statique
- Les requêtes /api sont proxifiées vers le backend FastAPI sur le port 8001
