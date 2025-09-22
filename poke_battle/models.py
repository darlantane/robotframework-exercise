# -*- coding: utf-8 -*-
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .types import Categorie, Statut, Type, STAGE_TABLE, ACC_EVA_TABLE
from .data import Espece, Attaque

@dataclass
class Pokemon:
    espece: Espece
    niveau: int = 50
    attaques: List[Attaque] = field(default_factory=list)
    nom: Optional[str] = None

    # État dynamique
    pv_max: int = field(init=False)
    pv: int = field(init=False)
    statut: Statut = Statut.AUCUN
    tours_sommeil: int = 0

    # Stats calculées + étages
    atq: int = field(init=False)
    defe: int = field(init=False)
    asp: int = field(init=False) # Attaque Spéciale
    dsp: int = field(init=False) # Défense Spéciale
    vit: int = field(init=False)
    niveaux: Dict[str, int] = field(default_factory=lambda: {
    "atq":0, "def":0, "asp":0, "dsp":0, "vit":0, "prec":0, "esq":0
    })

    def __post_init__(self):
        self.nom = self.nom or self.espece.nom
        # Formules simplifiées (EV/IV neutres)
        self.pv_max = math.floor(((2 * self.espece.base_pv) * self.niveau) /
        100) + self.niveau + 10
        self.atq = math.floor(((2 * self.espece.base_atq) * self.niveau) /
        100) + 5
        self.defe = math.floor(((2 * self.espece.base_def) * self.niveau) /
        100) + 5
        self.asp = math.floor(((2 * self.espece.base_as) * self.niveau) /
        100) + 5
        self.dsp = math.floor(((2 * self.espece.base_ds) * self.niveau) /
        100) + 5
        self.vit = math.floor(((2 * self.espece.base_vit) * self.niveau) /
        100) + 5
        self.pv = self.pv_max
        # Cloner les attaques pour des PP indépendants
        self.attaques = [Attaque(a.nom, a.type, a.categorie, a.puissance,
        a.precision, a.pp, a.priorite, a.effet) for a in self.attaques]

    @property
    def types(self) -> Tuple[Type, Optional[Type]]:
        return (self.espece.type1, self.espece.type2)

    def multiplicateur_niveau(self, cle: str) -> float:
        niveau = max(-6, min(6, self.niveaux[cle]))
        table = ACC_EVA_TABLE if cle in ("prec", "esq") else STAGE_TABLE
        return float(table[niveau])

    def stat_effective(self, cle: str) -> int:
        base = {"atq": self.atq, "def": self.defe, "asp": self.asp, "dsp": self.dsp, "vit": self.vit}[cle]
        mult = self.multiplicateur_niveau(cle)
        if cle == "atq" and self.statut == Statut.BRULURE:
            mult *= 0.5
        return max(1, int(base * mult))

    def modif_niveau(self, cle: str, delta: int):
        if cle not in self.niveaux:
            return
        self.niveaux[cle] = max(-6, min(6, self.niveaux[cle] + delta))

    def set_statut(self, s: Statut):
        # Immunités simples
        if s == Statut.PARALYSIE and (Type.ELECTRIQUE in self.types):
            return
        if s == Statut.POISON and (Type.POISON in self.types or Type.ACIER in self.types):
            return
        if self.statut is Statut.AUCUN:
            self.statut = s
            if s == Statut.PARALYSIE:
                self.modif_niveau("vit", -2)

    def set_tours_sommeil(self, n: int):
        if self.statut is Statut.AUCUN:
            self.statut = Statut.SOMMEIL
            self.tours_sommeil = n

    def est_ko(self) -> bool:
        return self.pv <= 0

    def choisir_attaque_par_nom(self, nom: str) -> Optional[Attaque]:
        for a in self.attaques:
            if a.nom.lower() == nom.lower():
                return a
        return None