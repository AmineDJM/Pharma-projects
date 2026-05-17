import streamlit as st
import pandas as pd
from sqlalchemy import inspect
from db import init_db, get_session, Product, CellComment, User, UserPermission, ProductionLine
from auth import (
    create_default_admin, login_widget, current_user, logout_button, is_admin,
    hash_password, accessible_lines, accessible_categories,
    can_edit_line_category, can_view_line_category
)
from seed import seed_data
from config import CATEGORIES, COLUMN_LABELS, SELECT_OPTIONS, STATUS_COLORS
from utils import normalize_product_key, now_iso, completion_score

st.set_page_config(page_title="Pharma Project Tracker", layout="wide")

init_db()
create_default_admin()
seed_data()

CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.4rem;}
.section-header {
    padding: 0.55rem 0.75rem;
    border-radius: 0.7rem;
    background: #f3f5f7;
    border: 1px solid #e2e6ea;
    margin-top: 1.1rem;
    font-weight: 700;
}
.confidential {
    padding: 0.55rem;
    background: #f7f7f7;
    color: #777;
    border: 1px dashed #bbb;
    border-radius: 0.5rem;
}
.metric-card {
    padding: 1rem;
    border: 1px solid #e7e7e7;
    border-radius: 1rem;
    background: white;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def product_to_dict(p):
    return {c.name: getattr(p, c.name) for c in Product.__table__.columns}

def get_products(line):
    db = get_session()
    try:
        rows = db.query(Product).filter_by(production_line=line).all()
        return [product_to_dict(p) for p in rows]
    finally:
        db.close()

def update_product(product_id, updates):
    db = get_session()
    try:
        p = db.query(Product).filter_by(id=product_id).first()
        if not p:
            return
        for k, v in updates.items():
            if hasattr(p, k):
                setattr(p, k, "" if pd.isna(v) else str(v))
        if any(k in updates for k in ["dci", "dosage", "form"]):
            p.product_key = normalize_product_key(p.dci, p.dosage, p.form)
        db.commit()
    finally:
        db.close()

def add_comment(product_id, column_name, author, comment_type, text, comment_date):
    db = get_session()
    try:
        c = CellComment(
            product_id=product_id,
            column_name=column_name,
            author=author,
            comment_type=comment_type,
            text=text,
            comment_date=comment_date,
        )
        db.add(c)
        db.commit()
    finally:
        db.close()

def get_comments(product_id, column_name=None):
    db = get_session()
    try:
        q = db.query(CellComment).filter_by(product_id=product_id)
        if column_name:
            q = q.filter_by(column_name=column_name)
        rows = q.order_by(CellComment.id.desc()).all()
        return [
            {
                "id": c.id,
                "column_name": c.column_name,
                "author": c.author,
                "comment_type": c.comment_type,
                "text": c.text,
                "comment_date": c.comment_date,
            }
            for c in rows
        ]
    finally:
        db.close()

def styled_df(df):
    def style_cell(val):
        color = STATUS_COLORS.get(str(val), "")
        return f"background-color: {color}" if color else ""
    return df.style.applymap(style_cell)

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

def dashboard(user):
    st.title("Dashboard global")
    lines = accessible_lines(user)
    all_rows = []
    for line in lines:
        all_rows.extend(get_products(line))
    df = pd.DataFrame(all_rows)
    if df.empty:
        st.info("Aucun produit accessible.")
        return
    df["completion"] = df.apply(lambda r: completion_score(r.to_dict()), axis=1)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Produits", len(df))
    c2.metric("Bloqués", int((df["global_status"] == "Bloqué").sum()))
    c3.metric("Ready for launch", int((df["global_status"] == "Ready for launch").sum()))
    c4.metric("Avancement moyen", f"{int(df['completion'].mean())}%")

    st.subheader("Avancement par ligne")
    progress = df.groupby("production_line")["completion"].mean().round(0).reset_index()
    st.bar_chart(progress.set_index("production_line"))

    st.subheader("Produits critiques")
    critical = df[(df["global_status"] == "Bloqué") | (df["priority"] == "Haute")]
    if critical.empty:
        st.success("Aucun produit critique.")
    else:
        show = critical[["production_line", "product_key", "priority", "global_status", "dossier_available", "regulatory_status"]]
        show = show.rename(columns=COLUMN_LABELS)
        st.dataframe(show, use_container_width=True, hide_index=True)

def production_line_page(user):
    st.title("Suivi par ligne de production")
    lines = accessible_lines(user)
    if not lines:
        st.warning("Aucune ligne accessible pour cet utilisateur.")
        return

    line = st.sidebar.selectbox("Ligne de production", lines)
    st.subheader(line)

    rows = get_products(line)
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("Aucun produit dans cette ligne.")
        return

    df["completion"] = df.apply(lambda r: completion_score(r.to_dict()), axis=1)

    visible_cols = visible_columns_for(user, line)
    if "completion" not in visible_cols:
        visible_cols.append("completion")
    visible_cols = [c for c in visible_cols if c in df.columns]

    st.caption("Clique sur une ligne dans le tableau puis ouvre la fiche produit en dessous. Les cellules importantes ont des commentaires détaillés dans la fiche.")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        priority = st.multiselect("Priorité", ["Haute", "Moyenne", "Basse"], default=[])
    with filter_col2:
        status = st.multiselect("Statut global", ["Pas commencé", "En cours", "Bloqué", "Validé", "On hold", "Ready for launch"], default=[])
    with filter_col3:
        search = st.text_input("Recherche produit / fournisseur")

    filtered = df.copy()
    if priority:
        filtered = filtered[filtered["priority"].isin(priority)]
    if status:
        filtered = filtered[filtered["global_status"].isin(status)]
    if search:
        s = search.lower()
        filtered = filtered[filtered.apply(lambda r: s in " ".join([str(x).lower() for x in r.values]), axis=1)]

    display = filtered[visible_cols].copy()
    display = display.rename(columns=COLUMN_LABELS)

    st.dataframe(styled_df(display), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Modifier rapidement le tableau")
    editable_cols = editable_columns_for(user, line)
    if not editable_cols:
        st.info("Lecture seule : tu n'as pas accès en édition sur cette ligne.")
    else:
        edit_df = filtered[["id"] + [c for c in visible_cols if c != "id" and c != "completion"]].copy()
        column_config = {}
        disabled = ["id"]
        for c in edit_df.columns:
            label = COLUMN_LABELS.get(c, c)
            if c in SELECT_OPTIONS:
                column_config[c] = st.column_config.SelectboxColumn(label, options=SELECT_OPTIONS[c])
            else:
                column_config[c] = st.column_config.TextColumn(label)
            if c not in editable_cols and c != "id":
                disabled.append(c)
        edited = st.data_editor(
            edit_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
            disabled=disabled,
            key=f"editor_{line}",
        )
        if st.button("Enregistrer les modifications", type="primary"):
            original = edit_df.set_index("id")
            new = edited.set_index("id")
            changes = 0
            for pid in new.index:
                updates = {}
                for col in new.columns:
                    if col in editable_cols:
                        old_v = "" if pd.isna(original.loc[pid, col]) else str(original.loc[pid, col])
                        new_v = "" if pd.isna(new.loc[pid, col]) else str(new.loc[pid, col])
                        if old_v != new_v:
                            updates[col] = new_v
                if updates:
                    update_product(int(pid), updates)
                    changes += 1
            st.success(f"{changes} produit(s) modifié(s).")
            st.rerun()

    st.markdown("---")
    st.subheader("Fiche détaillée produit")
    product_options = {f"{r['product_key']} | #{r['id']}": r["id"] for _, r in filtered.iterrows()}
    selected_label = st.selectbox("Produit", list(product_options.keys()))
    if selected_label:
        product_detail(user, line, product_options[selected_label])

def product_detail(user, line, product_id):
    db = get_session()
    try:
        p = db.query(Product).filter_by(id=product_id).first()
        if not p:
            st.error("Produit introuvable.")
            return
        row = product_to_dict(p)
    finally:
        db.close()

    st.markdown(f"### {row['product_key']}")
    st.progress(completion_score(row) / 100, text=f"Avancement automatique : {completion_score(row)}%")

    tabs = st.tabs(list(CATEGORIES.keys()) + ["Commentaires cellule"])
    for i, (category, cols) in enumerate(CATEGORIES.items()):
        with tabs[i]:
            if not can_view_line_category(user, line, category):
                st.markdown('<div class="confidential">Confidentiel — accès non autorisé.</div>', unsafe_allow_html=True)
                continue
            st.markdown(f'<div class="section-header">{category}</div>', unsafe_allow_html=True)
            can_edit = can_edit_line_category(user, line, category)
            updates = {}
            for c in cols:
                label = COLUMN_LABELS.get(c, c)
                current = row.get(c, "")
                if c == "product_key":
                    st.text_input(label, value=current, disabled=True, key=f"{product_id}_{c}_readonly")
                    continue
                if c in SELECT_OPTIONS:
                    options = SELECT_OPTIONS[c]
                    idx = options.index(current) if current in options else 0
                    val = st.selectbox(label, options, index=idx, disabled=not can_edit, key=f"{product_id}_{c}")
                else:
                    if "comment" in c or "reserve" in c or "issue" in c or "competitors" in c or "equipment" in c or "action" in c:
                        val = st.text_area(label, value=current or "", disabled=not can_edit, key=f"{product_id}_{c}")
                    else:
                        val = st.text_input(label, value=current or "", disabled=not can_edit, key=f"{product_id}_{c}")
                if can_edit and str(val) != str(current or ""):
                    updates[c] = val
            if can_edit and st.button(f"Enregistrer {category}", key=f"save_{category}_{product_id}"):
                update_product(product_id, updates)
                st.success("Modifications enregistrées.")
                st.rerun()

    with tabs[-1]:
        st.markdown("### Ajouter un détail / réserve / réponse sur une cellule")
        accessible_cols = []
        for cat, cols in CATEGORIES.items():
            if can_view_line_category(user, line, cat):
                accessible_cols.extend(cols)
        selected_col = st.selectbox(
            "Cellule concernée",
            accessible_cols,
            format_func=lambda x: COLUMN_LABELS.get(x, x),
            key=f"comment_col_{product_id}"
        )
        can_comment = any(selected_col in cols and can_edit_line_category(user, line, cat) for cat, cols in CATEGORIES.items())
        comment_type = st.selectbox("Type", ["Commentaire", "Réserve", "Réponse réserve", "Décision", "Blocage"])
        comment_date = st.text_input("Date", value=now_iso())
        text = st.text_area("Texte détaillé")
        if st.button("Ajouter le commentaire", disabled=not can_comment):
            if not text.strip():
                st.error("Le texte est vide.")
            else:
                add_comment(product_id, selected_col, current_user()["username"], comment_type, text, comment_date)
                st.success("Commentaire ajouté.")
                st.rerun()

        st.markdown("### Historique")
        comments = get_comments(product_id)
        if not comments:
            st.info("Aucun commentaire.")
        else:
            cdf = pd.DataFrame(comments)
            cdf["cellule"] = cdf["column_name"].map(lambda x: COLUMN_LABELS.get(x, x))
            st.dataframe(cdf[["comment_date", "author", "cellule", "comment_type", "text"]], use_container_width=True, hide_index=True)

def admin_page():
    st.title("Administration")
    if not is_admin():
        st.error("Accès admin uniquement.")
        return

    tab_users, tab_lines, tab_products, tab_export = st.tabs(["Utilisateurs & accès", "Lignes de production", "Ajouter produit", "Export"])

    with tab_users:
        st.subheader("Créer un utilisateur")
        with st.form("create_user"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Rôle", ["editor", "viewer", "admin"])
            submit = st.form_submit_button("Créer")
            if submit:
                if not username or not password:
                    st.error("Username/password requis.")
                else:
                    db = get_session()
                    try:
                        if db.query(User).filter_by(username=username).first():
                            st.error("Utilisateur déjà existant.")
                        else:
                            db.add(User(username=username, password_hash=hash_password(password), role=role, is_active=True))
                            db.commit()
                            st.success("Utilisateur créé.")
                    finally:
                        db.close()

        st.subheader("Gérer les accès")
        db = get_session()
        try:
            users = db.query(User).all()
            lines = [x.name for x in db.query(ProductionLine).all()]
        finally:
            db.close()

        user_map = {f"{u.username} ({u.role})": u.id for u in users}
        selected_user = st.selectbox("Utilisateur", list(user_map.keys()))
        selected_user_id = user_map[selected_user]
        selected_line = st.selectbox("Ligne", lines)
        st.write("Catégories")
        for cat in CATEGORIES.keys():
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(cat)
            view = col2.checkbox("Voir", key=f"view_{selected_user_id}_{selected_line}_{cat}")
            edit = col3.checkbox("Éditer", key=f"edit_{selected_user_id}_{selected_line}_{cat}")
            if st.button(f"Enregistrer accès {cat}", key=f"perm_{selected_user_id}_{selected_line}_{cat}"):
                db = get_session()
                try:
                    perm = db.query(UserPermission).filter_by(user_id=selected_user_id, production_line=selected_line, category=cat).first()
                    if not perm:
                        perm = UserPermission(user_id=selected_user_id, production_line=selected_line, category=cat)
                        db.add(perm)
                    perm.can_view = view
                    perm.can_edit = edit
                    db.commit()
                    st.success(f"Accès enregistré pour {cat}.")
                finally:
                    db.close()

    with tab_lines:
        st.subheader("Ajouter une ligne de production")
        name = st.text_input("Nom de la ligne")
        desc = st.text_area("Description")
        if st.button("Créer la ligne"):
            db = get_session()
            try:
                if db.query(ProductionLine).filter_by(name=name).first():
                    st.error("Cette ligne existe déjà.")
                else:
                    db.add(ProductionLine(name=name, description=desc))
                    db.commit()
                    st.success("Ligne créée.")
                    st.rerun()
            finally:
                db.close()

    with tab_products:
        st.subheader("Ajouter un produit")
        db = get_session()
        try:
            lines = [x.name for x in db.query(ProductionLine).all()]
        finally:
            db.close()

        with st.form("add_product"):
            line = st.selectbox("Ligne", lines)
            dci = st.text_input("DCI", placeholder="dolutégravir")
            dosage = st.text_input("Dosage", placeholder="50 mg")
            form = st.text_input("Forme", placeholder="comprimé / capsule / injectable")
            supplier = st.text_input("Fournisseur")
            manufacturer = st.text_input("Fabricant")
            distributor = st.text_input("Distributeur")
            priority = st.selectbox("Priorité", ["Haute", "Moyenne", "Basse"])
            submit = st.form_submit_button("Ajouter")
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
                        priority=priority,
                    )
                    db.add(p)
                    db.commit()
                    st.success(f"Produit ajouté : {product_key}")
                finally:
                    db.close()

    with tab_export:
        st.subheader("Export Excel")
        db = get_session()
        try:
            rows = [product_to_dict(p) for p in db.query(Product).all()]
        finally:
            db.close()
        if rows:
            df = pd.DataFrame(rows)
            out = "pharma_project_tracker_export.xlsx"
            df.to_excel(out, index=False)
            with open(out, "rb") as f:
                st.download_button("Télécharger Excel", f, file_name=out)
        else:
            st.info("Aucune donnée à exporter.")

def main():
    user = current_user()
    if not user:
        login_widget()
        return

    st.sidebar.success(f"Connecté : {user['username']} ({user['role']})")
    logout_button()

    page = st.sidebar.radio("Navigation", ["Dashboard", "Lignes de production", "Admin"])
    if page == "Dashboard":
        dashboard(user)
    elif page == "Lignes de production":
        production_line_page(user)
    elif page == "Admin":
        admin_page()

if __name__ == "__main__":
    main()
