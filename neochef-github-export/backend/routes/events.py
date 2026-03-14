"""
Routes API pour le module Événements
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional, List
import uuid
from datetime import datetime, timezone
import os
import base64

# Import models
from models.events import (
    CreateEventRequest, UpdateEventRequest, DuplicateEventRequest,
    CreateProviderRequest, UpdateProviderRequest, ValidateQuoteRequest, UpdateInvoiceStatusRequest,
    CreateEventTaskRequest, UpdateEventTaskRequest, UpdateTaskStatusRequest,
    CreateEventMenuSectionRequest, UpdateEventMenuSectionRequest,
    CreateEventMenuItemRequest, UpdateEventMenuItemRequest,
    CreatePricePackageRequest, UpdatePricePackageRequest,
    CreateDrinkOptionRequest, UpdateDrinkOptionRequest
)

# Router
events_router = APIRouter(prefix="/events", tags=["events"])

# Les collections et fonctions d'auth seront injectées depuis server.py
_db = None
_get_current_user = None

def init_events_router(db, get_current_user_func):
    """Initialiser le router avec les dépendances de server.py"""
    global _db, _get_current_user
    _db = db
    _get_current_user = get_current_user_func

# Collections helpers
def events_collection():
    return _db.mep_events

def providers_collection():
    return _db.mep_event_providers

def event_tasks_collection():
    return _db.mep_event_tasks

def event_menu_sections_collection():
    return _db.mep_event_menu_sections

def event_menu_items_collection():
    return _db.mep_event_menu_items

def price_packages_collection():
    return _db.mep_event_price_packages

def drink_options_collection():
    return _db.mep_event_drink_options

# Uploads directory
UPLOADS_DIR = "/app/backend/uploads/events"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ==================== HELPER FUNCTIONS ====================

def has_event_access(user: dict, permission_level: str = "admin") -> bool:
    """Vérifier si l'utilisateur a accès au module événements"""
    # Admin et manager ont accès complet
    if user.get("role") in ["admin", "manager"]:
        return True
    
    # Vérifier les permissions spécifiques aux événements
    event_permission = user.get("permissions", {}).get("events", "none")
    
    if permission_level == "admin":
        return event_permission == "admin"
    elif permission_level == "read_only":
        return event_permission in ["admin", "read_only", "task_status_only"]
    elif permission_level == "task_status_only":
        return event_permission in ["admin", "task_status_only"]
    
    return False

# ==================== EVENT ENDPOINTS ====================

