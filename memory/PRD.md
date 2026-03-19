# NeoChef - Product Requirements Document

## Résumé du Produit
NeoChef est une PWA de gestion de restaurant complète comprenant:
- Gestion des menus (carte, ardoise)
- Gestion des événements avec prestataires
- Système de permissions pour le staff
- Traductions automatiques des menus (multi-langues)
- Génération de PDF (menus, propositions événements)

## Architecture Technique
- **Frontend**: Expo for Web (React Native Web) - `/app/temp_clone/frontend`
- **Backend**: FastAPI - `/app/backend/server.py`
- **Database**: MongoDB
- **Build servi depuis**: `/app/frontend/build` (copie de `temp_clone/frontend/dist`)

## Session du 19 Mars 2026

### Bugs Corrigés

#### 1. Menu Client Bloqué ✅
- **Cause**: URL du backend manquante dans la config Expo
- **Solution**: Ajout de `EXPO_PUBLIC_BACKEND_URL` dans `.env` et `app.json`
- **Fichiers**: `/app/temp_clone/frontend/.env`, `/app/temp_clone/frontend/app.json`

#### 2. Détails Prestataire Non Affichés ✅
- **Cause**: Build non synchronisé entre `temp_clone` et `frontend/build`
- **Solution**: Affichage systématique des horaires/tarifs
- **Fichiers**: `/app/temp_clone/frontend/app/index.tsx`

#### 3. Logo PDF Déformé ✅
- **Cause**: Logo forcé en carré sans respect des proportions
- **Solution**: Utilisation de PIL pour calculer le ratio
- **Fichiers**: `/app/backend/server.py`

#### 4. Prix des Plats dans PDF Événement ✅
- **Cause**: Prix non affichés dans la génération PDF
- **Solution**: Ajout de l'affichage du prix à côté du nom du plat
- **Fichiers**: `/app/backend/server.py` (fonction `export_event_menu_pdf`)

#### 5. Traduction des Tailles (Petit/Grand) ✅
- **Cause**: Les noms de formats n'étaient pas traduits
- **Solution**: Ajout de traduction pour "Petit", "Grand" → "小份", "大份" (chinois), etc.
- **Fichiers**: `/app/temp_clone/frontend/app/client/[restaurant_id].tsx`

### Point Technique Important
Le frontend Expo est dans `/app/temp_clone/frontend` mais le serveur sert `/app/frontend/build`. Après chaque modification frontend:
```bash
cd /app/temp_clone/frontend && npx expo export --platform web
cp -r dist/* /app/frontend/build/
sudo supervisorctl restart frontend
```

## Problèmes Restants (Backlog)

### P1 - Priorité Haute
- **Sauvegarde Permissions UI**: Le formulaire de gestion des permissions staff ne sauvegarde pas correctement
- **Aperçu PDF blanc iOS**: L'aperçu PDF dans la PWA iOS ne fonctionne pas
- **Service Worker/Cache**: Stratégie de mise à jour du SW à définir

### P2 - Priorité Moyenne
- **Barre Navigation iOS**: Problème de mise en page persistant
- **Photos Espaces Privatisation**: Ne s'affichent pas côté client
- **Édition Ardoise**: Ne charge pas les plats du menu

### P3 - Refactoring
- Décomposer `server.py` (~17k lignes) en modules
- Décomposer `index.tsx` (~25k lignes) en composants

## Endpoints Clés

### API Publique (Menu Client)
- `GET /api/menu-restaurant/public/{restaurant_id}` - Menu public
- `GET /api/public/translations/{restaurant_id}` - Traductions cachées

### API Événements
- `GET /api/events` - Liste des événements
- `GET /api/events/{id}/providers` - Prestataires d'un événement
- `GET /api/events/{id}/menu/export-pdf` - Générer PDF menu événement

## Credentials de Test
- **Admin**: `groupenaga@gmail.com` / `LeCercle123!`
- **Staff**: `tharshikan@orange.fr` / `Kajan1012`

## Intégrations
- **MongoDB**: Base de données
- **Emergent LLM**: Traductions automatiques
- **XLSX**: Import/export Excel
