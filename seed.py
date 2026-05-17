from db import get_session, ProductionLine, Product
from config import PRODUCTION_LINES
from utils import normalize_product_key

def seed_data():
    db = get_session()
    try:
        for line in PRODUCTION_LINES:
            if not db.query(ProductionLine).filter_by(name=line).first():
                db.add(ProductionLine(name=line, description=f"Ligne {line}"))
        db.commit()

        examples = [
            ("ARV", "dolutégravir", "50 mg", "comprimé", "McLeods", "McLeods", "SD Pharmaceutical", "Assia", "Haute", "En cours", "Oui", "OK", "OK", "Réserve", "OK", "OK", "2M USD", "PCH", "Go"),
            ("ARV", "raltégravir", "400 mg", "comprimé", "Partenaire Inde", "AT Pharma", "SD Pharmaceutical", "Yassine", "Haute", "Bloqué", "Partiel", "OK", "OK", "Manquant", "OK", "OK", "8M USD", "PCH", "Go"),
            ("ARV", "darunavir", "600 mg", "comprimé", "Partenaire Inde", "AT Pharma", "SD Pharmaceutical", "Assia", "Moyenne", "Pas commencé", "Non", "Manquant", "Manquant", "Manquant", "Manquant", "Manquant", "600k USD", "PCH", "À revoir"),
            ("oral oncologie", "lenalidomide", "25 mg", "gélule", "Partenaire Inde", "Fabricant Inde", "AT Pharma", "Chef projet 1", "Haute", "En cours", "Partiel", "OK", "OK", "Réserve", "OK", "OK", "À estimer", "PCH", "Go"),
            ("oral oncologie", "nintedanib", "150 mg", "capsule", "Deepak", "Fabricant Inde", "AT Pharma", "Chef projet 2", "Haute", "En cours", "Partiel", "OK", "OK", "Réserve", "OK", "OK", "À estimer", "PCH", "Go"),
            ("hormones orales", "progesterone micronisée", "200 mg", "capsule", "Partenaire Europe", "AT Pharma", "AT Pharma", "Chef projet 3", "Moyenne", "En cours", "Oui", "OK", "OK", "OK", "OK", "OK", "À estimer", "Ville", "Go"),
            ("capsules dures", "ibuprofène", "400 mg", "gélule", "Local", "AT Pharma", "AT Pharma", "Chef projet 4", "Basse", "Pas commencé", "Non", "Manquant", "Manquant", "Manquant", "Manquant", "Manquant", "À estimer", "Ville", "À revoir"),
        ]

        if db.query(Product).count() == 0:
            for row in examples:
                line, dci, dosage, form, supplier, manufacturer, distributor, pm, priority, status, dossier, m1, m2, m3, m4, m5, market, channel, gngo = row
                p = Product(
                    production_line=line,
                    dci=dci,
                    dosage=dosage,
                    form=form,
                    product_key=normalize_product_key(dci, dosage, form),
                    supplier=supplier,
                    manufacturer=manufacturer,
                    distributor=distributor,
                    project_manager=pm,
                    priority=priority,
                    global_status=status,
                    dossier_available=dossier,
                    module_1=m1,
                    module_2=m2,
                    module_3=m3,
                    module_4=m4,
                    module_5=m5,
                    estimated_market=market,
                    channel=channel,
                    business_go_no_go=gngo,
                )
                db.add(p)
            db.commit()
    finally:
        db.close()