@events_router.post("")
async def create_event(request: CreateEventRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer un nouvel événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    event_id = f"event_{uuid.uuid4().hex[:12]}"
    event = {
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "title": request.title,
        "date": request.date,
        "description": request.description,
        "notes": request.notes,
        "is_active": True,
        "created_by": current_user["user_id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await events_collection().insert_one(event)
    
    # Remove MongoDB _id before returning
    event.pop("_id", None)
    return event

@events_router.get("")
async def list_events(current_user: dict = Depends(lambda: _get_current_user)):
    """Lister tous les événements du restaurant, triés par date"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    events = await events_collection().find(
        {"restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).sort("date", 1).to_list(length=1000)
    
    return events

@events_router.get("/{event_id}")
async def get_event(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Obtenir les détails d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    event = await events_collection().find_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"_id": 0}
    )
    
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return event

@events_router.put("/{event_id}")
async def update_event(event_id: str, request: UpdateEventRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await events_collection().update_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return await get_event(event_id, current_user)

@events_router.delete("/{event_id}")
async def delete_event(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer un événement (soft delete)"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await events_collection().update_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    return {"message": "Événement supprimé"}

@events_router.post("/{event_id}/duplicate")
async def duplicate_event(event_id: str, request: DuplicateEventRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Dupliquer un événement avec tous ses prestataires, tâches et menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Récupérer l'événement original
    original_event = await events_collection().find_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"_id": 0}
    )
    
    if not original_event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Créer le nouvel événement
    new_event_id = f"event_{uuid.uuid4().hex[:12]}"
    new_event = {
        **original_event,
        "event_id": new_event_id,
        "title": request.new_title or f"{original_event['title']} (copie)",
        "date": request.new_date or original_event["date"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": current_user["user_id"]
    }
    
    await events_collection().insert_one(new_event)
    
    # Dupliquer les prestataires
    providers = await providers_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    provider_id_map = {}
    for provider in providers:
        old_id = provider["provider_id"]
        new_id = f"provider_{uuid.uuid4().hex[:12]}"
        provider_id_map[old_id] = new_id
        
        new_provider = {
            **provider,
            "provider_id": new_id,
            "event_id": new_event_id,
            # Reset file paths and statuses for new event
            "quote_path": None,
            "quote_status": "pending",
            "invoice_path": None,
            "invoice_status": "pending",
            "payment_proof_path": None,
            "payment_method": None,
            "created_at": datetime.now(timezone.utc)
        }
        await providers_collection().insert_one(new_provider)
    
    # Dupliquer les tâches
    tasks = await event_tasks_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    for task in tasks:
        new_task_id = f"task_{uuid.uuid4().hex[:12]}"
        new_task = {
            **task,
            "task_id": new_task_id,
            "event_id": new_event_id,
            "status": "todo",  # Reset status
            "created_at": datetime.now(timezone.utc)
        }
        await event_tasks_collection().insert_one(new_task)
    
    # Dupliquer les sections de menu
    sections = await event_menu_sections_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    section_id_map = {}
    for section in sections:
        old_id = section["section_id"]
        new_id = f"section_{uuid.uuid4().hex[:12]}"
        section_id_map[old_id] = new_id
        
        new_section = {
            **section,
            "section_id": new_id,
            "event_id": new_event_id,
            "created_at": datetime.now(timezone.utc)
        }
        await event_menu_sections_collection().insert_one(new_section)
    
    # Dupliquer les items de menu
    items = await event_menu_items_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    for item in items:
        new_item_id = f"item_{uuid.uuid4().hex[:12]}"
        new_item = {
            **item,
            "item_id": new_item_id,
            "event_id": new_event_id,
            "section_id": section_id_map.get(item["section_id"], item["section_id"]),
            "created_at": datetime.now(timezone.utc)
        }
        await event_menu_items_collection().insert_one(new_item)
    
    # Dupliquer les packages de prix
    packages = await price_packages_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    for package in packages:
        new_package_id = f"package_{uuid.uuid4().hex[:12]}"
        # Mapper les anciens IDs de sections vers les nouveaux
        new_section_ids = [section_id_map.get(sid, sid) for sid in package.get("section_ids", [])]
        new_package = {
            **package,
            "package_id": new_package_id,
            "event_id": new_event_id,
            "section_ids": new_section_ids,
            "created_at": datetime.now(timezone.utc)
        }
        await price_packages_collection().insert_one(new_package)
    
    # Dupliquer les options de boissons
    drinks = await drink_options_collection().find(
        {"event_id": event_id},
        {"_id": 0}
    ).to_list(length=1000)
    
    for drink in drinks:
        new_drink_id = f"drink_{uuid.uuid4().hex[:12]}"
        new_drink = {
            **drink,
            "drink_id": new_drink_id,
            "event_id": new_event_id,
            "is_selected": False,  # Reset selection
            "created_at": datetime.now(timezone.utc)
        }
        await drink_options_collection().insert_one(new_drink)
    
    new_event.pop("_id", None)
    return {
        "message": "Événement dupliqué avec succès",
        "event": new_event,
        "duplicated": {
            "providers": len(providers),
            "tasks": len(tasks),
            "menu_sections": len(sections),
            "menu_items": len(items),
            "price_packages": len(packages),
            "drink_options": len(drinks)
        }
    }

# ==================== PROVIDER (PRESTATAIRE) ENDPOINTS ====================

@events_router.post("/{event_id}/providers")
async def create_provider(event_id: str, request: CreateProviderRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Ajouter un prestataire à un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier que l'événement existe
    event = await events_collection().find_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]}
    )
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    provider_id = f"provider_{uuid.uuid4().hex[:12]}"
    provider = {
        "provider_id": provider_id,
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "name": request.name,
        "contact_name": request.contact_name,
        "phone": request.phone,
        "email": request.email,
        "notes": request.notes,
        # Devis
        "quote_path": None,
        "quote_status": "pending",  # "pending", "validated"
        # Facture
        "invoice_path": None,
        "invoice_status": "pending",  # "pending", "awaiting_payment", "paid"
        "payment_method": None,
        "payment_proof_path": None,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await providers_collection().insert_one(provider)
    provider.pop("_id", None)
    return provider

@events_router.get("/{event_id}/providers")
async def list_providers(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les prestataires d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    providers = await providers_collection().find(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).to_list(length=1000)
    
    return providers

@events_router.put("/{event_id}/providers/{provider_id}")
async def update_provider(event_id: str, provider_id: str, request: UpdateProviderRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier un prestataire"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prestataire non trouvé")
    
    provider = await providers_collection().find_one(
        {"provider_id": provider_id},
        {"_id": 0}
    )
    return provider

@events_router.delete("/{event_id}/providers/{provider_id}")
async def delete_provider(event_id: str, provider_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer un prestataire"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Prestataire non trouvé")
    
    return {"message": "Prestataire supprimé"}

# File upload endpoints for providers
@events_router.post("/{event_id}/providers/{provider_id}/quote")
async def upload_provider_quote(
    event_id: str, 
    provider_id: str, 
    file: UploadFile = File(...),
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Uploader un devis PDF pour un prestataire"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier le type de fichier
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    # Créer le dossier si nécessaire
    event_dir = os.path.join(UPLOADS_DIR, event_id, "providers", provider_id)
    os.makedirs(event_dir, exist_ok=True)
    
    # Sauvegarder le fichier
    file_path = os.path.join(event_dir, f"quote_{uuid.uuid4().hex[:8]}.pdf")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Mettre à jour le provider
    await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id},
        {"$set": {"quote_path": file_path, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Devis uploadé", "path": file_path}

@events_router.post("/{event_id}/providers/{provider_id}/validate-quote")
async def validate_provider_quote(
    event_id: str, 
    provider_id: str, 
    request: ValidateQuoteRequest,
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Valider un devis"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    provider = await providers_collection().find_one(
        {"provider_id": provider_id, "event_id": event_id}
    )
    
    if not provider:
        raise HTTPException(status_code=404, detail="Prestataire non trouvé")
    
    if not provider.get("quote_path"):
        raise HTTPException(status_code=400, detail="Aucun devis uploadé")
    
    status = "validated" if request.validated else "pending"
    await providers_collection().update_one(
        {"provider_id": provider_id},
        {"$set": {"quote_status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": f"Devis {'validé' if request.validated else 'remis en attente'}"}

@events_router.post("/{event_id}/providers/{provider_id}/invoice")
async def upload_provider_invoice(
    event_id: str, 
    provider_id: str, 
    file: UploadFile = File(...),
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Uploader une facture PDF pour un prestataire"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
    event_dir = os.path.join(UPLOADS_DIR, event_id, "providers", provider_id)
    os.makedirs(event_dir, exist_ok=True)
    
    file_path = os.path.join(event_dir, f"invoice_{uuid.uuid4().hex[:8]}.pdf")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id},
        {"$set": {"invoice_path": file_path, "invoice_status": "awaiting_payment", "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Facture uploadée", "path": file_path}

@events_router.post("/{event_id}/providers/{provider_id}/invoice-status")
async def update_invoice_status(
    event_id: str, 
    provider_id: str, 
    request: UpdateInvoiceStatusRequest,
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Mettre à jour le statut de la facture"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if request.status not in ["pending", "awaiting_payment", "paid"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    
    if request.status == "paid" and not request.payment_method:
        raise HTTPException(status_code=400, detail="Méthode de paiement requise pour statut 'payé'")
    
    update_data = {
        "invoice_status": request.status,
        "updated_at": datetime.now(timezone.utc)
    }
    if request.payment_method:
        update_data["payment_method"] = request.payment_method
    
    await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id},
        {"$set": update_data}
    )
    
    return {"message": "Statut de facture mis à jour"}

@events_router.post("/{event_id}/providers/{provider_id}/payment-proof")
async def upload_payment_proof(
    event_id: str, 
    provider_id: str, 
    file: UploadFile = File(...),
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Uploader une preuve de paiement (screenshot, etc.)"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Accepter images et PDFs
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Format de fichier non accepté (PDF, PNG, JPG)")
    
    event_dir = os.path.join(UPLOADS_DIR, event_id, "providers", provider_id)
    os.makedirs(event_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(event_dir, f"payment_proof_{uuid.uuid4().hex[:8]}{ext}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    await providers_collection().update_one(
        {"provider_id": provider_id, "event_id": event_id},
        {"$set": {"payment_proof_path": file_path, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Preuve de paiement uploadée", "path": file_path}

# ==================== TASK ENDPOINTS ====================

@events_router.post("/{event_id}/tasks")
async def create_event_task(event_id: str, request: CreateEventTaskRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer une tâche pour un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier que l'événement existe
    event = await events_collection().find_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]}
    )
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    
    # Récupérer le nom de l'utilisateur assigné si fourni
    assigned_user_name = None
    if request.assigned_user_id:
        assigned_user = await _db.mep_users.find_one(
            {"user_id": request.assigned_user_id},
            {"name": 1}
        )
        if assigned_user:
            assigned_user_name = assigned_user.get("name")
    
    task = {
        "task_id": task_id,
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "title": request.title,
        "description": request.description,
        "due_date": request.due_date,
        "assigned_user_id": request.assigned_user_id,
        "assigned_user_name": assigned_user_name,
        "status": "todo",  # "todo", "in_progress", "completed"
        "is_active": True,
        "created_by": current_user["user_id"],
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await event_tasks_collection().insert_one(task)
    task.pop("_id", None)
    return task

@events_router.get("/{event_id}/tasks")
async def list_event_tasks(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les tâches d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    tasks = await event_tasks_collection().find(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).sort("due_date", 1).to_list(length=1000)
    
    return tasks

@events_router.put("/{event_id}/tasks/{task_id}")
async def update_event_task(event_id: str, task_id: str, request: UpdateEventTaskRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier une tâche d'événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    # Si on change l'utilisateur assigné, récupérer son nom
    if "assigned_user_id" in update_data:
        if update_data["assigned_user_id"]:
            assigned_user = await _db.mep_users.find_one(
                {"user_id": update_data["assigned_user_id"]},
                {"name": 1}
            )
            update_data["assigned_user_name"] = assigned_user.get("name") if assigned_user else None
        else:
            update_data["assigned_user_name"] = None
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await event_tasks_collection().update_one(
        {"task_id": task_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    task = await event_tasks_collection().find_one(
        {"task_id": task_id},
        {"_id": 0}
    )
    return task

@events_router.put("/{event_id}/tasks/{task_id}/status")
async def update_task_status(event_id: str, task_id: str, request: UpdateTaskStatusRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Mettre à jour uniquement le statut d'une tâche (pour utilisateurs avec permissions limitées)"""
    current_user = await _get_current_user()
    
    # Vérifier au minimum la permission de mise à jour de statut
    if not has_event_access(current_user, "task_status_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if request.status not in ["todo", "in_progress", "completed"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    
    # Pour les utilisateurs avec permission limitée, vérifier qu'ils sont assignés à la tâche
    if not has_event_access(current_user, "admin"):
        task = await event_tasks_collection().find_one(
            {"task_id": task_id, "event_id": event_id}
        )
        if task and task.get("assigned_user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Vous pouvez uniquement modifier vos tâches assignées")
    
    result = await event_tasks_collection().update_one(
        {"task_id": task_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"status": request.status, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    return {"message": "Statut mis à jour"}

@events_router.delete("/{event_id}/tasks/{task_id}")
async def delete_event_task(event_id: str, task_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer une tâche"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await event_tasks_collection().update_one(
        {"task_id": task_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    
    return {"message": "Tâche supprimée"}

# ==================== EVENT MENU ENDPOINTS ====================

@events_router.post("/{event_id}/menu/sections")
async def create_menu_section(event_id: str, request: CreateEventMenuSectionRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer une section de menu pour l'événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier que l'événement existe
    event = await events_collection().find_one(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"]}
    )
    if not event:
        raise HTTPException(status_code=404, detail="Événement non trouvé")
    
    # Calculer l'ordre si non fourni
    if request.order is None:
        last_section = await event_menu_sections_collection().find_one(
            {"event_id": event_id},
            sort=[("order", -1)]
        )
        order = (last_section["order"] + 1) if last_section else 0
    else:
        order = request.order
    
    section_id = f"section_{uuid.uuid4().hex[:12]}"
    section = {
        "section_id": section_id,
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "name": request.name,
        "order": order,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await event_menu_sections_collection().insert_one(section)
    section.pop("_id", None)
    return section

@events_router.get("/{event_id}/menu/sections")
async def list_menu_sections(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les sections de menu d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    sections = await event_menu_sections_collection().find(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).sort("order", 1).to_list(length=1000)
    
    return sections

@events_router.put("/{event_id}/menu/sections/{section_id}")
async def update_menu_section(event_id: str, section_id: str, request: UpdateEventMenuSectionRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier une section de menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    result = await event_menu_sections_collection().update_one(
        {"section_id": section_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Section non trouvée")
    
    section = await event_menu_sections_collection().find_one(
        {"section_id": section_id},
        {"_id": 0}
    )
    return section

@events_router.delete("/{event_id}/menu/sections/{section_id}")
async def delete_menu_section(event_id: str, section_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer une section de menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await event_menu_sections_collection().update_one(
        {"section_id": section_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Section non trouvée")
    
    return {"message": "Section supprimée"}

# Menu Items
@events_router.post("/{event_id}/menu/items")
async def create_menu_item(event_id: str, request: CreateEventMenuItemRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer un item de menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Calculer l'ordre si non fourni
    if request.order is None:
        last_item = await event_menu_items_collection().find_one(
            {"section_id": request.section_id},
            sort=[("order", -1)]
        )
        order = (last_item["order"] + 1) if last_item else 0
    else:
        order = request.order
    
    item_id = f"item_{uuid.uuid4().hex[:12]}"
    item = {
        "item_id": item_id,
        "event_id": event_id,
        "section_id": request.section_id,
        "restaurant_id": current_user["restaurant_id"],
        "name": request.name,
        "description": request.description,
        "order": order,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await event_menu_items_collection().insert_one(item)
    item.pop("_id", None)
    return item

@events_router.get("/{event_id}/menu/items")
async def list_menu_items(event_id: str, section_id: Optional[str] = None, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les items de menu d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    query = {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True}
    if section_id:
        query["section_id"] = section_id
    
    items = await event_menu_items_collection().find(
        query,
        {"_id": 0}
    ).sort("order", 1).to_list(length=1000)
    
    return items

@events_router.put("/{event_id}/menu/items/{item_id}")
async def update_menu_item(event_id: str, item_id: str, request: UpdateEventMenuItemRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier un item de menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    result = await event_menu_items_collection().update_one(
        {"item_id": item_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    
    item = await event_menu_items_collection().find_one(
        {"item_id": item_id},
        {"_id": 0}
    )
    return item

@events_router.delete("/{event_id}/menu/items/{item_id}")
async def delete_menu_item(event_id: str, item_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer un item de menu"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await event_menu_items_collection().update_one(
        {"item_id": item_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    
    return {"message": "Item supprimé"}

# ==================== PRICE PACKAGES ENDPOINTS ====================

@events_router.post("/{event_id}/menu/packages")
async def create_price_package(event_id: str, request: CreatePricePackageRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer un package de prix (ex: Entrée + Plat = 25€)"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    package_id = f"package_{uuid.uuid4().hex[:12]}"
    package = {
        "package_id": package_id,
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "name": request.name,
        "section_ids": request.section_ids,
        "price": request.price,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await price_packages_collection().insert_one(package)
    package.pop("_id", None)
    return package

@events_router.get("/{event_id}/menu/packages")
async def list_price_packages(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les packages de prix d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    packages = await price_packages_collection().find(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).to_list(length=1000)
    
    return packages

@events_router.put("/{event_id}/menu/packages/{package_id}")
async def update_price_package(event_id: str, package_id: str, request: UpdatePricePackageRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier un package de prix"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    result = await price_packages_collection().update_one(
        {"package_id": package_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Package non trouvé")
    
    package = await price_packages_collection().find_one(
        {"package_id": package_id},
        {"_id": 0}
    )
    return package

@events_router.delete("/{event_id}/menu/packages/{package_id}")
async def delete_price_package(event_id: str, package_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer un package de prix"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await price_packages_collection().update_one(
        {"package_id": package_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Package non trouvé")
    
    return {"message": "Package supprimé"}

# ==================== DRINK OPTIONS ENDPOINTS ====================

@events_router.post("/{event_id}/menu/drinks")
async def create_drink_option(event_id: str, request: CreateDrinkOptionRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Créer une option de boisson"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    drink_id = f"drink_{uuid.uuid4().hex[:12]}"
    drink = {
        "drink_id": drink_id,
        "event_id": event_id,
        "restaurant_id": current_user["restaurant_id"],
        "name": request.name,
        "price": request.price,
        "is_selected": False,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }
    
    await drink_options_collection().insert_one(drink)
    drink.pop("_id", None)
    return drink

@events_router.get("/{event_id}/menu/drinks")
async def list_drink_options(event_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Lister les options de boissons d'un événement"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    drinks = await drink_options_collection().find(
        {"event_id": event_id, "restaurant_id": current_user["restaurant_id"], "is_active": True},
        {"_id": 0}
    ).to_list(length=1000)
    
    return drinks

@events_router.put("/{event_id}/menu/drinks/{drink_id}")
async def update_drink_option(event_id: str, drink_id: str, request: UpdateDrinkOptionRequest, current_user: dict = Depends(lambda: _get_current_user)):
    """Modifier une option de boisson"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    result = await drink_options_collection().update_one(
        {"drink_id": drink_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Boisson non trouvée")
    
    drink = await drink_options_collection().find_one(
        {"drink_id": drink_id},
        {"_id": 0}
    )
    return drink

@events_router.delete("/{event_id}/menu/drinks/{drink_id}")
async def delete_drink_option(event_id: str, drink_id: str, current_user: dict = Depends(lambda: _get_current_user)):
    """Supprimer une option de boisson"""
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await drink_options_collection().update_one(
        {"drink_id": drink_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Boisson non trouvée")
    
    return {"message": "Boisson supprimée"}

# ==================== FILE DOWNLOAD ENDPOINTS ====================

@events_router.get("/{event_id}/providers/{provider_id}/download/{file_type}")
async def download_provider_file(
    event_id: str, 
    provider_id: str, 
    file_type: str,
    current_user: dict = Depends(lambda: _get_current_user)
):
    """Télécharger un fichier d'un prestataire (quote, invoice, payment_proof)"""
    from fastapi.responses import FileResponse
    
    current_user = await _get_current_user()
    
    if not has_event_access(current_user, "read_only"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if file_type not in ["quote", "invoice", "payment_proof"]:
        raise HTTPException(status_code=400, detail="Type de fichier invalide")
    
    provider = await providers_collection().find_one(
        {"provider_id": provider_id, "event_id": event_id, "restaurant_id": current_user["restaurant_id"]}
    )
    
    if not provider:
        raise HTTPException(status_code=404, detail="Prestataire non trouvé")
    
    file_path = provider.get(f"{file_type}_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    
    return FileResponse(file_path, filename=os.path.basename(file_path))
