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

### Menu Restaurant & Menu en Cours (Draft)
- Menu principal (lecture seule pour staff)
- Menu en cours (brouillon modifiable)
- Import/Export CSV et Excel
- Import PDF avec extraction automatique
- **Endpoints PUT ajoutés pour menu draft** : `/api/menu-restaurant-draft/items/{item_id}` et `/api/menu-restaurant-draft/sections/{section_id}`

### Module Événements
- Création et gestion d'événements avec prestataires, tâches et menu
- **PDF événement** : Logo du restaurant prioritaire, mise en page améliorée (nom sur une ligne, description en dessous)
- **Prévisualisation PDF** : Modal avec boutons Retour et Télécharger
- **Couleur de section** : Champ `color` ajouté au modèle `UpdateEventMenuSectionRequest`
- **Prix des plats** : Affichage par section/succession (pas de total additionnant toutes les successions)

### Ardoise
- Stockage séparé par restaurant (`mep_ardoise` collection)
- Indépendante des imports CSV (jamais supprimée)
- **Bouton Retour amélioré** sur l'écran Rapport Ardoise

### UI/UX
- Barre de navigation inférieure fixée avec `position: fixed` pour iOS
- **Formulaire prestataire** : Horaires (Heure début/fin) avec style compact pour éviter le débordement

## Recent Changes (19/03/2026)

### Bug Fix: Modifications menu non sauvegardées
- **Cause racine** : Frontend appelait `/menu-restaurant/items/` au lieu de `${apiPrefix}/items/` pour le menu draft
- **Correction Backend** : Ajout des endpoints PUT pour `/api/menu-restaurant-draft/items/{item_id}` et `/api/menu-restaurant-draft/sections/{section_id}`
- **Correction Frontend** : Utilisation de `${apiPrefix}/items/` dans la fonction de mise à jour

### Module Événements amélioré
- **Couleur de section** : Ajout du champ `color` au modèle backend pour sauvegarder la couleur
- **PDF événement** : Logo du restaurant en priorité (avant le logo par défaut), mise en page des plats sur plusieurs lignes
- **Prévisualisation PDF** : Ajout d'un modal avec boutons Retour et Télécharger
- **Prix des successions** : Affichage par section avec note explicative (pas d'addition de toutes les successions)

### Corrections Permissions Staff
- **Task Templates**: Endpoints utilisent `detailed_permissions.taches.modeles_*`
- **Menu Restaurant**: Endpoints vérifient `detailed_permissions.menu_restaurant.*`
- **Liste Templates**: Staff avec `taches.categories: []` a accès à toutes les catégories

### Performance
- Traductions automatiques **désactivées** temporairement (bloquaient le serveur)

## Tech Stack
- Frontend: React/Expo for Web
- Backend: FastAPI
- Database: MongoDB
- Auth: JWT
- PWA: Service Workers

## Key Collections
- `mep_users` - Utilisateurs avec `detailed_permissions`
- `mep_restaurants` - Configuration restaurant avec `logo_base64`
- `mep_menu_restaurant_sections` - Sections menu principal
- `mep_menu_restaurant_items` - Items menu principal
- `mep_menu_restaurant_draft_sections` - Sections brouillon
- `mep_menu_restaurant_draft_items` - Items brouillon
- `mep_event_menu_sections` - Sections menu événement
- `mep_event_menu_items` - Items menu événement
- `mep_ardoise` - Ardoise (indépendante par restaurant)
- `mep_privatisation_spaces` - Espaces de privatisation avec photos

## API Credentials
- Admin: groupenaga@gmail.com / LeCercle123!
- Staff: tharshikan@orange.fr / Kajan1012

## Backlog (P2/P3)
- Photos des espaces de privatisation non affichées pour les clients (à investiguer)
- Aperçu PDF blanc sur iOS
- Refactoring des fichiers monolithes (server.py ~17k lignes, index.tsx ~25k lignes)
- Réactivation réinitialisation mot de passe par email
- Réactiver les traductions automatiques avec un worker séparé
