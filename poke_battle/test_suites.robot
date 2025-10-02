*** Settings ***
# -*- coding: utf-8 -*-
Documentation     Suite de tests Robot Framework : projet Pokémon
Library           Process
Library           OperatingSystem
Library           JSONLibrary

*** Variables ***
${CMD}            python -m poke_battle
${TEMPDIR}    ${CURDIR}/temp
${PROMPT}         >
${JOURNAL}        journal_combat.json

*** Test Cases ***
Test 1 : Menu principal
    [Documentation]    Vérifier la présence des trois options et du prompt

    # Lance le processus du jeu en redirigeant la sortie standard et erreur dans des fichiers temporaires
    Start Process    ${CMD}    shell=True    stdout=${TEMPDIR}/stdout.txt    stderr=${TEMPDIR}/stderr.txt

    #Attend deux secondes pour laisser le temps au programme d'afficher le menu
    Sleep    2s

    # Récupère le contenu des fichiers stdout, stderr et concatène les deux sorties
    ${stdout}=    Get File    ${TEMPDIR}/stdout.txt
    ${stderr}=    Get File    ${TEMPDIR}/stderr.txt
    ${out}=    Set Variable    ${stdout}${stderr}

    # Vérifie les options affichées
    Should Contain    ${out}    === Combat Pokémon – Console ===
    Should Contain    ${out}    1) Duel interactif
    Should Contain    ${out}    2) Mode Démonstration (stable pour tests)
    Should Contain    ${out}    3) Quitter
    Should Contain    ${out}    ${PROMPT}

Test 2 : Mode Démonstration
    [Documentation]    Vérifie l'exécution du mode démonstration

    # Lance le processus du jeu en redirigeant la sortie standard et erreur dans des fichiers temporaires
    Start Process    ${CMD}    shell=True    stdout=${TEMPDIR}/stdout.txt    stderr=${TEMPDIR}/stderr.txt    stdin=PIPE

    #Attend deux secondes pour laisser le temps au programme d'afficher le menu
    Sleep    2s

    # Simule le choix de l'option "2" (Mode Démonstration) en l'envoyant à la commande
    ${result}=    Run Process    echo 2 | ${CMD}    shell=True

    # Récupère le contenu du fichier stdout
    ${stdout}=    Get File    ${TEMPDIR}/stdout.txt
    ${out}=    Set Variable    ${result.stdout}

    # Vérifie les options affichées
    Should Contain    ${out}    Tour 1
    Should Contain    ${out}    >>> Vainqueur

    # Vérifie que le fichier de journal_combat.json existe et n'est pas vide
    File Should Exist    ${JOURNAL}
    File Should Not Be Empty    ${JOURNAL}

    # Charge le contenu du fichier (au format JSON)
    ${json_content}=    Get File    ${JOURNAL}
    ${json_data}=    Evaluate    json.loads('''${json_content}''')    json

    # Vérifie que les joueurs 1 et 2 sont bien Pikachu et Bulbizarre
    Should Be Equal As Strings    ${json_data[0]["p1"]["nom"]}    Pikachu
    Should Be Equal As Strings    ${json_data[0]["p2"]["nom"]}    Bulbizarre

Test 3 : Duel Interactif
    [Documentation]  Vérifie le bon déroulement d'un duel interactif (smoke test) en simulant une séquence d'entrées valides.

    # Définit une liste de choix simulés (actions du joueur pendant le duel)
    @{choices}=    Create List    1    1    2    1    1    1    1    1    1

    # Concatène les choix en une chaîne avec des retours à la ligne,
    # puis ajoute un retour final pour bien "valider" la saisie simulée
    ${inputs}=     Evaluate    '\\n'.join(${choices}) + '\\n'

    # Exécute le programme avec les entrées simulées et redirige les sorties dans des fichiers
    Run Process    ${CMD}    shell=True    stdin=${inputs}    stdout=${TEMPDIR}/stdout.txt    stderr=${TEMPDIR}/stderr.txt

    # Récupère le contenu des fichiers stdout, stderr et concatène les deux sorties
    ${stdout}=    Get File    ${TEMPDIR}/stdout.txt
    ${stderr}=    Get File    ${TEMPDIR}/stderr.txt
    ${out}=       Set Variable    ${stdout}${stderr}

    # Vérifie les options affichées
    Should Contain    ${out}    == État actuel ==
    Should Contain    ${out}    Pikachu
    Should Contain    ${out}    Bulbizarre
    Should Contain    ${out}    PP
    Should Contain    ${out}    inflige
    Should Contain    ${out}    PV
    Should Contain    ${out}    ${PROMPT}

Test 4 : Gestion des entrées invalides
    [Documentation]  Vérifie que le programme gère correctement les entrées invalides et affiche un message d'erreur approprié.

    # Démarre le processus du jeu en redirigeant stdout et stderr dans des fichiers temporaires
    # et en laissant stdin ouvert pour pouvoir envoyer des choix
    Start Process    ${CMD}    shell=True    stdout=${TEMPDIR}/stdout.txt    stderr=${TEMPDIR}/stderr.txt    stdin=PIPE    alias=jeu
    Sleep    2s

    # Prépare une liste de choix incluant une valeur invalide ("99")
    @{choices}=    Create List    1    1    99    1    1    1    1    1

    # Transforme la liste en une chaîne avec des retours à la ligne
    # Ajoute un retour final pour bien simuler la saisie utilisateur
    ${inputs}=     Evaluate    '\\n'.join(${choices}) + '\\n'

    # Exécute le programme avec les entrées simulées, et redirige les sorties
    ${result}=    Run Process    ${CMD}    shell=True    stdin=${inputs}    stdout=${TEMPDIR}/stdout.txt    stderr=${TEMPDIR}/stderr.txt

    # Récupère le contenu des fichiers stdout, stderr et concatène les deux sorties
    ${stdout}=    Get File    ${TEMPDIR}/stdout.txt
    ${stderr}=    Get File    ${TEMPDIR}/stderr.txt
    ${out}=    Set Variable    ${stdout}${stderr}

    # Vérifie les options
    Should Contain    ${out}    Entrée invalide, réessayez.
    Should Contain    ${out}    ${PROMPT}