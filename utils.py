import re
import unicodedata
from datetime import datetime
from config import FORM_ABBREVIATIONS

def normalize_text(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    return value

def normalize_product_key(dci: str, dosage: str, form: str) -> str:
    dci = normalize_text(dci)
    dosage = normalize_text(dosage)
    form_norm = normalize_text(form)
    abbr = FORM_ABBREVIATIONS.get(form_norm, form_norm)
    return f"{dci} {dosage} {abbr}".strip()

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def completion_score(row: dict) -> int:
    keys = [
        "dossier_available", "module_1", "module_2", "module_3", "module_4", "module_5",
        "site_feasible", "technical_status",
        "batch_formula_received", "manufacturing_process_received", "analytical_methods_received",
        "pilot_batch_done", "validation_batch_done",
        "regulatory_status", "site_ready_for_product", "business_go_no_go",
    ]
    positive = {"OK", "Oui", "Validé", "Terminé", "Approuvé", "Go", "Ready for launch"}
    partial = {"Partiel", "En cours", "Déposé", "À revoir"}
    score = 0
    max_score = len(keys) * 2
    for k in keys:
        v = str(row.get(k, "") or "")
        if v in positive:
            score += 2
        elif v in partial:
            score += 1
    return int(round((score / max_score) * 100)) if max_score else 0
