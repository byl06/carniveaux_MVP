import streamlit as st
import pandas as pd
from datetime import datetime

from db.connection import test_connection, init_db, get_session
from db.models import (
    Chantier, Troncon, Materiau, CompositionBeton, Depense, Avancement
)
from core.calculs import quantites_troncon, totaux_chantier
from core.materiaux import besoins_materiaux
from core.avancement import ETAPES, STATUTS, avancement_troncon, avancement_chantier
from exports.pdf_export import export_pdf
from exports.excel_export import export_excel

st.set_page_config(page_title="Caniveaux MVP", layout="wide")
st.title("Caniveaux en béton armé — MVP")

if "db_initialized" not in st.session_state:
    try:
        init_db()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Erreur init DB : {e}")
        st.stop()

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Aller à",
    ["Tableau de bord", "Chantiers", "Détail chantier", "Quantification",
     "Matériaux", "Composition béton", "Dépenses", "Avancement", "Exports", "Test DB"],
)

if page == "Test DB":
    if st.button("Tester la connexion"):
        ok, msg = test_connection()
        st.success(msg) if ok else st.error(msg)
    st.stop()

session = get_session()


def select_chantier(key):
    chantiers = session.query(Chantier).order_by(Chantier.nom).all()
    if not chantiers:
        st.info("Aucun chantier.")
        session.close()
        st.stop()
    options = {f"{c.nom} (id={c.id})": c.id for c in chantiers}
    choix = st.selectbox("Chantier", list(options.keys()), key=key)
    return options[choix]


def donnees_chantier(cid):
    chantier = session.get(Chantier, cid)
    troncons = session.query(Troncon).filter_by(chantier_id=cid).order_by(Troncon.id).all()
    comps = session.query(CompositionBeton).filter_by(chantier_id=cid).all()
    mats = session.query(Materiau).all()
    mats_by_id = {m.id: m for m in mats}
    besoins = besoins_materiaux(troncons, comps, mats_by_id)
    budget_total = sum(b["cout"] for b in besoins["besoins"].values())
    depenses = session.query(Depense).filter_by(chantier_id=cid).order_by(Depense.date.desc()).all()
    depenses_total = sum(d.montant for d in depenses)
    avancements_par_troncon = {}
    for t in troncons:
        avancements_par_troncon[t.id] = session.query(Avancement).filter_by(troncon_id=t.id).all()
    avanc_pct = avancement_chantier(troncons, avancements_par_troncon)
    return {
        "chantier": chantier, "troncons": troncons, "comps": comps, "mats_by_id": mats_by_id,
        "besoins": besoins, "budget_total": budget_total,
        "depenses": depenses, "depenses_total": depenses_total,
        "avancements_par_troncon": avancements_par_troncon, "avancement_pct": avanc_pct,
    }


# ========== Tableau de bord ==========
if page == "Tableau de bord":
    cid = select_chantier("dash")
    d = donnees_chantier(cid)
    tot = totaux_chantier(d["troncons"])
    ch = d["chantier"]
    st.header(f"📊 Tableau de bord — {ch.nom}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Longueur totale (m)", f"{tot['longueur']:.2f}")
    c2.metric("Tronçons", len(d["troncons"]))
    c3.metric("Volume béton (m³)", f"{tot['volume_beton_total']:.2f}")
    c4.metric("Avancement", f"{d['avancement_pct']:.1f} %")
    c1.metric("Budget prévisionnel", f"{d['budget_total']:.0f} FCFA")
    c2.metric("Dépenses", f"{d['depenses_total']:.0f} FCFA")
    c3.metric("Écart", f"{d['budget_total'] - d['depenses_total']:.0f} FCFA")
    if not d["besoins"]["compo_validee"]:
        st.warning("⚠️ Composition béton non validée : " + ", ".join(d["besoins"]["manquants"]))

# ========== Chantiers ==========
elif page == "Chantiers":
    st.header("Chantiers")
    with st.expander("➕ Créer un nouveau chantier", expanded=False):
        with st.form("form_chantier"):
            nom = st.text_input("Nom du chantier *")
            localisation = st.text_input("Localisation")
            description = st.text_area("Description")
            if st.form_submit_button("Créer"):
                if not nom.strip():
                    st.error("Le nom est obligatoire.")
                else:
                    c = Chantier(nom=nom.strip(), localisation=localisation.strip(), description=description.strip())
                    session.add(c); session.commit(); st.rerun()
    chantiers = session.query(Chantier).order_by(Chantier.id.desc()).all()
    for c in chantiers:
        with st.expander(f"🏗️ {c.nom} — {c.localisation or '—'} (id={c.id})"):
            st.write(f"**Description :** {c.description or '—'}")
            if st.button(f"🗑️ Supprimer {c.id}", key=f"del_{c.id}"):
                session.delete(c); session.commit(); st.rerun()

