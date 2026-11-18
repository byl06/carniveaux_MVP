import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def export_pdf(chantier_nom, localisation, quantites_totaux, besoins_rows,
               depenses_rows, budget_total, depenses_total, avancement_pct):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=30, rightMargin=30,
                            topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    title = ParagraphStyle("title", parent=styles["Heading1"], fontSize=16, spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=6)
    story.append(Paragraph(f"Rapport chantier — {chantier_nom}", title))
    story.append(Paragraph(f"Localisation : {localisation or '—'}", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Quantités globales", h2))
    data = [["Indicateur", "Valeur"]]
    for k, v in quantites_totaux.items():
        data.append([k, f"{v:.2f}"])
    t = Table(data, colWidths=[250, 150])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Besoins en matériaux", h2))
    data = [["Matériau", "Unité", "Quantité", "Coût (FCFA)"]]
    for r in besoins_rows:
        data.append([r["designation"], r["unite"], f"{r['quantite']:.2f}", f"{r['cout']:.0f}"])
    t = Table(data, colWidths=[140, 60, 90, 110])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Synthèse financière", h2))
    data = [
        ["Budget prévisionnel", f"{budget_total:.0f} FCFA"],
        ["Dépenses réelles", f"{depenses_total:.0f} FCFA"],
        ["Écart", f"{budget_total - depenses_total:.0f} FCFA"],
        ["Avancement global", f"{avancement_pct:.1f} %"],
    ]
    t = Table(data, colWidths=[250, 150])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(t)

    story.append(Paragraph("Dépenses", h2))
    data = [["Date", "Catégorie", "Montant", "Description"]]
    for d in depenses_rows:
        data.append([d["date"], d["categorie"], f"{d['montant']:.0f}", d["description"][:40]])
    if len(data) == 1:
        data.append(["—", "—", "—", "Aucune dépense"])
    t = Table(data, colWidths=[80, 90, 90, 160])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Données incertaines signalées : vérifier la composition béton et les prix unitaires "
        "avant exploitation. Le prototype ne remplace pas la validation d'un professionnel.",
        ParagraphStyle("warn", parent=styles["Italic"], fontSize=8, textColor=colors.red)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()