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
    "sirop": "syr",
    "solution": "sol",
    "suspension": "susp",
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
        "priority", "availability_status", "global_status"
    ],
    "Dossier": [
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
    "Enregistrement": [
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

    "dossier_available": "Dossier disponible",
    "module_1": "Module 1",
    "module_2": "Module 2",
    "module_3": "Module 3",
    "module_4": "Module 4",
    "module_5": "Module 5",
    "dossier_reserve": "Réserve dossier",
    "dossier_owner": "Responsable dossier",
    "dossier_deadline": "Deadline dossier complet",

    "site_feasible": "Faisable sur site actuel",
    "specific_equipment_needed": "Besoin équipement spécifique",
    "missing_equipment": "Équipement manquant",
    "oeb_level": "Niveau OEB",
    "containment_needed": "Besoin confinement",
    "dedicated_area_needed": "Besoin zone dédiée",
    "production_comment": "Commentaire production",
    "technical_status": "Statut technique",

    "batch_formula_received": "Batch formula reçue",
    "manufacturing_process_received": "Manufacturing process reçu",
    "analytical_methods_received": "Analytical methods reçues",
    "process_validation_received": "Validation process reçue",
    "pilot_batch_done": "Batch pilote fait",
    "validation_batch_done": "Batch validation fait",
    "technical_issue": "Problème technique",
    "next_action_tt": "Prochaine action TT",
    "tt_owner": "Responsable TT",
    "tt_deadline": "Deadline TT",

    "pre_submission": "Pré-soumission",
    "anpp_submission_date": "Dépôt ANPP",
    "receipt_acknowledged": "Accusé réception",
    "anpp_reserves": "Réserves ANPP",
    "reserve_response_status": "Réponse aux réserves",
    "amm_obtained": "AMM obtenue",
    "estimated_amm_date": "Date AMM estimée",
    "regulatory_status": "Statut réglementaire",

    "room_available": "Salle disponible",
    "hvac_ready": "HVAC prêt",
    "equipment_installed_percent": "Équipements installés %",
    "iq_oq_pq_status": "Qualification IQ/OQ/PQ",
    "cleaning_validated": "Nettoyage validé",
    "personnel_trained": "Personnel formé",
    "sop_available": "SOP disponibles",
    "internal_audit_date": "Audit interne",
    "site_ready_for_product": "Site prêt pour produit",

    "estimated_market": "Marché estimé",
    "channel": "Canal",
    "target_price": "Prix cible",
    "estimated_volume": "Volume estimé",
    "estimated_margin": "Marge estimée",
    "competitors": "Concurrents",
    "market_attractiveness": "Attractivité marché",
    "business_go_no_go": "Go / No Go business",
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
