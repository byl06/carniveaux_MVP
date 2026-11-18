"""
Calculs de quantification pour un tronçon de caniveau en béton armé.
Toutes les dimensions sont en mètres. Les résultats sont en m³ ou m².
Aucune valeur n'est codée en dur : tout provient des dimensions saisies.
"""

def hauteur_paroi(troncon):
    """Hauteur de la paroi au-dessus du radier."""
    if troncon.hauteur is None or troncon.epaisseur_radier is None:
        return None
    return max(troncon.hauteur - troncon.epaisseur_radier, 0.0)

def volume_fouille(troncon):
    if None in (troncon.largeur_fouille, troncon.profondeur_fouille, troncon.longueur):
        return None
    return troncon.largeur_fouille * troncon.profondeur_fouille * troncon.longueur

def volume_radier(troncon):
    if None in (troncon.largeur, troncon.epaisseur_radier, troncon.longueur):
        return None
    return troncon.largeur * troncon.epaisseur_radier * troncon.longueur

def volume_parois(troncon):
    hp = hauteur_paroi(troncon)
    if None in (hp, troncon.epaisseur_paroi, troncon.longueur):
        return None
    return 2 * hp * troncon.epaisseur_paroi * troncon.longueur

def volume_beton_total(troncon):
    vr = volume_radier(troncon)
    vp = volume_parois(troncon)
    if vr is None or vp is None:
        return None
    return vr + vp

def surface_coffrage(troncon):
    """4 faces verticales (2 intérieures + 2 extérieures), abouts non comptés."""
    hp = hauteur_paroi(troncon)
    if None in (hp, troncon.longueur):
        return None
    return 4 * hp * troncon.longueur

def quantites_troncon(troncon):
    """Retourne un dict complet, avec None si données manquantes."""
    return {
        "reference": troncon.reference,
        "longueur": troncon.longueur,
        "volume_fouille": volume_fouille(troncon),
        "volume_radier": volume_radier(troncon),
        "volume_parois": volume_parois(troncon),
        "volume_beton_total": volume_beton_total(troncon),
        "surface_coffrage": surface_coffrage(troncon),
    }

def totaux_chantier(troncons):
    """Agrège les quantités sur une liste de tronçons."""
    totaux = {
        "longueur": 0.0,
        "volume_fouille": 0.0,
        "volume_radier": 0.0,
        "volume_parois": 0.0,
        "volume_beton_total": 0.0,
        "surface_coffrage": 0.0,
    }
    for t in troncons:
        q = quantites_troncon(t)
        for k in totaux:
            if k == "longueur":
                totaux[k] += t.longueur or 0.0
            elif q[k] is not None:
                totaux[k] += q[k]
    return totaux