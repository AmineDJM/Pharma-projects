import os
import streamlit as st
import pandas as pd
from io import BytesIO
from db import init_db, get_session, Product, User, UserPermission, ProductionLine, ChangeLog
from auth import (
    create_default_admin, login_widget, current_user, logout_button, is_admin,
    hash_password, accessible_lines, can_edit_line_category, can_view_line_category
)
from seed import seed_data
from config import CATEGORIES, COLUMN_LABELS, SELECT_OPTIONS, STATUS_COLORS, CATEGORY_COLORS, DOCUMENT_COLUMNS
from utils import normalize_product_key, now_iso, completion_score, safe_filename

st.set_page_config(page_title="AT Pharma — Excel Only Tracker", layout="wide", initial_sidebar_state="collapsed")

init_db()
create_default_admin()
seed_data()

UPLOAD_DIR = "uploaded_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 0.4rem !important;
    padding-left: 0.7rem !important;
    padding-right: 0.7rem !important;
    max-width: 100% !important;
}
[data-testid="stHeader"] {height: 0rem;}
.main-title {
    font-size: clamp(18px, 2vw, 28px);
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.toolbar {
    border: 1px solid #d9dee3;
    border-radius: 14px;
    padding: 8px 10px 2px 10px;
    background: #fbfbfc;
    margin-bottom: 8px;
}
.category-strip {
    display: flex;
    width: max-content;
    min-width: 100%;
    border: 1px solid #cbd5e1;
    border-bottom: 0;
    border-radius: 10px 10px 0 0;
    overflow: hidden;
    font-size: 11px;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
.category-cell {
    padding: 8px 8px;
    text-align: center;
    border-right: 1px solid #cbd5e1;
    color: #111827;
    white-space: nowrap;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #cbd5e1;
    border-radius: 0 0 10px 10px;
}
.stDataFrame div {
    font-size: clamp(10px, 0.8vw, 13px);
}
.small-note {
    font-size: 11px;
    color: #6b7280;
}
@media (max-width: 900px) {
    .category-cell {font-size: 9px; padding: 6px 4px;}
    .block-container {padding-left: 0.3rem !important; padding-right: 0.3rem !important;}
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def product_to_dict(p):
    return {c.name: getattr(p, c.name) for c in Product.__table__.columns}

def get_products(line=None):
    db = get_session()
    try:
        q = db.query(Product)
        if line:
            q = q.filter_by(production_line=line)
        rows = q.all()
        return [product_to_dict(p) for p in rows]
    finally:
        db.close()

def log_change(db, product, column_name, old, new, user, change_type="cell_update"):
    db.add(ChangeLog(
        product_id=product.id if product else None,
        product_key=product.product_key if product else "",
        production_line=product.production_line if product else "",
        column_name=column_name,
        old_value="" if old is None else str(old),
        new_value="" if new is None else str(new),
        changed_by=user["username"],
        change_type=change_type,
        changed_at=now_iso(),
    ))

def update_products_cellwise(changes_by_product, user):
    """Sauvegarde cellule-par-cellule : relit la DB au moment du save, applique seulement les cellules modifiées."""
    db = get_session()
    saved = 0
    try:
        for product_id, updates in changes_by_product.items():
            p = db.query(Product).filter_by(id=int(product_id)).first()
            if not p:
                continue
            for col, new_value in updates.items():
                if not hasattr(p, col):
                    continue
                old_value = getattr(p, col)
                new_value = "" if pd.isna(new_value) else str(new_value)
                if str(old_value or "") != new_value:
                    setattr(p, col, new_value)
                    log_change(db, p, col, old_value, new_value, user, "cell_update")
                    saved += 1
            if any(k in updates for k in ["dci", "dosage", "form"]):
                old_key = p.product_key
                p.product_key = normalize_product_key(p.dci, p.dosage, p.form)
                if old_key != p.product_key:
                    log_change(db, p, "product_key", old_key, p.product_key, user, "auto_update")
            p.row_version = (p.row_version or 1) + 1
        db.commit()
    finally:
        db.close()
    return saved

def upload_document(product_id, column_name, uploaded_file, user):
    db = get_session()
    try:
        p = db.query(Product).filter_by(id=int(product_id)).first()
        if not p:
            return False, "Produit introuvable."
        product_dir = os.path.join(UPLOAD_DIR, str(product_id), column_name)
        os.makedirs(product_dir, exist_ok=True)
        filename = f"{now_iso().replace(':','-').replace(' ','_')}_{safe_filename(uploaded_file.name)}"
        path = os.path.join(product_dir, filename)
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        old = getattr(p, column_name, "")
        display_value = filename
        setattr(p, column_name, display_value)
        log_change(db, p, column_name, old, display_value, user, "file_upload")
        p.row_version = (p.row_version or 1) + 1
        db.commit()
        return True, filename
    finally:
        db.close()

def list_document_files(product_id, column_name):
    folder = os.path.join(UPLOAD_DIR, str(product_id), column_name)
    if not os.path.exists(folder):
        return []
    return sorted([os.path.join(folder, x) for x in os.listdir(folder)], reverse=True)

def visible_columns_for(user, line):
    cols = ["id"]
    for category, category_cols in CATEGORIES.items():
        if can_view_line_category(user, line, category):
            cols.extend(category_cols)
    return list(dict.fromkeys(cols))

def editable_columns_for(user, line):
    cols = []
    for category, category_cols in CATEGORIES.items():
        if can_edit_line_category(user, line, category):
            cols.extend(category_cols)
    return cols

def category_for_col(col):
    for cat, cols in CATEGORIES.items():
        if col in cols:
            return cat
    return ""

def display_label(col):
    if col == "id":
        return "ID"
    if col == "completion":
        return "Avancement %"
    cat = category_for_col(col)
    label = COLUMN_LABELS.get(col, col)
    # La catégorie est intégrée dans le header de chaque colonne pour éviter toute ambiguïté.
    return f"{cat} ▸ {label}" if cat else label

def style_table(df):
    def cell_style(val):
        color = STATUS_COLORS.get(str(val), "")
        if color:
            return f"background-color:{color}; font-weight:700; color:#111827;"
        return ""
    return df.style.map(cell_style)

def render_category_strip(visible_raw_cols):
    visible_without_id = [c for c in visible_raw_cols if c not in ["id", "completion"]]
    chunks = []
    for cat, cols in CATEGORIES.items():
        included = [c for c in cols if c in visible_without_id]
        if included:
            width = max(118 * len(included), 150)
            color = CATEGORY_COLORS.get(cat, "#f3f4f6")
            chunks.append(f'<div class="category-cell" style="background:{color}; width:{width}px;">{cat}</div>')
    st.markdown('<div class="category-strip">' + "".join(chunks) + "</div>", unsafe_allow_html=True)

def excel_export(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="tracker", index=False)
        workbook = writer.book
        worksheet = writer.sheets["tracker"]
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#E9ECEF", "border": 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, max(13, min(38, len(str(value)) + 3)))
    output.seek(0)
    return output

def table_page(user):
    lines = accessible_lines(user)
    if not lines:
        st.warning("Aucun accès.")
        return

    st.markdown('<div class="main-title">AT Pharma — Excel Project Tracker</div>', unsafe_allow_html=True)

    # Top toolbar only
    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    top = st.columns([1.1, 1, 1, 1.1, 1.1, 1, 1])
    with top[0]:
        line = st.selectbox("Feuille", lines, label_visibility="collapsed")
    with top[1]:
        priority = st.multiselect("Priorité", ["Haute", "Moyenne", "Basse"], placeholder="Priorité")
    with top[2]:
        status = st.multiselect("Statut", ["Pas commencé", "En cours", "Bloqué", "Validé", "On hold", "Ready for launch"], placeholder="Statut")
    with top[3]:
        search = st.text_input("Recherche", placeholder="Recherche", label_visibility="collapsed")
    with top[4]:
        compact = st.toggle("Compact", value=True)
    with top[5]:
        refresh = st.button("Actualiser")
    with top[6]:
        save_button_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    rows = get_products(line)
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("Aucun produit dans cette feuille.")
        return

    df["completion"] = df.apply(lambda r: completion_score(r.to_dict()), axis=1)

    filtered = df.copy()
    if priority:
        filtered = filtered[filtered["priority"].isin(priority)]
    if status:
        filtered = filtered[filtered["global_status"].isin(status)]
    if search:
        s = search.lower()
        filtered = filtered[filtered.apply(lambda r: s in " ".join([str(x).lower() for x in r.values]), axis=1)]

    visible_cols = visible_columns_for(user, line)
    visible_cols = [c for c in visible_cols if c in filtered.columns]
    if "completion" not in visible_cols:
        visible_cols.append("completion")

    if compact:
        long_cols = ["production_comment", "technical_issue", "competitors", "missing_equipment"]
        visible_cols = [c for c in visible_cols if c not in long_cols]

    editable_cols = editable_columns_for(user, line)
    edit_df = filtered[visible_cols].copy()

    # renaming is for display only
    display_cols = {c: display_label(c) for c in edit_df.columns}
    display_df = edit_df.rename(columns=display_cols)

    column_config = {}
    disabled = []
    for c in edit_df.columns:
        dlabel = display_cols[c]
        if c == "id" or c == "completion" or c == "product_key" or c in DOCUMENT_COLUMNS:
            disabled.append(dlabel)
        elif c not in editable_cols:
            disabled.append(dlabel)

        if c in SELECT_OPTIONS:
            column_config[dlabel] = st.column_config.SelectboxColumn(dlabel, options=SELECT_OPTIONS[c], width="small")
        elif c in DOCUMENT_COLUMNS:
            column_config[dlabel] = st.column_config.TextColumn(dlabel, width="medium", disabled=True)
        elif c == "completion":
            column_config[dlabel] = st.column_config.ProgressColumn(dlabel, min_value=0, max_value=100, width="small")
        else:
            width = "medium"
            if c in ["product_key", "dossier_reserve", "anpp_reserves", "next_action_tt"]:
                width = "large"
            column_config[dlabel] = st.column_config.TextColumn(dlabel, width=width)

    # Upload/download is top-only, not below table.
    with st.popover("📎 Documents / cellule"):
        st.caption("Uploader un ZIP/CTD/document dans une cellule documentaire. La cellule du tableau se met à jour avec le nom du fichier.")
        product_options = {f"{r['product_key']} | #{r['id']}": int(r["id"]) for _, r in filtered.iterrows()}
        if product_options:
            selected_product_label = st.selectbox("Produit", list(product_options.keys()))
            doc_col = st.selectbox("Cellule document", list(DOCUMENT_COLUMNS.keys()), format_func=lambda x: DOCUMENT_COLUMNS[x])
            up = st.file_uploader("Déposer fichier", type=None, accept_multiple_files=False)
            if st.button("Uploader dans la cellule"):
                if up is None:
                    st.error("Aucun fichier.")
                else:
                    # Permission = category edit
                    cat = category_for_col(doc_col)
                    if not can_edit_line_category(user, line, cat):
                        st.error("Accès insuffisant.")
                    else:
                        ok, msg = upload_document(product_options[selected_product_label], doc_col, up, user)
                        if ok:
                            st.success(f"Upload OK : {msg}")
                            st.rerun()
                        else:
                            st.error(msg)

            st.markdown("---")
            st.caption("Fichiers existants")
            files = list_document_files(product_options[selected_product_label], doc_col)
            for fpath in files[:8]:
                with open(fpath, "rb") as f:
                    st.download_button(
                        os.path.basename(fpath),
                        f,
                        file_name=os.path.basename(fpath),
                        key=f"dl_{fpath}",
                    )

    with st.popover("➕ Ajouter produit"):
        if is_admin() or user["role"] in ["editor"]:
            add_product_form(line, user)
        else:
            st.info("Accès non autorisé.")

    export_df = filtered[visible_cols].rename(columns=display_cols)
    st.download_button(
        "⬇️ Export Excel",
        excel_export(export_df),
        file_name=f"AT_Pharma_{line.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    render_category_strip(visible_cols)
    edited_display = st.data_editor(
        style_table(display_df),
        use_container_width=True,
        hide_index=True,
        height=720,
        column_config=column_config,
        disabled=disabled,
        num_rows="fixed",
        key=f"excel_editor_{line}",
    )

    # Save button top-right behavior approximated: visible just before table actions in toolbar area.
    if save_button_placeholder.button("💾 Enregistrer", type="primary", use_container_width=True):
        reverse_cols = {v: k for k, v in display_cols.items()}
        edited = edited_display.rename(columns=reverse_cols)
        original = edit_df.set_index("id")
        new = edited.set_index("id")

        changes_by_product = {}
        for pid in new.index:
            updates = {}
            for col in new.columns:
                if col in ["completion"] or col in DOCUMENT_COLUMNS or col == "product_key":
                    continue
                if col in editable_cols:
                    old_v = "" if pd.isna(original.loc[pid, col]) else str(original.loc[pid, col])
                    new_v = "" if pd.isna(new.loc[pid, col]) else str(new.loc[pid, col])
                    if old_v != new_v:
                        updates[col] = new_v
            if updates:
                changes_by_product[int(pid)] = updates

        count = update_products_cellwise(changes_by_product, user)
        st.toast(f"{count} cellule(s) enregistrée(s).", icon="✅")
        st.rerun()

def add_product_form(line, user):
    with st.form(f"add_product_{line}"):
        dci = st.text_input("DCI", placeholder="dolutégravir")
        dosage = st.text_input("Dosage", placeholder="50 mg")
        form = st.text_input("Forme", placeholder="comprimé / capsule / injectable")
        supplier = st.text_input("Fournisseur")
        manufacturer = st.text_input("Fabricant")
        distributor = st.text_input("Distributeur")
        project_manager = st.text_input("Chef de projet")
        priority = st.selectbox("Priorité", ["Haute", "Moyenne", "Basse"])
        submit = st.form_submit_button("Créer")
        if submit:
            db = get_session()
            try:
                product_key = normalize_product_key(dci, dosage, form)
                p = Product(
                    production_line=line,
                    dci=dci.lower().strip(),
                    dosage=dosage.lower().strip(),
                    form=form.lower().strip(),
                    product_key=product_key,
                    supplier=supplier,
                    manufacturer=manufacturer,
                    distributor=distributor,
                    project_manager=project_manager,
                    priority=priority,
                )
                db.add(p)
                db.commit()
                log_change(db, p, "product", "", product_key, user, "create_product")
                db.commit()
                st.success(f"Produit créé : {product_key}")
                st.rerun()
            finally:
                db.close()

def admin_page(user):
    st.title("Admin — accès, utilisateurs, logs")
    if not is_admin():
        st.error("Admin uniquement.")
        return

    tab_users, tab_lines, tab_logs = st.tabs(["Utilisateurs & accès", "Lignes", "Logs / métadonnées"])

    with tab_users:
        st.subheader("Créer utilisateur")
        with st.form("create_user"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Rôle", ["editor", "supplier", "viewer", "admin"])
            submit = st.form_submit_button("Créer")
            if submit:
                db = get_session()
                try:
                    if not username or not password:
                        st.error("Username/password requis.")
                    elif db.query(User).filter_by(username=username).first():
                        st.error("Utilisateur existant.")
                    else:
                        db.add(User(username=username, password_hash=hash_password(password), role=role, is_active=True))
                        db.commit()
                        st.success("Utilisateur créé.")
                finally:
                    db.close()

        st.subheader("Permissions par feuille et catégorie")
        db = get_session()
        try:
            users = db.query(User).all()
            lines = [x.name for x in db.query(ProductionLine).all()]
        finally:
            db.close()

        user_map = {f"{u.username} ({u.role})": u.id for u in users}
        selected_user = st.selectbox("Utilisateur", list(user_map.keys()))
        selected_user_id = user_map[selected_user]
        selected_line = st.selectbox("Feuille", lines)

        for cat in CATEGORIES.keys():
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(cat)
            view = col2.checkbox("Voir", key=f"view_{selected_user_id}_{selected_line}_{cat}")
            edit = col3.checkbox("Éditer", key=f"edit_{selected_user_id}_{selected_line}_{cat}")
            if st.button(f"Sauver {cat}", key=f"perm_{selected_user_id}_{selected_line}_{cat}"):
                db = get_session()
                try:
                    perm = db.query(UserPermission).filter_by(
                        user_id=selected_user_id,
                        production_line=selected_line,
                        category=cat
                    ).first()
                    if not perm:
                        perm = UserPermission(user_id=selected_user_id, production_line=selected_line, category=cat)
                        db.add(perm)
                    perm.can_view = view
                    perm.can_edit = edit
                    db.commit()
                    st.success("Permission enregistrée.")
                finally:
                    db.close()

    with tab_lines:
        st.subheader("Créer une feuille / ligne de production")
        name = st.text_input("Nom")
        desc = st.text_area("Description")
        if st.button("Créer feuille"):
            db = get_session()
            try:
                if db.query(ProductionLine).filter_by(name=name).first():
                    st.error("Existe déjà.")
                else:
                    db.add(ProductionLine(name=name, description=desc))
                    db.commit()
                    st.success("Feuille créée.")
                    st.rerun()
            finally:
                db.close()

    with tab_logs:
        st.subheader("Logs complets")
        db = get_session()
        try:
            logs = db.query(ChangeLog).order_by(ChangeLog.id.desc()).limit(1000).all()
            data = [{
                "date": l.changed_at,
                "user": l.changed_by,
                "type": l.change_type,
                "feuille": l.production_line,
                "produit": l.product_key,
                "cellule": COLUMN_LABELS.get(l.column_name, l.column_name),
                "ancien": l.old_value,
                "nouveau": l.new_value,
            } for l in logs]
        finally:
            db.close()
        ldf = pd.DataFrame(data)
        if ldf.empty:
            st.info("Aucun log.")
        else:
            st.dataframe(ldf, use_container_width=True, hide_index=True, height=620)
            st.download_button(
                "Exporter logs Excel",
                excel_export(ldf),
                file_name="AT_Pharma_logs.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

def main():
    user = current_user()
    if not user:
        login_widget()
        return

    st.sidebar.success(f"{user['username']} ({user['role']})")
    logout_button()
    page = st.sidebar.radio("Navigation", ["Tableau", "Admin"])
    if page == "Tableau":
        table_page(user)
    else:
        admin_page(user)

if __name__ == "__main__":
    main()
