import re

def extraire_numero_telephone(texte_cv):
    # Expression régulière pour numéro français classique
    pattern = re.compile(
        r'(\+33\s?|0033\s?|0)[1-9](?:[\s\.-]?\d{2}){4}'
    )

    resultats = pattern.findall(texte_cv)
    if resultats:
        # La regex trouve des correspondances, mais findall avec groupes capture uniquement le groupe
        # Il vaut mieux utiliser finditer pour récupérer la chaîne complète
        matches = pattern.finditer(texte_cv)
        for match in matches:
            numero = match.group()
            # Nettoyer le numéro pour garder uniquement chiffres et +
            numero_nettoye = re.sub(r'[^\d+]', '', numero)
            return numero_nettoye

    return None
