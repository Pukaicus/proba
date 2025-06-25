import re
import spacy

def extraire_experiences(texte_cv):
    nlp = spacy.load("fr_core_news_lg")
    doc = nlp(texte_cv)

    lignes = [ligne.strip() for ligne in texte_cv.splitlines() if ligne.strip()]
    experiences = set()

    # Mots-clés typiques de section d'expériences
    mots_cles = [
        "expérience professionnelle", "expériences professionnelles", 
        "expérience", "professionnelle", "emploi", "travail", "stage", "poste", "CDD", "CDI", "alternance"
    ]

    # Liste de métiers fréquents pour aider à détecter les expériences
    metiers_frequents = [
        "développeur", "ingénieur", "technicien", "analyste", "chef de projet",
        "formateur", "enseignant", "commercial", "consultant", "assistant",
        "facteur", "conseiller", "vendeur", "stagiaire", "freelance", "professeur"
    ]

    for i, ligne in enumerate(lignes):
        ligne_lower = ligne.lower()
        if any(mot in ligne_lower for mot in mots_cles) or any(metier in ligne_lower for metier in metiers_frequents):
            if len(ligne.split()) > 2 or re.search(r"\d{4}", ligne):  # contient assez d'info ou une date
                experiences.add(ligne)

            # Bonus : inclure une ligne suivante s'il y a une continuation
            if i + 1 < len(lignes) and len(lignes[i+1].split()) > 1:
                experiences.add(lignes[i+1])

    return list(experiences)
