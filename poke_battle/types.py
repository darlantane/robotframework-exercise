# -*- coding: utf-8 -*-
from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Tuple

class Categorie(Enum):
    PHYSIQUE = "physique"
    SPECIALE = "speciale"
    STATUT = "statut"

class Statut(Enum):
    AUCUN = "aucun"
    BRULURE = "brulure"
    POISON = "poison"
    PARALYSIE = "paralysie"
    SOMMEIL = "sommeil"

class Type(Enum):
    NORMAL = "Normal"
    FEU = "Feu"
    EAU = "Eau"
    PLANTE = "Plante"
    ELECTRIQUE = "Électrik"
    GLACE = "Glace"
    COMBAT = "Combat"
    POISON = "Poison"
    SOL = "Sol"
    VOL = "Vol"
    PSY = "Psy"
    INSECTE = "Insecte"
    ROCHE = "Roche"
    SPECTRE = "Spectre"
    DRAGON = "Dragon"
    TENEBRES = "Ténèbres"
    ACIER = "Acier"
    FEE = "Fée"

# Étages de stats : multiplicateurs (-6..+6)

STAGE_TABLE = {
    -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
    0: 1.0,
    1: 3/2, 2: 4/2, 3: 5/2, 4: 6/2, 5: 7/2, 6: 8/2,
}

# Précision/Esquive (on réutilise la même table pour simplifier)
ACC_EVA_TABLE = STAGE_TABLE

# Table d’efficacité des types (simplifiée mais cohérente)
def multiplicateur_type(type_attaque: Type, types_defenseur: Tuple[Type,
Optional[Type]]):
    chart: Dict[Tuple[Type, Type], float] = {
        # Feu/Eau/Plante/Électrik
        (Type.FEU, Type.PLANTE): 2.0,
        (Type.FEU, Type.EAU): 0.5,
        (Type.FEU, Type.ROCHE): 0.5,
        (Type.FEU, Type.GLACE): 2.0,
        (Type.EAU, Type.FEU): 2.0,
        (Type.EAU, Type.PLANTE): 0.5,
        (Type.PLANTE, Type.EAU): 2.0,
        (Type.PLANTE, Type.FEU): 0.5,
        (Type.PLANTE, Type.PLANTE): 0.5,
        (Type.ELECTRIQUE, Type.EAU): 2.0,
        (Type.ELECTRIQUE, Type.VOL): 2.0,
        (Type.ELECTRIQUE, Type.SOL): 0.0,

        # Normal/Combat/Roche/Spectre basiques
        (Type.NORMAL, Type.ROCHE): 0.5,
        (Type.NORMAL, Type.SPECTRE): 0.0,
        (Type.COMBAT, Type.NORMAL): 2.0,
        (Type.COMBAT, Type.ROCHE): 2.0,
        (Type.ROCHE, Type.VOL): 2.0,
        (Type.SPECTRE, Type.SPECTRE): 2.0,
        (Type.SPECTRE, Type.NORMAL): 0.0,
    }
    mult = 1.0
    for dt in types_defenseur:
        if dt is None:
            continue
        mult *= chart.get((type_attaque, dt), 1.0)
    return mult