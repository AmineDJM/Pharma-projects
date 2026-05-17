STATUS_COLORS = {
    "OK": "#D9FDD3",
    "Manquant": "#FFD6D6",
    "Réserve": "#FFE9B3",
    "Oui": "#D9FDD3",
    "Non": "#FFD6D6",
    "Partiel": "#FFE9B3",
    "Haute": "#FFD6D6",
    "Moyenne": "#FFE9B3",
    "Basse": "#D9FDD3",
    "Bloqué": "#FFD6D6",
    "En cours": "#FFE9B3",
    "Validé": "#D9FDD3",
    "Approuvé": "#D9FDD3",
    "Déposé": "#E3F2FD",
    "Non déposé": "#F3F3F3",
    "Ready for launch": "#D9FDD3",
    "À revoir": "#FFE9B3",
    "Go": "#D9FDD3",
    "No Go": "#FFD6D6",
}

CATEGORY_COLORS = {
    "Produit": "#E9ECEF",
    "Dossier réglementaire": "#DDEBFF",
    "Évaluation technique": "#EFE3FF",
    "Tech transfer": "#FFF2CC",
    "Enregistrement ANPP": "#DFF6E4",
    "Site readiness": "#FFE5CC",
    "Business": "#FADADD",
}

FORM_ABBREVIATIONS = {
    "comprimé": "cp",
    "comprime": "cp",
    "tablet": "cp",
    "capsule": "cap",
    "gélule": "gel",
    "gelule": "gel",
    "injectable": "inj",
    "injection": "inj",
    "solution injectable": "inj",
    "sirop": "syr",
    "solution": "sol",
    "suspension": "susp",
    "poudre": "pwd",
}

PRODUCTION_LINES = [
    "ARV",
    "oral oncologie",
    "injectable oncologie",
    "biosimilaires",
    "oral general formulation",
    "hormones orales",
    "capsules molles",
    "capsules dures",
    "injectables classiques",
]

CATEGORIES = {
    "Produit": [
        "product_key", "supplier", "manufacturer", "distributor",
        "priority", "availability_status", "global_status", "project_manager"
    ],
    "Dossier réglementaire": [
        "dossier_available", "module_1", "module_2", "module_3", "module_4", "module_5",
        "dossier_reserve", "dossier_owner", "dossier_deadline"
    ],
    "Évaluation technique": [
        "site_feasible", "specific_equipment_needed", "missing_equipment", "oeb_level",
        "containment_needed", "dedicated_area_needed", "production_comment", "technical_status"
    ],
    "Tech transfer": [
        "batch_formula_received", "manufacturing_process_received", "analytical_methods_received",
        "process_validation_received", "pilot_batch_done", "validation_batch_done",
        "technical_issue", "next_action_tt", "tt_owner", "tt_deadline"
    ],
    "Enregistrement ANPP": [
        "pre_submission", "anpp_submission_date", "receipt_acknowledged", "anpp_reserves",
        "reserve_response_status", "amm_obtained", "estimated_amm_date", "regulatory_status"
    ],
    "Site readiness": [
        "room_available", "hvac_ready", "equipment_installed_percent", "iq_oq_pq_status",
        "cleaning_validated", "personnel_trained", "sop_available", "internal_audit_date",
        "site_ready_for_product"
    ],
    "Business": [
        "estimated_market", "channel", "target_price", "estimated_volume",
        "estimated_margin", "competitors", "market_attractiveness", "business_go_no_go"
    ],
}

