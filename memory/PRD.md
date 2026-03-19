# NeoChef - Product Requirements Document

## Application Overview
PWA de gestion de restaurant (React/Expo + FastAPI + MongoDB) permettant la gestion des menus, fiches techniques, tâches, réservations et équipes.

## Core Features Implemented

### Système de Permissions
- Permissions granulaires par module (lecture, édition, ajout, suppression)
- Gestion admin/staff avec `detailed_permissions`
- Endpoints: PUT /api/users/{user_id}
- **Modèles de tâches** : Staff avec permissions `modeles_ajouter/modifier/supprimer` peut gérer les templates
- **Menu Restaurant** : Staff avec permissions `produits.ajouter/modifier/supprimer` peut éditer le menu

### Menu Restaurant
- Menu principal (lecture seule pour staff)
- Menu en cours (brouillon modifiable)
- Import/Export CSV et Excel
- Import PDF avec extraction automatique
- Support du format Excel exporté par l'application
- Endpoint: /api/menu-restaurant-draft/import-csv, /api/menu-restaurant-draft/import-pdf

### Ardoise
- Stockage séparé par restaurant (`mep_ardoise` collection)
- Indépendante des imports CSV (jamais supprimée)
- Endpoint: GET/PUT /api/ardoise
- **Bouton Retour ajouté** sur l'écran Rapport Ardoise

### UI/UX PWA iOS
- Barre de navigation inférieure fixée avec `position: fixed`
- Support de `env(safe-area-inset-bottom)` pour iOS
- Header étendu avec padding pour la barre d'état iOS
- Espacement réduit entre les icônes de navigation

## Recent Changes (19/03/2026)

### Corrections Permissions Staff
- **Task Templates**: Endpoints `create/update/delete` utilisent maintenant `detailed_permissions.taches.modeles_*` au lieu de `role === 'admin'`
- **Subtasks**: Même correction pour les sous-tâches
- **Menu Restaurant**: Endpoints `create/update/delete` pour sections et items vérifient `detailed_permissions.menu_restaurant.*`
- **Liste Templates**: Staff avec `taches.categories: []` (vide) a accès à toutes les catégories

### Performance - Traductions Automatiques
- Traductions automatiques **désactivées** temporairement car elles bloquaient le serveur (timeout)
- Les mises à jour du menu sont maintenant instantanées
- Les traductions peuvent être déclenchées manuellement via l'endpoint existant

### UI
- Bouton "← Retour" amélioré sur l'écran Rapport Ardoise (plus visible avec fond blanc et bordure)

### Import CSV/Excel Amélioré
- Support direct des fichiers .xlsx et .xls (bibliothèque `xlsx`)
- Détection automatique du format d'export de l'application
- Conversion automatique vers le format CSV standard
- Préservation des paramètres (has_happy_hour) lors des imports
- Nouvelles sections héritent `has_happy_hour` des existantes
- Suppression des sections/items non présents dans le CSV

## Tech Stack
- Frontend: React/Expo for Web
- Backend: FastAPI
- Database: MongoDB
- Auth: JWT
- PWA: Service Workers

## Key Collections
- `mep_users` - Utilisateurs avec `detailed_permissions`
- `mep_restaurants` - Configuration restaurant
- `mep_menu_restaurant_sections` - Sections menu principal
- `mep_menu_restaurant_items` - Items menu principal
- `mep_menu_restaurant_draft_sections` - Sections brouillon
- `mep_menu_restaurant_draft_items` - Items brouillon
- `mep_ardoise` - Ardoise (indépendante par restaurant)

## API Credentials
- Admin: groupenaga@gmail.com / LeCercle123!
- Staff: tharshikan@orange.fr / Kajan1012

## Backlog (P2/P3)
- Aperçu PDF blanc sur iOS
- Refactoring des fichiers monolithes (server.py, index.tsx)
- Réactivation réinitialisation mot de passe par email
- Réactiver les traductions automatiques avec un worker séparé
