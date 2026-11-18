ETAPES = ["ferraillage", "coffrage", "bétonnage"]
STATUTS = ["non commencé", "en cours", "terminé"]

def avancement_troncon(etapes_troncon):
    """etapes_troncon: list[Avancement] pour un tronçon.
    Retourne % (0-100) basé sur statuts."""
    if not etapes_troncon:
        return 0.0
    total = 0.0
    for e in etapes_troncon:
        if e.statut == "terminé":
            total += 1.0
        elif e.statut == "en cours":
            total += 0.5
    return 100.0 * total / len(ETAPES)

def avancement_chantier(troncons, avancements_par_troncon):
    """Moyenne des avancements des tronçons."""
    if not troncons:
        return 0.0
    total = 0.0
    for t in troncons:
        total += avancement_troncon(avancements_par_troncon.get(t.id, []))
    return total / len(troncons)