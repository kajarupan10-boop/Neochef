# NeoChef PWA - Product Requirements Document

## Original Problem Statement
Migration d'une application PWA existante nommée "NeoChef" pour la gestion de restaurants. L'objectif principal est d'obtenir une URL de production stable et permanente.

## Stack Technologique
- Frontend: React Native/Expo (build web statique)
- Backend: FastAPI (Python)
- Base de données: MongoDB

## Core Features

### 1. Gestion de base
- Gestion des menus
- Système de réservations
- Génération de factures PDF
- Gestion multi-restaurants (Holding)
- Menu public via QR code

### 2. Module Ardoise (A L'ARDOISE)
- Édition des plats du jour
- Suivi des quantités vendues par jour
- Rapports de ventes (PDF/Excel)
- Calendrier pour saisir/modifier les ventes des jours passés
- Suggestions IA basées sur l'historique
- Planification des ardoises des jours à venir
- Export du planning des ardoises futures

### 3. Système de Permissions (Nouveau - Mars 2026)
Permissions granulaires pour le module Ardoise :
- **Édition** : Accès oui/non + mode lecture seule ou modifier
- **Ventes** : Accès oui/non + mode lecture seule ou modifier
- **Rapports** : Accès oui/non + mode lecture seule ou modifier + Export PDF/Excel

## What's Been Implemented

### Session Mars 2026
- [x] Nouveau système de permissions Ardoise avec 3 sections (Édition, Ventes, Rapports)
- [x] Mode lecture seule vs modifier pour chaque section
- [x] Export PDF/Excel conditionné aux permissions
- [x] Espacement réduit sur l'écran "Rapport Ardoise"
- [x] Backend mis à jour avec nouveaux modèles de permissions
- [x] Synchronisation build frontend corrigée

### Sessions précédentes
- [x] Visibilité de l'ardoise sur le menu client
- [x] Interface de planification d'ardoise avec calendrier
- [x] Interface de suggestion de plats avec historique
- [x] Calendrier dans l'onglet des ventes
- [x] Correction des bugs PDF (apostrophes, format paysage)
- [x] Correction des problèmes de connexion utilisateur

## Prioritized Backlog

### P0 (Critique)
- [ ] Déployer en production les nouvelles fonctionnalités

### P1 (Important)
- [ ] Téléchargement PDF sur mobile iOS (implémenter navigator.share)
- [ ] Vérifier l'export du planning des ardoises

### P2 (Normal)
- [ ] Vérifier les traductions sur le menu client public

### P3 (Nice to have)
- [ ] Refactoriser index.tsx (~5000 lignes) en composants
- [ ] Automatiser le build/déploiement

## Key Files
- `/app/backend/server.py` - Backend FastAPI monolithique
- `/app/temp_clone/frontend/app/index.tsx` - Frontend React monolithique
- `/app/temp_clone/frontend/app/client/[restaurant_id].tsx` - Menu client public

## Database Schema
- `mep_restaurants`: { _id, name, share_token }
- `ardoise_items`: { restaurant_id, name, category }
- `ardoise_formula_prices`: { restaurant_id, name, price }
- `ardoise_sales_history`: { restaurant_id, date, service, sales }
- `planned_ardoises`: { restaurant_id, date, entrees, plats, desserts }
- `translations`: { key, lang, value }

## Test Credentials
- Email: groupenaga@gmail.com
- Restaurant: Le Cercle
- Password: LeCercle123!

## URLs
- Preview: https://neochef-ardoise.preview.emergentagent.com
- Production: https://neochef-pwa-2.emergent.host (ancien, à mettre à jour)
