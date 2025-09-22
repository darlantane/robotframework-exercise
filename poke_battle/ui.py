# -*- coding: utf-8 -*-
from __future__ import annotations
import sys
from typing import List
from .types import Statut
from .data import POKEMON_DB, ATTAQUES_DB, Espece, Attaque
from .models import Pokemon
from .battle import Combat

PROMPT = "> "
GRAINE_DEMO = 1337
SCRIPT_DEMO = [
    ("Éclair", "Charge"),
    ("Vive-Attaque", "Fouet Lianes"),
    ("Éclair", "Mimi-Queue"),
]

def choisir_espece(prompt: str) -> str:
    noms = list(POKEMON_DB.keys())
    print(prompt)
    for i, n in enumerate(noms, 1):
        print(f" {i}. {n}")
    while True:
        s = input(PROMPT).strip()
        if s.isdigit() and 1 <= int(s) <= len(noms):
            return noms[int(s) - 1]
        if s in POKEMON_DB:
            return s
        print("Entrée invalide, réessayez.")

def attaques_defaut(nom_espece: str) -> List[str]:
    if nom_espece == "Pikachu":
        return ["Éclair", "Vive-Attaque", "Cage-Éclair", "Grognement"]
    if nom_espece == "Bulbizarre":
        return ["Fouet Lianes", "Charge", "Mimi-Queue", "Grognement"]
    if nom_espece == "Salamèche":
        return ["Flammèche", "Charge", "Mimi-Queue", "Grognement"]
    if nom_espece == "Carapuce":
        return ["Pistolet à O", "Charge", "Mimi-Queue", "Soin"]
    return ["Charge", "Mimi-Queue", "Grognement", "Vive-Attaque"]

def construire_pokemon(nom_espece: str) -> Pokemon:
    sp = POKEMON_DB[nom_espece]
    attaques = [ATTAQUES_DB[n] for n in attaques_defaut(nom_espece)]
    return Pokemon(sp, niveau=50, attaques=attaques)

def boucle_duel(combat: Combat):
    p1, p2 = combat.p1, combat.p2
    while not combat.vainqueur():
        print("\n== État actuel ==")
        print(f"{p1.nom}: {p1.pv}/{p1.pv_max} PV | Statut: {p1.statut.value}")
        print(f"{p2.nom}: {p2.pv}/{p2.pv_max} PV | Statut: {p2.statut.value}")
        print("\nChoisissez les capacités (par numéro):")
        for i, a in enumerate(p1.attaques, 1):
            print(f" P1 [{i}] {a.nom} (PP {a.pp})")
        for i, a in enumerate(p2.attaques, 1):
            print(f" P2 [{i}] {a.nom} (PP {a.pp})")
        try:
            i1 = int(input("P1 " + PROMPT)); i2 = int(input("P2 " + PROMPT))
            a1 = p1.attaques[i1 - 1]; a2 = p2.attaques[i2 - 1]
        except Exception:
            print("Entrée invalide, réessayez.")
            continue
        combat.faire_tour(a1, a2)
    print(f"\n>>> Vainqueur : {combat.vainqueur()} <<<")

def mode_demo():
    print("Mode Démonstration (déterministe)")
    p1 = construire_pokemon("Pikachu")
    p2 = construire_pokemon("Bulbizarre")
    c = Combat(p1, p2, graine=GRAINE_DEMO)
    for n1, n2 in SCRIPT_DEMO:
        if c.vainqueur():
            break
        a1 = p1.choisir_attaque_par_nom(n1)
        a2 = p2.choisir_attaque_par_nom(n2)
        c.faire_tour(a1, a2)
    print(f"\n>>> Vainqueur : {c.vainqueur()} <<<")
    c.ecrire_json("journal_combat.json")
    print("Journal écrit : journal_combat.json")

def main() -> int:
    print("=== Combat Pokémon – Console ===")
    print("1) Duel interactif")
    print("2) Mode Démonstration (stable pour tests)")
    print("3) Quitter")
    choix = input(PROMPT).strip()
    if choix == "1":
        s1 = choisir_espece("Choisissez le Pokémon 1 :")
        s2 = choisir_espece("Choisissez le Pokémon 2 :")
        c = Combat(construire_pokemon(s1), construire_pokemon(s2))
        boucle_duel(c)
        return 0
    elif choix == "2":
        mode_demo()
        return 0
    else:
        print("Au revoir.")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())