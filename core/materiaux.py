from core.calculs import volume_beton_total

def besoins_materiaux(troncons, composition, materiaux_par_id):
    v_total = sum((volume_beton_total(t) or 0.0) for t in troncons)
    if not composition:
        return {
            "compo_validee": False,
            "manquants": ["composition absente"],
            "besoins": {},
            "volume_beton": v_total,
        }
    besoins = {}
    manquants = []
    for c in composition:
        m = materiaux_par_id.get(c.materiau_id)
        if m is None:
            continue
        qte = (c.quantite_par_m3 or 0.0) * v_total
        besoins[m.id] = {
            "designation": m.designation,
            "unite": m.unite,
            "quantite": qte,
            "prix_unitaire": m.prix_unitaire,
            "cout": qte * m.prix_unitaire,
        }
        if not c.reference_validation:
            manquants.append(f"{m.designation} (sans référence)")
    return {
        "compo_validee": len(manquants) == 0,
        "manquants": manquants,
        "besoins": besoins,
        "volume_beton": v_total,
    }