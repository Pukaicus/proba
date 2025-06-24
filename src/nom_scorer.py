import pandas as pd
import numpy as np
import math

def charger_noms_depuis_csv(csv_path):
    df = pd.read_csv(csv_path, sep='\t', encoding='utf-8')
    df = df.set_index(df.columns[0])
    freq = df.sum(axis=1)
    total = freq.sum()
    rarity = {nom.upper(): -math.log(f / total) for nom, f in freq.items() if f > 0 and len(nom) >= 3}
    bins = np.histogram_bin_edges(list(rarity.values()), bins=7)
    return rarity, bins

def score_rarete(val, bins):
    return min(6, np.digitize(val, bins) - 1)

def get_nom_score(nom, rarity_dict, bins, email=None, texte=None, prenom=None):
    blacklist_noms = {
        "POWER", "GENIE", "POINT", "EXPERT", "COMPTA", "SAGE", "AVRIL", "MARS",
        "MOVIE", "ACCESS", "WINDOWS", "CISCO", "JEE", "PIX", "ORACLE", "COREL",
        "DEPUIS", "FREE", "POL", "AOUT", "SEPTEMBRE", "DECEMBRE", "JUIN", "JUILLET"
    }

    n_clean = nom.strip().upper()

    if n_clean in blacklist_noms or len(n_clean) < 3:
        return 1  # Faible score pour éviter les faux positifs

    rare_val = rarity_dict.get(n_clean, None)
    base_score = score_rarete(rare_val, bins) if rare_val else 1

    bonus = 0
    if email and n_clean.lower() in email.lower():
        bonus += 1
    if prenom and n_clean.lower() in prenom.lower():
        bonus += 1
    if texte and n_clean.lower() in texte.lower():
        bonus += 1

    final_score = min(6, base_score + bonus)
    return final_score

# --- TEST ---
if __name__ == "__main__":
    rarity, bins = charger_noms_depuis_csv("data/noms.csv")
    test_nom = "AABI"
    test_email = "aabi@example.com"
    test_texte = "LinkedIn: AABI profile"
    test_prenom = "Jean"

    score = get_nom_score(test_nom, rarity, bins, email=test_email, texte=test_texte, prenom=test_prenom)
    print(f"Score nom {test_nom} : {score}")