# ========== Détail chantier ==========
elif page == "Détail chantier":
    cid = select_chantier("detail")
    chantier = session.get(Chantier, cid)
    st.header(f"🏗️ {chantier.nom}")
    with st.form("form_troncon"):
        c1, c2 = st.columns(2)
        with c1:
            reference = st.text_input("Référence *")
            longueur = st.number_input("Longueur (m) *", min_value=0.0, step=0.1, format="%.2f")
            largeur = st.number_input("Largeur (m)", min_value=0.0, step=0.05, format="%.2f")
            hauteur = st.number_input("Hauteur (m)", min_value=0.0, step=0.05, format="%.2f")
            ep_radier = st.number_input("Ép. radier (m)", min_value=0.0, step=0.01, format="%.3f")
        with c2:
            ep_paroi = st.number_input("Ép. paroi (m)", min_value=0.0, step=0.01, format="%.3f")
            larg_f = st.number_input("Larg. fouille (m)", min_value=0.0, step=0.05, format="%.2f")
            prof_f = st.number_input("Prof. fouille (m)", min_value=0.0, step=0.05, format="%.2f")
        if st.form_submit_button("Ajouter tronçon"):
            if not reference.strip() or longueur <= 0:
                st.error("Référence et longueur obligatoires.")
            else:
                session.add(Troncon(
                    chantier_id=cid, reference=reference.strip(), longueur=longueur,
                    largeur=largeur or None, hauteur=hauteur or None,
                    epaisseur_radier=ep_radier or None, epaisseur_paroi=ep_paroi or None,
                    largeur_fouille=larg_f or None, profondeur_fouille=prof_f or None,
                ))
                session.commit(); st.rerun()
    troncons = session.query(Troncon).filter_by(chantier_id=cid).order_by(Troncon.id).all()
    for t in troncons:
        with st.expander(f"🔹 {t.reference} — {t.longueur} m"):
            st.write(f"L={t.largeur} H={t.hauteur} radier={t.epaisseur_radier} paroi={t.epaisseur_paroi}")
            if st.button(f"🗑️ Supprimer {t.id}", key=f"delt_{t.id}"):
                session.delete(t); session.commit(); st.rerun()

