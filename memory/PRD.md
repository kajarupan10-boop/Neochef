# NeoChef - Product Requirements Document

## Overview
NeoChef est une application PWA de gestion de restaurants, permettant la gestion des menus, réservations, facturation et ardoise quotidienne.

## Stack Technique
- **Frontend**: Expo for Web (React Native Web)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Fonctionnalités Principales

### 1. Gestion des Menus
- Carte Food et Carte Boisson
- Sections personnalisables
- Prix et descriptions

### 2. Menu Client Public (QR Code)
- Accessible via `/client/{restaurant_id}`
- Affichage responsive mobile
- Filtre par allergènes
- Support multilingue

### 3. A L'ARDOISE (Menu du Jour)
- Lien partageable permanent (`/ardoise/{token}`)
- Édition des plats (Entrée, Plat, Dessert - 2 items chacun)
- **Prix des formules éditables** (Plat du jour, E+P, P+D, E+P+D)
- **Suivi des ventes** - Enregistrement des quantités vendues par service
- Export PDF

### 4. Réservations
- Gestion des créneaux
- Notifications

### 5. Facturation
- Génération de factures et devis PDF

## Architecture

```
/app
├── backend/
│   ├── server.py         # API FastAPI (~14k lignes)
│   └── dist/             # Build Expo Web statique
└── temp_clone/
    └── frontend/
        └── app/
            ├── index.tsx            # App principale
            ├── client/[restaurant_id].tsx  # Menu client public
            └── ardoise/[token].tsx         # Interface ardoise
```

## Collections MongoDB
- `users` - Utilisateurs
- `mep_restaurants` - Restaurants
- `mep_ardoise` - Données de l'ardoise (plats, prix formules)
- `mep_ardoise_sales` - Historique des ventes de l'ardoise
- `menu_restaurant_sections` - Sections du menu
- `menu_restaurant_items` - Articles du menu

## API Endpoints Clés

### Ardoise
- `GET /api/ardoise/public/{token}` - Récupérer l'ardoise
- `PUT /api/ardoise/public/{token}` - Mettre à jour l'ardoise (plats + formule_prices)
- `POST /api/ardoise/public/{token}/sales` - Enregistrer les ventes
- `GET /api/ardoise/sales` - Récupérer l'historique des ventes

### Menu Client
- `GET /api/restaurants/{id}/public` - Info restaurant public
- `GET /api/menu-restaurant/public/{id}` - Menu public

## Implémenté (09/03/2026)

### Bug Fixes
- ✅ Correction du bug "Restaurant non trouvé" sur les pages client
  - Cause: Double préfixe `/api/api/` dans les appels frontend
  - Solution: Routes dupliquées côté backend pour gérer le cache CDN

### Nouvelles Fonctionnalités Ardoise
- ✅ **Prix des formules éditables** - Les prix (Plat du jour, E+P, P+D, E+P+D) sont maintenant stockés en base et modifiables
- ✅ **Suivi des quantités vendues** - Nouveau champ `quantity_sold` pour chaque plat
- ✅ **Endpoint de sauvegarde des ventes** - `/api/ardoise/public/{token}/sales`
- ✅ **Collection `mep_ardoise_sales`** pour l'historique
- ✅ **Rapports de ventes** - Visualisation des statistiques par jour/semaine/mois
- ✅ **Export PDF** - Rapport complet des ventes avec détails par plat et par jour
- ✅ **Export Excel** - Fichier Excel avec 3 feuilles (Résumé, Par Plat, Par Jour)

### Frontend Ardoise Mis à Jour
- Boutons "Édition", "Ventes" et "Rapports" séparés
- Section édition des prix de formules avec icône stylo
- Mode "Ventes" pour saisir les quantités vendues
- Mode "Rapports" avec cartes statistiques, top des ventes et exports
- Sauvegarde automatique vers la base de données

## Backlog

### P1 - Prioritaire
- [ ] Espace noir en bas de l'écran sur certaines pages

### P2 - Améliorations
- [ ] PDF génération nécessite plusieurs clics sur mobile
- [ ] Refactoring du fichier index.tsx (21k+ lignes)

### P3 - Bloqué
- [ ] Déploiement en production (limitation plateforme Emergent)

## Notes Techniques
- Le workflow de build nécessite: modifier source → `npx expo export --platform web` → copier dist → appliquer patches CSS
- Le cache CDN d'Emergent peut retarder la visibilité des changements frontend
