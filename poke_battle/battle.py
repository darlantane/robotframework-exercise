# -*- coding: utf-8 -*-
from __future__ import annotations
import json, math, random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import self

from .types import Categorie, Statut, multiplicateur_type
from .models import Pokemon
from .data import Attaque

@dataclass
class Action:
    acteur: Pokemon
    attaque : Attaque

class Combat:
    def __init__(self, p1: Pokemon, p2: Pokemon, graine: Optional[int] = None):
        self.p1 = p1
        self.p2 = p2
        self.tour = 1
        self.rng = random.Random(graine)
        self.logs: List[str] = []
        self.json_log: List[Dict] = []

    # Journalisation
    def log(self, msg: str):
        self.logs.append(msg)
        print(msg)

    def instantane(self) -> Dict:
        return {
            "tour": self.tour,
            "p1": {"nom": self.p1.nom, "pv": self.p1.pv, "pv_max":
            self.p1.pv_max, "statut": self.p1.statut.value, "niveaux":
            self.p1.niveaux.copy()},
            "p2": {"nom": self.p2.nom, "pv": self.p2.pv, "pv_max":
            self.p2.pv_max, "statut": self.p2.statut.value, "niveaux":
            self.p2.niveaux.copy()},
        }

    # Exécuter un tour
    def faire_tour(self, att_p1, att_p2):
        self.log(f"\n— Tour {self.tour} —")
        for acteur, attaque in self.ordre_d_actions(att_p1, att_p2):
            if self.p1.est_ko() or self.p2.est_ko():
                break
            self.resoudre_action(acteur, attaque)
        # Fin de tour : dégâts résiduels de statut
        for mon in [self.p1, self.p2]:
            if mon.est_ko():
                continue
            if mon.statut == Statut.BRULURE:
                d = max(1, mon.pv_max // 16)
                mon.pv -= d
                self.log(f"{mon.nom} souffre de sa brûlure ({d} PV).")
            elif mon.statut == Statut.POISON:
                d = max(1, mon.pv_max // 8)
                mon.pv -= d
                self.log(f"{mon.nom} souffre du poison ({d} PV).")
            if mon.pv <= 0:
                mon.pv = 0
                self.log(f"{mon.nom} est K.O. !")

        # Sommeil : décrément
        for mon in [self.p1, self.p2]:
            if mon.statut == Statut.SOMMEIL and mon.tours_sommeil > 0:
                mon.tours_sommeil -= 1
                if mon.tours_sommeil == 0:
                    mon.statut = Statut.AUCUN
                    self.log(f"{mon.nom} se réveille !")
        self.json_log.append(self.instantane())
        self.tour += 1

    def ordre_d_actions(self, a1, a2):
        # Priorité > Vitesse
        if a1.priorite != a2.priorite:
            return [(self.p1, a1), (self.p2, a2)] if a1.priorite > a2.priorite else [(self.p2, a2), (self.p1, a1)]
        v1 = self.p1.stat_effective("vit")
        v2 = self.p2.stat_effective("vit")
        if v1 == v2:
            return [(self.p1, a1), (self.p2, a2)] if self.rng.random() < 0.5 else [(self.p2, a2), (self.p1, a1)]
        return [(self.p1, a1), (self.p2, a2)] if v1 > v2 else [(self.p2, a2), (self.p1, a1)]

    def resoudre_action(self, acteur: Pokemon, attaque):
        cible = self.p2 if acteur is self.p1 else self.p1
        if acteur.est_ko():
           return
        # Sommeil
        if acteur.statut == Statut.SOMMEIL:
            self.log(f"{acteur.nom} dort et ne peut pas bouger !")
            return
        # Paralysie : 25% rate
        if acteur.statut == Statut.PARALYSIE and self.rng.random() < 0.25:
            self.log(f"{acteur.nom} est paralysé ! Il ne peut pas attaquer.")
            return
        # PP
        if attaque.pp <= 0:
            self.log(f"{acteur.nom} n’a plus de PP pour {attaque.nom} !(action perdue)")
            return
        attaque.pp -= 1
        self.log(f"{acteur.nom} utilise {attaque.nom} !")
        # Précision / esquive
        if attaque.categorie != Categorie.STATUT and attaque.precision < 100:
            acc = attaque.precision * acteur.multiplicateur_niveau("prec") / cible.multiplicateur_niveau("esq")
            if self.rng.random() > (acc / 100.0):
                self.log("L’attaque échoue !")
            return
        # Résolution
        if attaque.categorie == Categorie.STATUT:
            if attaque.effet:
                attaque.effet(self, acteur, cible)
            return
        # Dégâts
        degats = self.calculer_degats(acteur, cible, attaque)
        cible.pv = max(0, cible.pv - degats)
        self.log(f"{attaque.nom} inflige {degats} dégâts à {cible.nom}.({cible.pv}/{cible.pv_max} PV)")
        if cible.est_ko():
            self.log(f"{cible.nom} est K.O. !")

    def calculer_degats(self, attaquant: Pokemon, defenseur: Pokemon, attaque):
        niv = attaquant.niveau
        if attaque.categorie == Categorie.PHYSIQUE:
            A = attaquant.stat_effective("atq"); D = defenseur.stat_effective("def")
        else:
            A = attaquant.stat_effective("asp"); D = defenseur.stat_effective("dsp")
        base = int(((2 * niv) / 5 + 2) * attaque.puissance * A / D / 50) + 2
        # Modificateurs
        stab = 1.5 if attaque.type in attaquant.types else 1.0
        mult_type = multiplicateur_type(attaque.type, defenseur.types)
        crit = 1.5 if self.rng.random() < 0.0625 else 1.0
        alea = self.rng.uniform(0.85, 1.0)
        total = base * stab * mult_type * crit * alea
        degats = max(1, int(total))
        # Logs d’efficacité
        if mult_type == 0:
            self.log("Ça n’affecte pas le Pokémon adverse…")
            return 0
        if crit > 1.0:
            self.log("Coup critique !")
        if mult_type > 1.0:
            self.log("C’est super efficace !")
        elif mult_type < 1.0:
            self.log("Ce n’est pas très efficace…")
        return degats

    def vainqueur(self) -> Optional[str]:
        if self.p1.est_ko() and not self.p2.est_ko():
            return self.p2.nom
        if self.p2.est_ko() and not self.p1.est_ko():
            return self.p1.nom
        if self.p1.est_ko() and self.p2.est_ko():
            return "Égalité"
        return None

    def ecrire_json(self, chemin: str):
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(self.json_log, f, ensure_ascii=False, indent=2)