COLUMN_LABELS = {
    "product_key": "Produit",
    "supplier": "Fournisseur",
    "manufacturer": "Fabricant",
    "distributor": "Distributeur",
    "priority": "Priorité",
    "availability_status": "Disponibilité",
    "global_status": "Statut global",
    "project_manager": "Chef de projet",

    "dossier_available": "Dossier dispo",
    "module_1": "M1",
    "module_2": "M2",
    "module_3": "M3",
    "module_4": "M4",
    "module_5": "M5",
    "dossier_reserve": "Réserve dossier",
    "dossier_owner": "Resp. dossier",
    "dossier_deadline": "Deadline dossier",

    "site_feasible": "Faisabilité site",
    "specific_equipment_needed": "Équip. spécifique",
    "missing_equipment": "Équip. manquant",
    "oeb_level": "OEB",
    "containment_needed": "Confinement",
    "dedicated_area_needed": "Zone dédiée",
    "production_comment": "Commentaire prod.",
    "technical_status": "Statut technique",

    "batch_formula_received": "Batch formula",
    "manufacturing_process_received": "Process reçu",
    "analytical_methods_received": "Méthodes analytiques",
    "process_validation_received": "Validation process",
    "pilot_batch_done": "Batch pilote",
    "validation_batch_done": "Batch validation",
    "technical_issue": "Problème TT",
    "next_action_tt": "Prochaine action TT",
    "tt_owner": "Resp. TT",
    "tt_deadline": "Deadline TT",

    "pre_submission": "Pré-soumission",
    "anpp_submission_date": "Dépôt ANPP",
    "receipt_acknowledged": "AR reçu",
    "anpp_reserves": "Réserves ANPP",
    "reserve_response_status": "Réponse réserves",
    "amm_obtained": "AMM",
    "estimated_amm_date": "Date AMM estimée",
    "regulatory_status": "Statut ANPP",

    "room_available": "Salle dispo",
    "hvac_ready": "HVAC",
    "equipment_installed_percent": "Équip. installés %",
    "iq_oq_pq_status": "IQ/OQ/PQ",
    "cleaning_validated": "Nettoyage",
    "personnel_trained": "Personnel formé",
    "sop_available": "SOP",
    "internal_audit_date": "Audit interne",
    "site_ready_for_product": "Site prêt",

    "estimated_market": "Marché estimé",
    "channel": "Canal",
    "target_price": "Prix cible",
    "estimated_volume": "Volume",
    "estimated_margin": "Marge",
    "competitors": "Concurrents",
    "market_attractiveness": "Attractivité",
    "business_go_no_go": "Go/No Go",
}

SELECT_OPTIONS = {
    "priority": ["Haute", "Moyenne", "Basse"],
    "availability_status": ["Disponible", "Non disponible", "Partiel", "À confirmer"],
    "global_status": ["Pas commencé", "En cours", "Bloqué", "Validé", "On hold", "Ready for launch"],
    "dossier_available": ["Oui", "Non", "Partiel"],
    "module_1": ["OK", "Manquant", "Réserve"],
    "module_2": ["OK", "Manquant", "Réserve"],
    "module_3": ["OK", "Manquant", "Réserve"],
    "module_4": ["OK", "Manquant", "Réserve", "Non requis"],
    "module_5": ["OK", "Manquant", "Réserve", "Non requis"],
    "site_feasible": ["Oui", "Non", "À confirmer"],
    "specific_equipment_needed": ["Oui", "Non", "À confirmer"],
    "oeb_level": ["OEB 1", "OEB 2", "OEB 3", "OEB 4", "OEB 5", "À confirmer"],
    "containment_needed": ["Oui", "Non", "À confirmer"],
    "dedicated_area_needed": ["Oui", "Non", "À confirmer"],
    "technical_status": ["Non commencé", "En cours", "Validé", "Bloqué"],
    "batch_formula_received": ["Oui", "Non", "Partiel"],
    "manufacturing_process_received": ["Oui", "Non", "Partiel"],
    "analytical_methods_received": ["Oui", "Non", "Partiel"],
    "process_validation_received": ["Oui", "Non", "Partiel"],
    "pilot_batch_done": ["Oui", "Non", "En cours"],
    "validation_batch_done": ["Oui", "Non", "En cours"],
    "pre_submission": ["Oui", "Non", "En cours"],
    "receipt_acknowledged": ["Oui", "Non"],
    "reserve_response_status": ["Non applicable", "En cours", "Envoyée", "Acceptée", "Refusée"],
    "amm_obtained": ["Oui", "Non"],
    "regulatory_status": ["Non déposé", "Déposé", "Réserves", "Approuvé", "Refusé"],
    "room_available": ["Oui", "Non", "Partiel"],
    "hvac_ready": ["Oui", "Non", "Partiel"],
    "iq_oq_pq_status": ["Non", "En cours", "Terminé"],
    "cleaning_validated": ["Oui", "Non", "En cours"],
    "personnel_trained": ["Oui", "Non", "Partiel"],
    "sop_available": ["Oui", "Non", "Partiel"],
    "site_ready_for_product": ["Oui", "Non", "Partiel"],
    "channel": ["PCH", "Ville", "Mixte", "Export", "À confirmer"],
    "market_attractiveness": ["Haute", "Moyenne", "Basse"],
    "business_go_no_go": ["Go", "No Go", "À revoir"],
}
