import pandas as pd
import numpy as np
import math

def charger_prenoms_depuis_csv(csv_path):
    df = pd.read_csv(csv_path, sep='\t', dtype=str)
    df = df[df["preusuel"] != "_PRENOMS_RARES"]
    df["nombre"] = pd.to_numeric(df["nombre"], errors='coerce').fillna(0).astype(int)
    freq_series = df.groupby("preusuel")["nombre"].sum()
    total = freq_series.sum()
    # Filtrer prénoms de moins de 3 lettres
    freq_series = freq_series[[len(prenom) >= 3 for prenom in freq_series.index]]
    rarity = {prenom.upper(): -math.log(freq / total) for prenom, freq in freq_series.items()}
    bins = np.histogram_bin_edges(list(rarity.values()), bins=7)
    return rarity, bins

def score_rarete(val, bins):
    return min(8, np.digitize(val, bins) - 1)

import unicodedata

def normalize(text):
    # Normalise en ASCII MAJUSCULES sans accents
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').upper().strip()

def get_prenom_score(prenom, prenoms_base, bins_prenom, email=None, nom=None, texte=None):
    p_clean = normalize(prenom)

    mois_blacklist = {
        "JANVIER", "FÉVRIER", "FEVRIER", "MARS", "AVRIL", "MAI", "JUIN", "JUILLET",
        "AOÛT", "AOUT", "SEPTEMBRE", "OCTOBRE", "NOVEMBRE", "DÉCEMBRE", "DECEMBRE"
    }

    if p_clean in mois_blacklist or len(p_clean) < 3:
        return {
            "prenom": prenom,
            "base_score": 0,
            "bonus": 0,
            "final_score": 0
        }

    # Exemple de suite du calcul de score (simplifié)
    base_score = 1
    bonus = 0
    # Ici, tu rajoutes ta logique de score réelle avec prenoms_base, bins_prenom, etc.

    final_score = base_score + bonus
    return {
        "prenom": prenom,
        "base_score": base_score,
        "bonus": bonus,
        "final_score": final_score
    }


def get_prenom_score(prenom, rarity_dict, bins, email=None, nom=None, texte=None):
    p_clean = prenom.strip().upper()

    rare_val = rarity_dict.get(p_clean, None)

    # Score de base = 0 si prénom inconnu
    base_score = 0 if rare_val is None else score_rarete(rare_val, bins)

    bonus = 0
    if email and p_clean.lower() in email.lower():
        bonus += 2
    if nom and p_clean.lower() in nom.lower():
        bonus += 2
    if texte:
        text_lower = texte.lower()
        if any(tag in text_lower for tag in ['linkedin', 'github', 'twitter', 'instagram', 'facebook']):
            if p_clean.lower() in text_lower:
                bonus += 2

    final_score = min(8, base_score + bonus)

    return {
        "prenom": prenom,
        "base_score": base_score,
        "bonus": bonus,
        "final_score": final_score
    }

# --- TEST ---
if __name__ == "__main__":
    rarity, bins = charger_prenoms_depuis_csv("data/prenoms.csv")
    test_prenom = "Jean"
    test_email = "jean.dupont@example.com"
    test_nom = "Dupont"
    test_texte = "Linkedin: Jean Dupont, github.com/jeandupont"

    score = get_prenom_score(test_prenom, rarity, bins, email=test_email, nom=test_nom, texte=test_texte)
    print(f"Score prénom {test_prenom} : base {score['base_score']}, bonus {score['bonus']}, final {score['final_score']}")
