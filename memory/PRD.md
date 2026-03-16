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

### 1. Back-Office Super Admin
- Tableau de bord avec vue sur tous les restaurants et utilisateurs
- Création de nouveaux comptes restaurants
- Réinitialisation manuelle des mots de passe utilisateurs
- Accès via login spécial `superadmin`

### 2. Système de Permissions Granulaires
- Contrôle d'accès en lecture/écriture aux différents modules
- Permission spécifique pour le bouton "Publier" du menu brouillon (à implémenter)
- 3 sections pour le module Ardoise: Édition, Ventes, Rapports

### 3. Système de Menu Brouillon
- Environnement de test "Menu en cours" pour modifications sans affecter le menu public
- Bouton "Publier" pour appliquer les changements au menu public
- Initialisation automatique du menu brouillon

### 4. Gestion des Prestataires
- CRUD complet pour la gestion des prestataires
- Intégration avec le module Événements (à compléter)

### 5. PWA
- Notification de mise à jour pour informer les utilisateurs
- Service Worker pour le cache et fonctionnement hors-ligne
- Support iOS avec gestion des safe areas (encoche/home indicator)

## What's Been Implemented (Mars 2026)

### Session actuelle (15 mars 2026) - Correction finale
- [x] **Bug Fix CRITICAL** : Page "Équipe" affichait un écran vide
  - Cause : Références à `users.map()` et `u.assigned_categories.length` sans vérification null
  - Solution : Ajout de `(users || [])` et `(u.assigned_categories || [])` pour éviter les crashs
- [x] **Nouvelle fonctionnalité** : Bouton "Donner tous les accès"
  - Backend : `POST /api/users/{user_id}/grant-full-access` - Active tous les modules pour un staff
  - Frontend : Nouveau bouton vert dans le menu d'actions de chaque staff
- [x] **Bug Fix P0** : Correction des permissions vides pour les utilisateurs staff
  - Cause identifiée : L'utilisateur `tharshikan@orange.fr` avait `detailed_permissions: {}` (vide)
  - Solution : Ajout des permissions complètes dans MongoDB pour tous les modules
- [x] **Bug Fix P0** : Accès aux événements pour le staff - API `/api/events` fonctionne maintenant
- [x] **Bug Fix P0** : Changement de restaurant - API `/api/restaurants/switch` fonctionne correctement
- [x] **Bug Fix P0** : API de traduction - `/api/translate` fonctionne correctement
- [x] Validation backend : 100% (9/9 tests passés)
- [x] Validation frontend : 90% (Login, dashboard, sidebar fonctionnent)

### Session précédente (15 mars 2026)
- [x] **Bug Fix P0** : Correction de la sauvegarde des permissions - Fusion profonde des objets imbriqués dans `openPermissionsModal`
- [x] **Bug Fix P0** : Initialisation de `restaurants_access` à partir de `user.restaurant_ids` existants
- [x] **Bug Fix P0** : Fallback dans `savePermissions` pour préserver les `restaurant_ids` si `allRestaurants` n'est pas chargé
- [x] Validation par testing agent : 100% des tests backend et frontend passés
- [x] Suppression du code Super Admin et SendGrid pour simplifier l'application

### Sessions précédentes
- [x] Correction CSS pour les espaces vides sur PWA iOS (safe areas)
- [x] Back-office Super Admin (supprimé depuis)
- [x] Module Prestataires (CRUD)
- [x] Notification de mise à jour PWA
- [x] Correction bug réinitialisation mot de passe SendGrid (supprimé depuis)
- [x] Correction suppression éléments menu brouillon
- [x] Correction UI écran "Équipe" avec menu déroulant
- [x] Système de permissions Ardoise
- [x] Déploiement en production avec script initialisation

## Prioritized Backlog

### P0 (Critique) - Corrigés ✅
- [x] Sauvegarde des permissions (corrigé le 15 mars 2026)
- [x] Initialisation des restaurant_ids dans le modal permissions
- [x] Accès staff aux modules (corrigé le 15 mars 2026) - Ajout des detailed_permissions manquantes
- [x] API /api/events accessible aux staff
- [x] API /api/restaurants/switch fonctionne
- [x] API /api/translate fonctionne

### P0 (Critique) - À valider par l'utilisateur
- [ ] **IMPORTANT** : L'utilisateur doit tester en production après avoir vidé le cache de son navigateur/PWA
  - Sur ordinateur : Hard refresh (Ctrl+Shift+R ou Cmd+Shift+R)
  - Sur iPhone : Supprimer l'icône PWA et la réajouter depuis Safari

### P1 (Important)
- [ ] Espaces vides PWA iOS (nécessite test utilisateur sur vrai iPhone)
- [ ] Aperçu PDF blanc sur iOS - explorer solution react-pdf
- [ ] Refactoring server.py et index.tsx (monolithes > 10k lignes)
- [ ] Fiabilité des mises à jour PWA (service worker)

### P2 (Normal)
- [ ] Permission pour bouton "Publier" du menu brouillon
- [ ] Intégration sélection prestataires dans écran Événements
- [ ] Export planning ardoises
- [ ] Réactiver la réinitialisation de mot de passe par email

### P3 (Nice to have)
- [ ] Automatiser process de build/déploiement

## Key Files
- `/app/backend/server.py` - Backend FastAPI monolithique (~13k lignes)
- `/app/temp_clone/frontend/app/index.tsx` - Frontend React monolithique (~24k lignes)
- `/app/frontend/build/index.html` - HTML généré avec CSS safe area corrigé
- `/app/frontend/build/sw.js` - Service Worker pour PWA

## Database Schema
- `users`: { _id, email, password, role: 'admin'|'staff'|'superadmin', restaurants }
- `mep_restaurants`: { _id, name, share_token, primary_color, secondary_color }
- `prestataires`: { _id, restaurant_id, name, contact, email, phone, speciality }
- `ardoise_items`, `ardoise_sales_history`, `planned_ardoises`

## Test Credentials
- Super Admin: neochef.fr@gmail.com / Kajan1012
- Utilisateur standard: groupenaga@gmail.com / LeCercle123!

## URLs
- Preview: https://perms-debug.preview.emergentagent.com
- Production: À confirmer après déploiement

## Process de Build
1. Modifier dans `/app/temp_clone/frontend/`
2. Exécuter `yarn expo export --platform web`
3. Copier `/app/temp_clone/frontend/dist/*` vers `/app/frontend/build/`
4. Corriger CSS safe area dans index.html si nécessaire
5. Redémarrer frontend: `sudo supervisorctl restart frontend`
