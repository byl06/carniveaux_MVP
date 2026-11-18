import io
import pandas as pd
from openpyxl import Workbook

def export_excel(chantier_nom, df_quantif, df_besoins, df_depenses):
    """Retourne un bytes d'un fichier Excel multi-feuilles."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_quantif.to_excel(writer, sheet_name="Quantification", index=True)
        df_besoins.to_excel(writer, sheet_name="Besoins matériaux", index=False)
        df_depenses.to_excel(writer, sheet_name="Dépenses", index=False)
    output.seek(0)
    return output.getvalue()