from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func
import os

DB_PATH = os.environ.get("AT_PHARMA_TRACKER_DB", "sqlite:///at_pharma_tracker.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="editor")
    is_active = Column(Boolean, default=True)

class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    production_line = Column(String, nullable=False)
    category = Column(String, nullable=False)
    can_view = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)
    user = relationship("User")
    __table_args__ = (UniqueConstraint("user_id", "production_line", "category"),)

class ProductionLine(Base):
    __tablename__ = "production_lines"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, default="")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    production_line = Column(String, nullable=False)

    dci = Column(String, default="")
    dosage = Column(String, default="")
    form = Column(String, default="")
    product_key = Column(String, default="")

    supplier = Column(String, default="")
    manufacturer = Column(String, default="")
    distributor = Column(String, default="")
    priority = Column(String, default="Moyenne")
    availability_status = Column(String, default="À confirmer")
    global_status = Column(String, default="Pas commencé")
    project_manager = Column(String, default="")

    dossier_available = Column(String, default="Non")
    module_1 = Column(String, default="Manquant")
    module_2 = Column(String, default="Manquant")
    module_3 = Column(String, default="Manquant")
    module_4 = Column(String, default="Manquant")
    module_5 = Column(String, default="Manquant")
    dossier_reserve = Column(Text, default="")
    dossier_owner = Column(String, default="")
    dossier_deadline = Column(String, default="")

    site_feasible = Column(String, default="À confirmer")
    specific_equipment_needed = Column(String, default="À confirmer")
    missing_equipment = Column(Text, default="")
    oeb_level = Column(String, default="À confirmer")
    containment_needed = Column(String, default="À confirmer")
    dedicated_area_needed = Column(String, default="À confirmer")
    production_comment = Column(Text, default="")
    technical_status = Column(String, default="Non commencé")

    batch_formula_received = Column(String, default="Non")
    manufacturing_process_received = Column(String, default="Non")
    analytical_methods_received = Column(String, default="Non")
    process_validation_received = Column(String, default="Non")
    pilot_batch_done = Column(String, default="Non")
    validation_batch_done = Column(String, default="Non")
    technical_issue = Column(Text, default="")
    next_action_tt = Column(Text, default="")
    tt_owner = Column(String, default="")
    tt_deadline = Column(String, default="")

    pre_submission = Column(String, default="Non")
    anpp_submission_date = Column(String, default="")
    receipt_acknowledged = Column(String, default="Non")
    anpp_reserves = Column(Text, default="")
    reserve_response_status = Column(String, default="Non applicable")
    amm_obtained = Column(String, default="Non")
    estimated_amm_date = Column(String, default="")
    regulatory_status = Column(String, default="Non déposé")

    room_available = Column(String, default="Non")
    hvac_ready = Column(String, default="Non")
    equipment_installed_percent = Column(String, default="0")
    iq_oq_pq_status = Column(String, default="Non")
    cleaning_validated = Column(String, default="Non")
    personnel_trained = Column(String, default="Non")
    sop_available = Column(String, default="Non")
    internal_audit_date = Column(String, default="")
    site_ready_for_product = Column(String, default="Non")

    estimated_market = Column(String, default="")
    channel = Column(String, default="À confirmer")
    target_price = Column(String, default="")
    estimated_volume = Column(String, default="")
    estimated_margin = Column(String, default="")
    competitors = Column(Text, default="")
    market_attractiveness = Column(String, default="Moyenne")
    business_go_no_go = Column(String, default="À revoir")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CellComment(Base):
    __tablename__ = "cell_comments"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    column_name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    comment_type = Column(String, default="Commentaire")
    text = Column(Text, nullable=False)
    comment_date = Column(String, nullable=False)
    product = relationship("Product")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()
