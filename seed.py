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
            ("ARV", "dolutégravir", "50 mg", "comprimé", "McLeods", "McLeods", "SD Pharmaceutical"),
            ("ARV", "raltégravir", "400 mg", "comprimé", "Partenaire Inde", "Fabricant Inde", "SD Pharmaceutical"),
            ("oral oncologie", "lenalidomide", "25 mg", "gélule", "Partenaire Inde", "Fabricant Inde", "AT Pharma"),
            ("oral oncologie", "nintedanib", "150 mg", "capsule", "Partenaire Chine", "Fabricant Chine", "AT Pharma"),
            ("hormones orales", "progesterone micronisée", "200 mg", "capsule", "Partenaire Europe", "AT Pharma", "AT Pharma"),
            ("capsules dures", "ibuprofène", "400 mg", "gélule", "Local", "AT Pharma", "AT Pharma"),
        ]

        if db.query(Product).count() == 0:
            for line, dci, dosage, form, supplier, manufacturer, distributor in examples:
                p = Product(
                    production_line=line,
                    dci=dci,
                    dosage=dosage,
                    form=form,
                    product_key=normalize_product_key(dci, dosage, form),
                    supplier=supplier,
                    manufacturer=manufacturer,
                    distributor=distributor,
                )
                db.add(p)
            db.commit()
    finally:
        db.close()
