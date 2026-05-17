import streamlit as st
import pandas as pd
from io import BytesIO
from db import init_db, get_session, Product, CellComment, User, UserPermission, ProductionLine
from auth import (
    create_default_admin, login_widget, current_user, logout_button, is_admin,
    hash_password, accessible_lines, accessible_categories,
    can_edit_line_category, can_view_line_category
)
from seed import seed_data
from config import CATEGORIES, COLUMN_LABELS, SELECT_OPTIONS, STATUS_COLORS, CATEGORY_COLORS
from utils import normalize_product_key, now_iso, completion_score

st.set_page_config(page_title="AT Pharma — Big Excel Tracker", layout="wide", initial_sidebar_state="expanded")

init_db()
create_default_admin()
seed_data()

CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 0.8rem;
    padding-left: 1.2rem;
    padding-right: 1.2rem;
    max-width: 100%;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #d0d7de;
    border-radius: 8px;
}
.category-strip {
    display: flex;
    width: max-content;
    min-width: 100%;
    border: 1px solid #d0d7de;
    border-bottom: 0;
    border-radius: 8px 8px 0 0;
    overflow: hidden;
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.category-cell {
    padding: 8px 10px;
    text-align: center;
    border-right: 1px solid #d0d7de;
    color: #1f2328;
    white-space: nowrap;
}
.toolbar {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px;
    background: #fafafa;
}
.small-caption {
    color: #6b7280;
    font-size: 12px;
}
.confidential {
    padding: 0.55rem;
    background: #f7f7f7;
    color: #777;
    border: 1px dashed #bbb;
    border-radius: 0.5rem;
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

def column_category_map():
    mapping = {}
    for cat, cols in CATEGORIES.items():
        for col in cols:
            mapping[col] = cat
    return mapping

def style_excel_table(df, raw_col_order):
    cat_map = column_category_map()

    def style_cell(val):
        color = STATUS_COLORS.get(str(val), "")
        return f"background-color: {color};"

    styles = pd.DataFrame("", index=df.index, columns=df.columns)

    for display_col in df.columns:
        original_col = None
        for k, v in COLUMN_LABELS.items():
            if v == display_col:
                original_col = k
                break
        if display_col == "ID":
            original_col = "id"

        if original_col:
            cat = cat_map.get(original_col)
            if cat and cat in CATEGORY_COLORS:
                styles[display_col] = f"border-left: 1px solid #d0d7de; background-color: {CATEGORY_COLORS[cat]};"

        for idx in df.index:
            val_style = style_cell(df.loc[idx, display_col])
            if val_style:
                styles.loc[idx, display_col] += val_style + " font-weight: 600;"

    return styles

def render_category_strip(visible_raw_cols):
    # approximation visuelle : largeur fixe par colonne pour créer une ligne de catégories au-dessus du tableau
    visible_without_id = [c for c in visible_raw_cols if c not in ["id"]]
    chunks = []
    for cat, cols in CATEGORIES.items():
        included = [c for c in cols if c in visible_without_id]
        if included:
            width = max(120 * len(included), 160)
            color = CATEGORY_COLORS.get(cat, "#f3f4f6")
            chunks.append(f'<div class="category-cell" style="background:{color}; width:{width}px;">{cat}</div>')
    html = '<div class="category-strip">' + "".join(chunks) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

def excel_export(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="export", index=False)
        workbook = writer.book
        worksheet = writer.sheets["export"]
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#E9ECEF", "border": 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, max(14, min(35, len(str(value)) + 4)))
    output.seek(0)
    return output

def big_excel_tracker(user):
    lines = accessible_lines(user)
    if not lines:
        st.warning("Aucune ligne accessible.")
        return

    st.title("AT Pharma — Big Excel Project Tracker")
    st.caption("Une feuille par ligne de production. Une ligne = un produit. Toutes les catégories sont lisibles horizontalement.")

    line = st.selectbox("Feuille / ligne de production", lines, key="selected_line")

    rows = get_products(line)
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("Aucun produit dans cette ligne.")
        return

    df["completion"] = df.apply(lambda r: completion_score(r.to_dict()), axis=1)

    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns([1,1,1,1.2,1])
    with f1:
        priority = st.multiselect("Priorité", ["Haute", "Moyenne", "Basse"])
    with f2:
        status = st.multiselect("Statut", ["Pas commencé", "En cours", "Bloqué", "Validé", "On hold", "Ready for launch"])
    with f3:
        channel = st.multiselect("Canal", ["PCH", "Ville", "Mixte", "Export", "À confirmer"])
    with f4:
        search = st.text_input("Recherche")
    with f5:
        compact = st.toggle("Mode compact", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = df.copy()
    if priority:
        filtered = filtered[filtered["priority"].isin(priority)]
    if status:
        filtered = filtered[filtered["global_status"].isin(status)]
    if channel:
        filtered = filtered[filtered["channel"].isin(channel)]
    if search:
        s = search.lower()
        filtered = filtered[filtered.apply(lambda r: s in " ".join([str(x).lower() for x in r.values]), axis=1)]

    visible_cols = visible_columns_for(user, line)
    visible_cols = [c for c in visible_cols if c in filtered.columns]
    if "completion" not in visible_cols:
        visible_cols.append("completion")

    if compact:
        # retire certaines colonnes très longues de la vue principale, sans les supprimer de la base
        long_cols = ["production_comment", "technical_issue", "competitors"]
        visible_cols = [c for c in visible_cols if c not in long_cols]

    display = filtered[visible_cols].copy()
    display = display.rename(columns={**COLUMN_LABELS, "id": "ID", "completion": "Avancement %"})

    st.markdown("#### Tableau principal")
    render_category_strip(visible_cols)

    styled = display.style.apply(lambda _: style_excel_table(display, visible_cols), axis=None)
    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        height=520,
    )

    st.markdown("---")
    left, right = st.columns([3, 1])
    with left:
        st.subheader("Édition directe du big tableau")
        editable_cols = editable_columns_for(user, line)
        if not editable_cols:
            st.info("Lecture seule sur cette feuille.")
        else:
            edit_cols = [c for c in visible_cols if c not in ["completion"]]
            edit_df = filtered[edit_cols].copy()
            column_config = {}
            disabled = ["id"]
            for c in edit_df.columns:
                label = COLUMN_LABELS.get(c, "ID" if c == "id" else c)
                if c in SELECT_OPTIONS:
                    column_config[c] = st.column_config.SelectboxColumn(label, options=SELECT_OPTIONS[c], width="small")
                else:
                    width = "medium"
                    if c in ["product_key", "dossier_reserve", "anpp_reserves", "technical_issue", "next_action_tt"]:
                        width = "large"
                    column_config[c] = st.column_config.TextColumn(label, width=width)
                if c not in editable_cols and c != "id":
                    disabled.append(c)

            edited = st.data_editor(
                edit_df,
                use_container_width=True,
                hide_index=True,
                height=420,
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

    with right:
        st.subheader("Actions")
        export_df = filtered[visible_cols].rename(columns={**COLUMN_LABELS, "id": "ID", "completion": "Avancement %"})
        st.download_button(
            "Exporter cette feuille Excel",
            excel_export(export_df),
            file_name=f"AT_Pharma_{line.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        if is_admin():
            with st.expander("+ Ajouter un produit"):
                add_product_form(line)

    st.markdown("---")
    st.subheader("Commentaires cellule / détail discret")
    if filtered.empty:
        st.info("Aucun produit.")
        return

    product_options = {f"{r['product_key']} | #{r['id']}": r["id"] for _, r in filtered.iterrows()}
    c1, c2 = st.columns([1.2, 1])
    with c1:
        selected_label = st.selectbox("Produit", list(product_options.keys()))
    with c2:
        selected_product_id = product_options[selected_label]
        accessible_cols = []
        for cat, cols in CATEGORIES.items():
            if can_view_line_category(user, line, cat):
                accessible_cols.extend(cols)
        selected_col = st.selectbox(
            "Cellule",
            accessible_cols,
            format_func=lambda x: COLUMN_LABELS.get(x, x)
        )

    comments_panel(user, line, selected_product_id, selected_col)

def comments_panel(user, line, product_id, column_name):
    comments = get_comments(product_id, column_name)
    cat_for_col = None
    for cat, cols in CATEGORIES.items():
        if column_name in cols:
            cat_for_col = cat
            break

    can_comment = can_edit_line_category(user, line, cat_for_col) if cat_for_col else False

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown(f"**Cellule sélectionnée :** {COLUMN_LABELS.get(column_name, column_name)}")
        comment_type = st.selectbox("Type", ["Commentaire", "Réserve", "Réponse réserve", "Décision", "Blocage"])
        comment_date = st.text_input("Date", value=now_iso())
        text = st.text_area("Texte")
        if st.button("Ajouter commentaire", disabled=not can_comment):
            if not text.strip():
                st.error("Texte vide.")
            else:
                add_comment(product_id, column_name, current_user()["username"], comment_type, text, comment_date)
                st.success("Commentaire ajouté.")
                st.rerun()

    with col2:
        st.markdown("**Historique de cette cellule**")
        if not comments:
            st.info("Aucun commentaire sur cette cellule.")
        else:
            cdf = pd.DataFrame(comments)
            cdf["cellule"] = cdf["column_name"].map(lambda x: COLUMN_LABELS.get(x, x))
            st.dataframe(cdf[["comment_date", "author", "comment_type", "text"]], use_container_width=True, hide_index=True)

def add_product_form(default_line):
    with st.form(f"add_product_{default_line}"):
        dci = st.text_input("DCI", placeholder="dolutégravir")
        dosage = st.text_input("Dosage", placeholder="50 mg")
        form = st.text_input("Forme", placeholder="comprimé / capsule / injectable")
        supplier = st.text_input("Fournisseur")
        manufacturer = st.text_input("Fabricant")
        distributor = st.text_input("Distributeur")
        project_manager = st.text_input("Chef de projet")
        priority = st.selectbox("Priorité", ["Haute", "Moyenne", "Basse"])
        submit = st.form_submit_button("Ajouter")
        if submit:
            db = get_session()
            try:
                product_key = normalize_product_key(dci, dosage, form)
                p = Product(
                    production_line=default_line,
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
                st.success(f"Produit ajouté : {product_key}")
                st.rerun()
            finally:
                db.close()

def admin_page(user):
    st.title("Administration")
    if not is_admin():
        st.error("Accès admin uniquement.")
        return

    tab_users, tab_lines, tab_export = st.tabs(["Utilisateurs & accès", "Lignes de production", "Export global"])

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

        st.subheader("Gérer les accès par feuille et catégorie")
        db = get_session()
        try:
            users = db.query(User).all()
            lines = [x.name for x in db.query(ProductionLine).all()]
        finally:
            db.close()

        user_map = {f"{u.username} ({u.role})": u.id for u in users}
        selected_user = st.selectbox("Utilisateur", list(user_map.keys()))
        selected_user_id = user_map[selected_user]
        selected_line = st.selectbox("Feuille / ligne", lines)

        for cat in CATEGORIES.keys():
            col1, col2, col3 = st.columns([2,1,1])
            col1.write(cat)
            view = col2.checkbox("Voir", key=f"view_{selected_user_id}_{selected_line}_{cat}")
            edit = col3.checkbox("Éditer", key=f"edit_{selected_user_id}_{selected_line}_{cat}")
            if st.button(f"Enregistrer {cat}", key=f"perm_{selected_user_id}_{selected_line}_{cat}"):
                db = get_session()
                try:
                    perm = db.query(UserPermission).filter_by(
                        user_id=selected_user_id,
                        production_line=selected_line,
                        category=cat
                    ).first()
                    if not perm:
                        perm = UserPermission(
                            user_id=selected_user_id,
                            production_line=selected_line,
                            category=cat
                        )
                        db.add(perm)
                    perm.can_view = view
                    perm.can_edit = edit
                    db.commit()
                    st.success(f"Accès enregistré pour {cat}.")
                finally:
                    db.close()

    with tab_lines:
        st.subheader("Ajouter une ligne de production")
        name = st.text_input("Nom")
        desc = st.text_area("Description")
        if st.button("Créer"):
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

    with tab_export:
        rows = get_products()
        if rows:
            df = pd.DataFrame(rows)
            df["completion"] = df.apply(lambda r: completion_score(r.to_dict()), axis=1)
            out = excel_export(df.rename(columns={**COLUMN_LABELS, "id": "ID", "completion": "Avancement %"}))
            st.download_button(
                "Télécharger export global",
                out,
                file_name="AT_Pharma_Global_Tracker.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

def main():
    user = current_user()
    if not user:
        login_widget()
        return

    st.sidebar.success(f"{user['username']} ({user['role']})")
    logout_button()

    page = st.sidebar.radio("Navigation", ["Big tableau", "Admin"])
    if page == "Big tableau":
        big_excel_tracker(user)
    elif page == "Admin":
        admin_page(user)

if __name__ == "__main__":
    main()
