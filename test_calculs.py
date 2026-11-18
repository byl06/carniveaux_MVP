from core.calculs import (
    quantites_troncon, totaux_chantier, hauteur_paroi
)

class FakeTroncon:
    reference = "T1"
    longueur = 10.0
    largeur = 1.5
    hauteur = 1.5
    epaisseur_radier = 0.20
    epaisseur_paroi = 0.15
    largeur_fouille = 1.9
    profondeur_fouille = 1.8

t = FakeTroncon()
q = quantites_troncon(t)
print("Hauteur paroi :", hauteur_paroi(t))          # attendu 1.30
print("V fouille     :", q["volume_fouille"])       # attendu 1.9*1.8*10 = 34.2
print("V radier      :", q["volume_radier"])        # attendu 1.5*0.20*10 = 3.0
print("V parois      :", q["volume_parois"])        # attendu 2*1.30*0.15*10 = 3.9
print("V béton total :", q["volume_beton_total"])   # attendu 6.9
print("S coffrage    :", q["surface_coffrage"])     # attendu 4*1.30*10 = 52.0