"""
Modèles Pydantic pour le module Événements
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

# ==================== EVENT MODELS ====================

class CreateEventRequest(BaseModel):
    """Créer un nouvel événement"""
    title: str
    date: str  # Format: YYYY-MM-DD
    description: Optional[str] = None
    notes: Optional[str] = None

class UpdateEventRequest(BaseModel):
    """Modifier un événement"""
    title: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class DuplicateEventRequest(BaseModel):
    """Dupliquer un événement"""
    new_title: Optional[str] = None  # Si non fourni, on ajoute " (copie)" au titre
    new_date: Optional[str] = None   # Si non fourni, on garde la même date

# ==================== PROVIDER (PRESTATAIRE) MODELS ====================

class CreateProviderRequest(BaseModel):
    """Créer un prestataire pour un événement"""
    name: str  # Nom du prestataire (DJ, Magicien, etc.)
    contact_name: Optional[str] = None  # Nom de la personne contact
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

class UpdateProviderRequest(BaseModel):
    """Modifier un prestataire"""
    name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    # Statut du devis
    quote_status: Optional[str] = None  # "pending", "validated"
    # Statut de la facture
    invoice_status: Optional[str] = None  # "pending", "awaiting_payment", "paid"
    payment_method: Optional[str] = None  # "cash", "card", "transfer", "check"
    is_active: Optional[bool] = None

class ValidateQuoteRequest(BaseModel):
    """Valider un devis"""
    validated: bool = True

class UpdateInvoiceStatusRequest(BaseModel):
    """Mettre à jour le statut de la facture"""
    status: str  # "pending", "awaiting_payment", "paid"
    payment_method: Optional[str] = None  # Requis si status == "paid"

# ==================== TASK (TÂCHE) MODELS ====================

class CreateEventTaskRequest(BaseModel):
    """Créer une tâche pour un événement"""
    title: str
    description: Optional[str] = None
    due_date: str  # Format: YYYY-MM-DD
    assigned_user_id: Optional[str] = None  # ID de l'utilisateur assigné

class UpdateEventTaskRequest(BaseModel):
    """Modifier une tâche d'événement"""
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    assigned_user_id: Optional[str] = None
    status: Optional[str] = None  # "todo", "in_progress", "completed"
    is_active: Optional[bool] = None

class UpdateTaskStatusRequest(BaseModel):
    """Modifier uniquement le statut d'une tâche (pour les utilisateurs avec permissions limitées)"""
    status: str  # "todo", "in_progress", "completed"

# ==================== EVENT MENU MODELS ====================

class EventMenuSection(BaseModel):
    """Section du menu événement (Entrée, Plat, Dessert)"""
    name: str
    order: int = 0

class EventMenuItem(BaseModel):
    """Item dans une section du menu"""
    name: str
    description: Optional[str] = None
    order: int = 0

class CreateEventMenuSectionRequest(BaseModel):
    """Créer une section de menu pour l'événement"""
    name: str
    order: Optional[int] = None

class UpdateEventMenuSectionRequest(BaseModel):
    """Modifier une section de menu"""
    name: Optional[str] = None
    order: Optional[int] = None

class CreateEventMenuItemRequest(BaseModel):
    """Créer un item dans une section de menu"""
    section_id: str
    name: str
    description: Optional[str] = None
    order: Optional[int] = None

class UpdateEventMenuItemRequest(BaseModel):
    """Modifier un item de menu"""
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

# ==================== MENU PRICING MODELS ====================

class MenuPricePackage(BaseModel):
    """Package de prix (ex: Entrée + Plat = 25€)"""
    name: str  # Ex: "Entrée + Plat"
    section_ids: List[str]  # IDs des sections incluses
    price: float

class CreatePricePackageRequest(BaseModel):
    """Créer un package de prix"""
    name: str
    section_ids: List[str]
    price: float

class UpdatePricePackageRequest(BaseModel):
    """Modifier un package de prix"""
    name: Optional[str] = None
    section_ids: Optional[List[str]] = None
    price: Optional[float] = None

# ==================== DRINKS SELECTION MODELS ====================

class DrinkOption(BaseModel):
    """Option de boisson avec prix"""
    name: str
    price: float
    is_selected: bool = False

class CreateDrinkOptionRequest(BaseModel):
    """Créer une option de boisson"""
    name: str
    price: float

class UpdateDrinkOptionRequest(BaseModel):
    """Modifier une option de boisson"""
    name: Optional[str] = None
    price: Optional[float] = None
    is_selected: Optional[bool] = None

# ==================== USER PERMISSION LEVELS ====================

# Les niveaux de permission pour le module Événements:
# - "admin" ou "manager": Accès complet (CRUD sur tout)
# - "read_only": Lecture seule (peut voir mais pas modifier)
# - "task_status_only": Peut uniquement changer le statut des tâches assignées

EVENT_PERMISSION_LEVELS = {
    "admin": "Accès complet",
    "read_only": "Lecture seule",
    "task_status_only": "Mise à jour tâches uniquement"
}
