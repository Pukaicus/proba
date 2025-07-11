import re
import PyPDF2
from src.prenom_scorer import charger_prenoms_depuis_csv, get_prenom_score
from src.nom_scorer import charger_noms_depuis_csv, get_nom_score
import unicodedata

def normalize(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').upper()

def extraire_texte_pdf(chemin_pdf):
    texte = ""
    with open(chemin_pdf, "rb") as f:
        try:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                texte += page.extract_text() + "\n"
        except Exception as e:
            print("Erreur lecture PDF :", e)
    return texte

def clean_lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()] 

def extraire_email(texte):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", texte)
    return match.group() if match else None

def extraire_prenom_nom_depuis_email(email, prenoms_base, noms_base):
    if not email or '@' not in email:
        return None, None
    partie_locale = email.split('@')[0].lower()
    morceaux = re.split(r'[._\-]', partie_locale)
    
    prenom = None
    nom = None
    
    for mot in morceaux:
        if mot.capitalize() in prenoms_base:
            prenom = mot.capitalize()
            break
    
    for mot in morceaux:
        if mot.capitalize() in noms_base:
            if mot.capitalize() != prenom:
                nom = mot.capitalize()
                break
    
    return prenom, nom

def trouver_paires_prenom_nom_par_lignes(texte, prenoms_base, noms_base, bins_prenom, email=None, texte_complet=None):
    blacklist = {
        "LE", "LA", "DU", "DE", "DES", "LES", "ET", "AU", "AUX", "EN", "SUR", "PAR", "AVEC", "SANS", "SOI",
        "GRETA", "SIO", "POSTE", "BANQUE", "CLIENTS", "CONSEILLER", "FACTEUR", "COLIS", "JAVA", "PYTHON",
        "JEE", "PIX", "CISCO", "DURANT", "FORMATION", "MISSION", "GROUPE", "DIVERSES", "UNIVERSITÉ",
        "LYCÉE", "NANTES", "QUIMPER", "INFORMATIQUE", "CDA", "ECOLE", "INSTITUT", 
        "ORACLE", "COREL", "PHOTOSHOP", "SQL", "MACROMEDIA", "WINDOWS", "PARIS"
    }

    def ligne_valide(ligne):
        if len(ligne.strip()) < 3:
            return False
        if ligne.strip().isdigit():
            return False
        ligne_lower = ligne.lower()
        mots_cles_blacklist = ['formation', 'experience', 'compétences', 'adresse', 'téléphone', 'email', 'contact', 'certificat']
        if any(mot in ligne_lower for mot in mots_cles_blacklist) and "@" not in ligne:
            return False
        return True

    lignes = texte.splitlines()
    paires = []

    for i, ligne in enumerate(lignes):
        if not ligne_valide(ligne):
            continue

        mots = re.findall(r'\b(?:[A-Z][a-z\-]{2,}|[A-Z]{2,}|[A-Z][a-z]{1,2})\b', ligne)
        print("Mots extraits :", mots)
        mots = [m for m in mots if m.upper() not in blacklist]
        print("Mots après blacklist :", mots)


        prenoms_trouves = [m for m in mots if m.upper() in prenoms_base and m.upper() not in blacklist]

        if not prenoms_trouves and i > 0 and ligne_valide(lignes[i - 1]):
            mots_prec = re.findall(r'\b[a-zA-Z\-]{3,}\b', lignes[i - 1])
            mots_prec = [m for m in mots_prec if m.upper() not in blacklist]
            prenoms_trouves = [m for m in mots_prec if m.upper() in prenoms_base]

        mots_suivants = []
        if i + 1 < len(lignes) and ligne_valide(lignes[i + 1]):
            mots_suivants = re.findall(r'\b(?:[A-Z][a-z\-]{2,}|[A-Z]{2,}|[A-Z][a-z]{1,2})\b', lignes[i + 1])
            mots_suivants = [m for m in mots_suivants if m.upper() not in blacklist]

        mots_a_tester = mots + mots_suivants
        noms_possibles = [m for m in mots_a_tester if m.upper() in noms_base]

        for prenom in prenoms_trouves:
            if len(prenom) < 3:
                continue
            for nom in noms_possibles:
                if prenom == nom:
                    continue
                if nom.upper() in blacklist or prenom.upper() in blacklist:
                    continue
                if len(nom) < 3:
                    continue

                score_data = get_prenom_score(prenom, prenoms_base, bins_prenom, email=email, nom=nom, texte=texte_complet)
                if score_data["base_score"] == 0 and score_data["bonus"] == 0:
                   continue

                ligne_paire = i + 1
                texte_ligne = lignes[i].strip()
                paires.append((prenom, nom, ligne_paire, texte_ligne))

    return paires


def analyser_cv_pdf(chemin_pdf):
    texte = extraire_texte_pdf(chemin_pdf)
    if not texte.strip():
        print("Erreur : texte PDF vide ou illisible.")
        return

    rarity_prenoms, bins_prenom = charger_prenoms_depuis_csv("data/prenoms.csv")
    rarity_noms, bins_nom = charger_noms_depuis_csv("data/noms.csv")

    email = extraire_email(texte)

    paires_detectees = trouver_paires_prenom_nom_par_lignes(
        texte, rarity_prenoms, rarity_noms, bins_prenom, email=email, texte_complet=texte
    )

    if not paires_detectees:
        print("Aucune paire prénom + nom fiable détectée.")
        return

    scores_detailles = []

    for prenom, nom, ligne_num, ligne_texte in paires_detectees:
        score_prenom_data = get_prenom_score(
            prenom,
            rarity_prenoms,
            bins_prenom,
            email=email,
            texte=texte,
            nom=nom
        )
        score_nom = get_nom_score(
            nom,
            rarity_noms,
            bins_nom,
            email=email,
            texte=texte,
            prenom=prenom
        )
        score_total = min(8, score_prenom_data['final_score'] + score_nom)

        scores_detailles.append({
            "prenom": prenom,
            "nom": nom,
            "ligne": ligne_num,
            "texte_ligne": ligne_texte,
            "score_prenom": score_prenom_data,
            "score_nom": score_nom,
            "score_total": score_total
        })

    print("--- Détail des scores trouvés dans le CV (ligne par ligne) ---")
    for score in scores_detailles:
        print(f"Ligne {score['ligne']:3d}: {score['texte_ligne']}")
        print(f"  => {score['prenom']} {score['nom']} : total {score['score_total']} / 8 "
              f"(prénom base {score['score_prenom']['base_score']} + bonus {score['score_prenom']['bonus']} / nom {score['score_nom']})\n")

    scores_detailles.sort(
        key=lambda x: (x['score_prenom']['bonus'], x['score_total']),
        reverse=True
    )
    meilleure = scores_detailles[0]

    print("\n--- Résultat final ---")
    print(f"Prénom : {meilleure['prenom']}, Nom : {meilleure['nom']}, Score combiné : {meilleure['score_total']} / 8")

    with open("rapport_analyse_cv.txt", "w", encoding="utf-8") as f:
        f.write("--- Texte extrait du CV ---\n\n")
        f.write(texte)

if __name__ == "__main__":
    chemin_pdf = "D:/proba_CV/CV/3CV.pdf"
    analyser_cv_pdf(chemin_pdf)