# ========== Quantification ==========
elif page == "Quantification":
    cid = select_chantier("q")
    d = donnees_chantier(cid)
    st.header(f"Quantification — {d['chantier'].nom}")
    if not d["troncons"]:
        st.info("Aucun tronçon.")
    else:
        rows = [quantites_troncon(t) for t in d["troncons"]]
        st.dataframe(pd.DataFrame(rows).set_index("reference"), use_container_width=True)
        tot = totaux_chantier(d["troncons"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Fouille (m³)", f"{tot['volume_fouille']:.2f}")
        c2.metric("Béton (m³)", f"{tot['volume_beton_total']:.2f}")
        c3.metric("Coffrage (m²)", f"{tot['surface_coffrage']:.2f}")

# ========== Matériaux ==========
elif page == "Matériaux":
    st.header("Matériaux")
    with st.form("form_materiau"):
        c1, c2, c3 = st.columns(3)
        with c1: designation = st.text_input("Désignation *")
        with c2: unite = st.selectbox("Unité", ["kg", "m³", "L", "barre", "unité", "sac"])
        with c3: prix = st.number_input("Prix unitaire (FCFA)", min_value=0.0, step=100.0)
        if st.form_submit_button("Ajouter"):
            if designation.strip():
                session.add(Materiau(designation=designation.strip(), unite=unite, prix_unitaire=prix))
                session.commit(); st.rerun()
    for m in session.query(Materiau).order_by(Materiau.designation).all():
        with st.expander(f"📦 {m.designation} — {m.prix_unitaire:.0f} FCFA/{m.unite}"):
            if st.button(f"🗑️ Supprimer {m.id}", key=f"delm_{m.id}"):
                session.delete(m); session.commit(); st.rerun()

# ========== Composition béton ==========
elif page == "Composition béton":
    st.header("Composition béton (pour 1 m³)")
    st.caption("Valeurs validées par laboratoire ou responsable technique uniquement.")
    cid = select_chantier("comp")
    mats = session.query(Materiau).all()
    if not mats:
        st.warning("Crée d'abord des matériaux.")
        session.close(); st.stop()
    with st.form("form_compo"):
        mat_choices = {f"{m.designation} ({m.unite})": m.id for m in mats}
        mat_sel = st.selectbox("Matériau", list(mat_choices.keys()))
        qte = st.number_input("Quantité / m³ *", min_value=0.0, step=1.0)
        ref = st.text_input("Référence validation")
        if st.form_submit_button("Ajouter / mettre à jour"):
            mid = mat_choices[mat_sel]
            ex = session.query(CompositionBeton).filter_by(chantier_id=cid, materiau_id=mid).first()
            if ex:
                ex.quantite_par_m3 = qte; ex.reference_validation = ref
            else:
                session.add(CompositionBeton(chantier_id=cid, materiau_id=mid,
                                             quantite_par_m3=qte, reference_validation=ref))
            session.commit(); st.rerun()
    comps = session.query(CompositionBeton).filter_by(chantier_id=cid).all()
    if comps:
        rows = []
        for cb in comps:
            m = session.get(Materiau, cb.materiau_id)
            rows.append({"matériau": m.designation, "unité": m.unite,
                         "q/m³": cb.quantite_par_m3,
                         "validation": cb.reference_validation or "⚠️ non validé"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ========== Dépenses ==========
elif page == "Dépenses":
    st.header("Dépenses réelles")
    cid = select_chantier("dep")
    with st.form("form_dep"):
        c1, c2 = st.columns(2)
        with c1:
            cat = st.selectbox("Catégorie", ["matériaux", "main-d'œuvre", "transport", "matériel"])
            montant = st.number_input("Montant (FCFA) *", min_value=0.0, step=1000.0)
        with c2:
            date = st.date_input("Date", value=datetime.now().date())
            desc = st.text_input("Description")
        if st.form_submit_button("Enregistrer"):
            if montant <= 0:
                st.error("Montant obligatoire.")
            else:
                session.add(Depense(chantier_id=cid, categorie=cat,
                                    date=datetime.combine(date, datetime.min.time()),
                                    montant=montant, description=desc))
                session.commit(); st.rerun()
    deps = session.query(Depense).filter_by(chantier_id=cid).order_by(Depense.date.desc()).all()
    if deps:
        df = pd.DataFrame([{"date": d.date.strftime("%Y-%m-%d"), "catégorie": d.categorie,
                            "montant": d.montant, "description": d.description or ""} for d in deps])
        st.dataframe(df, use_container_width=True)
        st.metric("Total dépenses", f"{sum(d.montant for d in deps):.0f} FCFA")
    else:
        st.info("Aucune dépense.")

# ========== Avancement ==========
elif page == "Avancement":
    st.header("Suivi de l'avancement")
    cid = select_chantier("av")
    troncons = session.query(Troncon).filter_by(chantier_id=cid).order_by(Troncon.id).all()
    if not troncons:
        st.info("Aucun tronçon.")
    for t in troncons:
        st.subheader(f"🔹 {t.reference}")
        existants = {a.etape: a for a in session.query(Avancement).filter_by(troncon_id=t.id).all()}
        for etape in ETAPES:
            ex = existants.get(etape)
            col1, col2, col3 = st.columns([2, 2, 3])
            with col1:
                statut = st.selectbox(f"Statut {etape}", STATUTS,
                    index=STATUTS.index(ex.statut) if ex else 0,
                    key=f"st_{t.id}_{etape}")
            with col2:
                obs = st.text_input(f"Observation {etape}",
                    value=ex.observation if ex else "", key=f"ob_{t.id}_{etape}")
            with col3:
                if st.button(f"💾 Enregistrer {etape}", key=f"sv_{t.id}_{etape}"):
                    if ex:
                        ex.statut = statut; ex.observation = obs; ex.date = datetime.utcnow()
                    else:
                        session.add(Avancement(troncon_id=t.id, etape=etape,
                                               statut=statut, observation=obs))
                    session.commit(); st.rerun()
        av = avancement_troncon(list(existants.values()))
        st.progress(av / 100.0, text=f"Avancement : {av:.1f} %")

# ========== Exports ==========
elif page == "Exports":
    st.header("Exports PDF & Excel")
    cid = select_chantier("exp")
    d = donnees_chantier(cid)
    if not d["troncons"]:
        st.info("Aucun tronçon.")
    else:
        tot = totaux_chantier(d["troncons"])
        df_quantif = pd.DataFrame([quantites_troncon(t) for t in d["troncons"]]).set_index("reference")
        besoins_rows = list(d["besoins"]["besoins"].values())
        df_besoins = pd.DataFrame(besoins_rows) if besoins_rows else pd.DataFrame([{"info": "aucune composition"}])
        df_depenses = pd.DataFrame([{"date": dep.date.strftime("%Y-%m-%d"), "catégorie": dep.categorie,
                                     "montant": dep.montant, "description": dep.description or ""}
                                    for dep in d["depenses"]]) if d["depenses"] else pd.DataFrame([{"info": "aucune dépense"}])
        st.subheader("Excel")
        xls = export_excel(d["chantier"].nom, df_quantif, df_besoins, df_depenses)
        st.download_button("⬇️ Télécharger Excel", xls,
                           file_name=f"{d['chantier'].nom}_export.xlsx")
        st.subheader("PDF")
        pdf = export_pdf(d["chantier"].nom, d["chantier"].localisation,
                         {"Fouille (m³)": tot["volume_fouille"],
                          "Béton (m³)": tot["volume_beton_total"],
                          "Coffrage (m²)": tot["surface_coffrage"],
                          "Longueur (m)": tot["longueur"]},
                         besoins_rows,
                         [{"date": dep.date.strftime("%Y-%m-%d"), "categorie": dep.categorie,
                           "montant": dep.montant, "description": dep.description or ""}
                          for dep in d["depenses"]],
                         d["budget_total"], d["depenses_total"], d["avancement_pct"])
        st.download_button("⬇️ Télécharger PDF", pdf,
                           file_name=f"{d['chantier'].nom}_rapport.pdf")

session.close()