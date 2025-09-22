# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Callable
from .types import Type, Categorie, Statut
@dataclass
class Espece:
    nom: str
    type1: Type
    type2: Optional[Type]
    base_pv: int
    base_atq: int
    base_def: int
    base_as: int # Attaque Spéciale
    base_ds: int # Défense Spéciale
    base_vit: int

POKEMON_DB: Dict[str, Espece] = {
    "Pikachu": Espece("Pikachu", Type.ELECTRIQUE, None, 35,55,
40,50,50,90),
    "Bulbizarre":Espece("Bulbizarre", Type.PLANTE, Type.POISON, 45,49,
49,65,65,45),
    "Salamèche": Espece("Salamèche", Type.FEU, None, 39,52,
43,60,50,65),
    "Carapuce": Espece("Carapuce", Type.EAU, None, 44,48,
65,50,64,43),
}

@dataclass
class Attaque:
    nom: str
    type: Type
    categorie: Categorie
    puissance: int = 0
    precision: int = 100
    pp: int = 10
    priorite: int = 0
    effet: Optional[Callable] = None # signature: (combat, lanceur, cible) -> None

# Effets simples

def effet_grognement(combat, lanceur, cible):
    cible.modif_niveau("atq", -1)
    combat.log(f"{lanceur.nom} utilise Grognement ! L’Attaque de {cible.nom} baisse.")

def effet_mimi_queue(combat, lanceur, cible):
    cible.modif_niveau("def", -1)
    combat.log(f"{lanceur.nom} utilise Mimi-Queue ! La Défense de {cible.nom} baisse.")

def effet_soin(combat, lanceur, cible):
    gueris = min(lanceur.pv_max//2, lanceur.pv_max - lanceur.pv)
    lanceur.pv += gueris
    combat.log(f"{lanceur.nom} récupère {gueris} PV avec Soin.")

def effet_cage_eclair(combat, lanceur, cible):
    if cible.statut is Statut.AUCUN:
    # Immunité simple : type Électrik ne peut pas être paralysé par Cage‑Éclair
        if Type.ELECTRIQUE in cible.types:
            combat.log("Mais cela n’a aucun effet…")
            return
        cible.set_statut(Statut.PARALYSIE)
        combat.log(f"{cible.nom} est paralysé !")
    else:
        combat.log("Mais cela n’a aucun effet…")

ATTAQUES_DB: Dict[str, Attaque] = {
    # Physiques
    "Charge": Attaque("Charge", Type.NORMAL,
Categorie.PHYSIQUE, puissance=40, precision=100, pp=35),
    "Vive-Attaque": Attaque("Vive-Attaque", Type.NORMAL,
Categorie.PHYSIQUE, puissance=40, precision=100, pp=30, priorite=1),
    "Fouet Lianes": Attaque("Fouet Lianes", Type.PLANTE,
Categorie.PHYSIQUE, puissance=45, precision=100, pp=25),
    # Spéciales
    "Éclair": Attaque("Éclair", Type.ELECTRIQUE,
Categorie.SPECIALE, puissance=90, precision=100, pp=15),
    "Flammèche": Attaque("Flammèche", Type.FEU,
Categorie.SPECIALE, puissance=40, precision=100, pp=25),
    "Pistolet à O": Attaque("Pistolet à O", Type.EAU,
Categorie.SPECIALE, puissance=40, precision=100, pp=25),
    # Statut
    "Grognement": Attaque("Grognement", Type.NORMAL,
Categorie.STATUT, pp=40, effet=effet_grognement),
    "Mimi-Queue": Attaque("Mimi-Queue", Type.NORMAL,
Categorie.STATUT, pp=30, effet=effet_mimi_queue),
    "Soin": Attaque("Soin", Type.NORMAL,
Categorie.STATUT, pp=10, effet=effet_soin),
    "Cage-Éclair": Attaque("Cage-Éclair", Type.ELECTRIQUE,
Categorie.STATUT, precision=90, pp=20, effet=effet_cage_eclair),
}