# NeoChef - Product Requirements Document

## Original Problem Statement
Application PWA pour la gestion de restaurants avec :
- Gestion des menus (nourriture/boissons)
- Système de réservations
- Génération de factures et devis en PDF
- Gestion multi-restaurants (Holding)
- Menu public accessible via QR code
- Système de permissions pour les utilisateurs
- Fonctionnalités "Ardoise" (plats du jour)

## Stack Technique
- **Frontend**: React Native/Expo (build web statique)
- **Backend**: FastAPI (Python)
- **Base de données**: MongoDB
- **Déploiement**: Emergent Platform

## Fonctionnalités Ardoise (IMPLÉMENTÉES)

### Backend ✅ FONCTIONNEL
Tous les endpoints API sont implémentés et testés :

1. **GET /api/ardoise/public/{token}** - Récupérer l'ardoise
2. **PUT /api/ardoise/public/{token}** - Modifier l'ardoise (plats + prix formules)
3. **POST /api/ardoise/public/{token}/sales** - Enregistrer les ventes du service
4. **GET /api/ardoise/sales/report/public/{token}?period=week** - Rapport de ventes
5. **GET /api/ardoise/sales/export-pdf/{token}?period=week** - Export PDF
6. **GET /api/ardoise/sales/export-excel/{token}?period=week** - Export Excel

### Frontend (Code prêt, bloqué par cache CDN)
Le code frontend implémente :
- Mode Édition : modifier les plats et descriptions
- Mode Ventes : saisir les quantités vendues par plat
- Mode Rapports : visualiser les statistiques et exporter PDF/Excel
- Édition des prix des formules

## Traductions
7 langues générées : EN, ES, DE, IT, ZH, RU, PT
31 traductions par langue pour les sections et plats de l'ardoise

## Restaurants de Test
- **O'Parloir** (rest_17e485265f52) - Restaurant principal
- **Le Cercle** (rest_efb3705687ef)
- **Token Ardoise O'Parloir** : `3A72iGUORT3Ymx6zsrPcBQ`

## URLs
- **Preview** : https://restaurant-preview-6.preview.emergentagent.com
- **Production** : https://neochef-pwa-2.emergent.host
- **Ardoise O'Parloir** : https://restaurant-preview-6.preview.emergentagent.com/ardoise/3A72iGUORT3Ymx6zsrPcBQ

## Problèmes Connus

### ⚠️ Cache CDN (BLOQUANT)
Le cache Cloudflare au niveau de la plateforme Emergent empêche les mises à jour frontend de s'afficher. Solutions :
1. Redéployer via le bouton "Deploy"
2. Contacter support@emergent.sh pour purger le cache
3. Attendre l'expiration naturelle du cache

### Issues en attente
1. **Espace noir en bas de l'écran** - Non reproduit dans les tests
2. **Visibilité ardoise sur menu client** - Section activée, restriction d'heure supprimée

## Fichiers Clés
- `/app/backend/server.py` - Backend FastAPI (15k+ lignes)
- `/app/temp_clone/frontend/app/ardoise/[token].tsx` - Page gestion ardoise
- `/app/temp_clone/frontend/app/client/[restaurant_id].tsx` - Menu client public

## Changelog

### 2026-03-09
- Activé la section A L'ARDOISE pour O'Parloir
- Ajouté données de test pour l'ardoise (2 entrées, 2 plats, 2 desserts)
- Généré traductions pour 7 langues
- Supprimé restriction d'heure (ardoise visible toute la journée)
- Corrigé bug qui cachait section sans items réguliers
- Testé toutes les APIs backend (PUT prix, POST ventes, GET rapports, exports)
- Tenté plusieurs méthodes pour bypass cache CDN (sans succès)

## Backlog / Future Tasks
1. Corriger l'espace noir en bas de l'écran
2. Déployer en production avec corrections
3. Décomposer le fichier monolithique index.tsx
4. Automatiser le processus de build
