# NeoChef PWA - Product Requirements Document

## Original Problem Statement
Migration d'une application PWA existante nommée "NeoChef" pour la gestion de restaurants. L'application inclut un système complet de gestion avec :
- Back-office Super Admin pour gérer tous les restaurants de la plateforme
- Système de permissions granulaires pour contrôler l'accès aux modules
- Système de menu "brouillon" avant publication
- Module de gestion des prestataires
- Notification de mise à jour pour la PWA

## Stack Technologique
- Frontend: React Native/Expo for Web (build statique)
- Backend: FastAPI (Python)
- Base de données: MongoDB
- Email: SendGrid

## Core Features

### 1. Système de Permissions Granulaires
- Contrôle d'accès en lecture/écriture aux différents modules
- Menu Restaurant (final) = lecture seule pour staff
- Menu Restaurant en cours = édition complète pour staff
- Fiche Technique = permissions granulaires (sections, produits, photos)
- Permission spécifique pour le bouton "Publier" du menu brouillon

### 2. Système de Menu Brouillon
- Environnement de test "Menu en cours" pour modifications sans affecter le menu public
- Bouton "Publier" pour appliquer les changements au menu public
- Staff peut éditer le menu en cours mais pas le menu final

### 3. Fiche Technique
- Gestion des sections (Bar, Cuisine)
- Gestion des produits avec ingrédients
- Analyse des marges
- Export PDF/Excel
- Permissions granulaires pour ajouter/modifier/supprimer sections et produits

### 4. Menu Groupe
- Gestion des réservations de groupe
- Sections et items personnalisables
- Génération de factures

### 5. PWA
- Notification de mise à jour pour informer les utilisateurs
- Service Worker pour le cache et fonctionnement hors-ligne
- Support iOS avec gestion des safe areas

## What's Been Implemented

### Session 16 mars 2026 - Corrections majeures des permissions

#### Corrections Frontend (Fiche Technique)
- [x] **Bug Fix CRITICAL** : Page "Fiche Technique" affichait une page blanche
  - Cause : Fonction `canEditFicheTechnique()` non définie dans le composant
  - Solution : Ajout de la fonction dans FicheTechniqueScreen

- [x] **Bug Fix CRITICAL** : Boutons d'édition non visibles pour staff avec permissions
  - Cause : Utilisation de `isManager` au lieu des permissions détaillées
  - Solution : Remplacement par `canAddSection`, `canEditSection`, `canDeleteSection`, `canAddProduct`, `canEditProduct`, `canDeleteProduct`

- [x] **Amélioration** : Permissions utilisées pour conditionner les boutons :
  - Vue détail produit : bouton ✏️, colonnes de prix
  - Vue liste sections : boutons +, ✏️, 🗑️
  - Vue liste produits : boutons ✏️, 🗑️
  - Bouton "+ Ajouter une section"

#### Corrections Frontend (Menu Restaurant)
- [x] **Bug Fix** : Menu Restaurant final toujours en lecture seule pour staff
  - Même si permissions accordées, le menu final n'est modifiable que par admin
  
- [x] **Bug Fix** : Menu Restaurant en cours avec édition complète pour staff
  - Staff avec accès = tous les boutons d'édition (+, ✏️, 🗑️) sur sections et produits

#### Corrections Frontend (Divers)
- [x] **Bug Fix** : Bouton "Modifier mot de passe" non visible pour staff
  - Cause : Couleur du texte non définie
  - Solution : Ajout de `color: secondaryColor` et `data-testid`

- [x] **Bug Fix** : Réservations Menu Groupe non affichées
  - Cause : Données non rechargées à l'entrée dans l'écran
  - Solution : Ajout d'un `useEffect` pour charger les réservations au montage

- [x] **Bug Fix** : Normalisation de `section_access` pour Fiche Technique
  - Support de 'tous', 'all' et 'both'

#### Corrections Backend
- [x] API `/api/group-reservations/list` fonctionne pour admin
- [x] API `/api/users/{user_id}/detailed-permissions` sauvegarde correctement les permissions

### Session 15 mars 2026
- [x] Bug Fix : Page "Équipe" affichait un écran vide
- [x] Nouvelle fonctionnalité : Bouton "Donner tous les accès"
- [x] Bug Fix : Permissions vides pour les utilisateurs staff
- [x] Bug Fix : Accès aux événements pour le staff
- [x] Bug Fix : Changement de restaurant
- [x] Bug Fix : API de traduction

## Prioritized Backlog

### P0 (Critique) - Corrigés ✅
- [x] Fiche Technique page blanche
- [x] Boutons d'édition non visibles pour staff avec permissions
- [x] Menu Restaurant lecture seule pour staff
- [x] Menu Restaurant en cours éditable pour staff
- [x] Bouton "Modifier mot de passe" pour staff
- [x] Réservations Menu Groupe non affichées

### P1 (Important) - À surveiller
- [ ] Vérifier que les permissions sont correctement sauvegardées via l'interface
- [ ] Traduction en production (vérifier EMERGENT_LLM_KEY)

### P2 (Améliorations)
- [ ] Espaces vides PWA iOS
- [ ] Aperçu PDF blanc sur iOS
- [ ] Refactoring server.py et index.tsx (monolithes)
- [ ] Bouton "Retour" menu client sur iOS

## Architecture

### Backend
- `/app/backend/server.py` - API FastAPI (monolithe ~16k lignes)
- `/app/backend/.env` - Configuration (MONGO_URL, EMERGENT_LLM_KEY)

### Frontend
- `/app/temp_clone/frontend/app/index.tsx` - Application React/Expo (monolithe ~24k lignes)
- `/app/frontend/build/` - Build statique servi par Nginx
- `/app/frontend/.env` - Configuration (REACT_APP_BACKEND_URL)

### Key Endpoints
- `POST /api/auth/login` - Connexion
- `POST /api/auth/change-password` - Changement mot de passe
- `PUT /api/users/{user_id}` - Mise à jour utilisateur
- `PUT /api/users/{user_id}/detailed-permissions` - Mise à jour permissions
- `GET /api/group-reservations/list` - Liste des réservations groupe
- `GET /api/fiche-sections/list` - Liste des sections Fiche Technique
- `GET /api/fiche-products/list` - Liste des produits Fiche Technique

## Credentials (Preview)
- Admin: `groupenaga@gmail.com` / `LeCercle123!`
- Staff: `tharshikan@orange.fr` / `Kajan1012`

## Notes pour le déploiement
1. Après déploiement, re-sauvegarder les permissions des utilisateurs staff via l'interface
2. Vérifier la variable EMERGENT_LLM_KEY en production pour la traduction
3. Demander aux utilisateurs de vider leur cache PWA après mise à jour
