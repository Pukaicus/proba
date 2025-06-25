import spacy

def extraire_education(texte_cv):
    nlp = spacy.load('fr_core_news_lg')

    # Charger mots-clés éducation
    with open('C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/education.txt', 'r', encoding='utf-8') as f:
        mots_cles_education = [mot.strip().lower() for mot in f.readlines() if mot.strip()]

    education = set()
    lignes = [l.strip() for l in texte_cv.split('\n') if l.strip()]

    for ligne in lignes:
        ligne_lower = ligne.lower()

        # Si la ligne contient au moins un mot-clé d'éducation
        if any(mot in ligne_lower for mot in mots_cles_education):
            if 10 < len(ligne) < 150:  # Évite les lignes trop courtes ou trop longues
                education.add(ligne.strip())

    return list(education)
