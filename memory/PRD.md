# NeoChef - Product Requirements Document

## Résumé du Produit
NeoChef est une PWA de gestion de restaurant complète comprenant:
- Gestion des menus (carte, ardoise)
- Gestion des événements avec prestataires
- Système de permissions pour le staff
- Traductions automatiques des menus
- Génération de PDF (menus, propositions événements)

## Architecture Technique
- **Frontend**: Expo for Web (React Native Web) - `/app/temp_clone/frontend`
- **Backend**: FastAPI - `/app/backend/server.py`
- **Database**: MongoDB
- **Build servi depuis**: `/app/frontend/build` (copie de `temp_clone/frontend/dist`)

## État Actuel - Session du 19 Mars 2026

### Bugs Corrigés (P0)

1. **Menu Client Bloqué** ✅
   - **Cause**: Configuration manquante de l'URL backend dans Expo
   - **Solution**: Ajout de `EXPO_PUBLIC_BACKEND_URL` dans `.env` et `app.json`
   - **Fichiers modifiés**: `/app/temp_clone/frontend/.env`, `/app/temp_clone/frontend/app.json`

2. **Détails Prestataire Non Affichés** ✅
   - **Cause**: Build du frontend non synchronisé entre `temp_clone` et `frontend/build`
   - **Solution**: Modification du code pour afficher TOUJOURS les horaires et tarifs (même vides)
   - **Fichiers modifiés**: `/app/temp_clone/frontend/app/index.tsx` (lignes ~22912-22930)

3. **Logo PDF Déformé** ✅
   - **Cause**: Logo forcé en carré (w=h) sans respecter les proportions
   - **Solution**: Utilisation de PIL pour calculer le ratio et préserver les proportions
   - **Fichiers modifiés**: `/app/backend/server.py` (fonction `export_event_menu_pdf`)

### Corrections Techniques Importantes
- Le build Expo doit être copié de `/app/temp_clone/frontend/dist` vers `/app/frontend/build`
- Commande de déploiement:
  ```bash
  cd /app/temp_clone/frontend && npx expo export --platform web
  rm -rf /app/frontend/build/* && cp -r /app/temp_clone/frontend/dist/* /app/frontend/build/
  sudo supervisorctl restart frontend
  ```

## Problèmes Restants (Backlog)

### P1 - Priorité Haute
- **Sauvegarde Permissions UI**: Le formulaire frontend de gestion des permissions staff ne sauvegarde pas correctement
- **Aperçu PDF blanc iOS**: L'aperçu PDF dans la PWA iOS ne fonctionne pas
- **Service Worker/Cache**: Mettre en place une stratégie de mise à jour du SW

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

### API Événements
- `GET /api/events` - Liste des événements
- `GET /api/events/{id}/providers` - Prestataires d'un événement
- `POST /api/events/{id}/providers` - Ajouter prestataire
- `PUT /api/events/{id}/providers/{provider_id}` - Modifier prestataire
- `GET /api/events/{id}/menu/export-pdf` - Générer PDF menu événement

### API Menu
- `GET /api/menu-restaurant/sections` - Sections du menu
- `PUT /api/menu-restaurant-draft/items/{id}` - Modifier item menu draft

## Credentials de Test
- **Admin**: `groupenaga@gmail.com` / `LeCercle123!`
- **Staff**: `tharshikan@orange.fr` / `Kajan1012`

## Intégrations Tierces
- **MongoDB**: Base de données
- **Emergent LLM**: Traductions automatiques (clé dans `.env`)
- **XLSX**: Import/export Excel

## Notes de Développement
- Toujours rebuilder le frontend Expo après modifications
- Toujours copier le build vers `/app/frontend/build`
- Les `_id` MongoDB doivent être exclus des réponses JSON
