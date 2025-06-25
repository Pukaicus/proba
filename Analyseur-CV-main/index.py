import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import xml.etree.ElementTree as ET

# Import des extracteurs
from information.nom import extraire_prenom_nom
from information.education import extraire_education
from information.telephone import extraire_numero_telephone
from information.email import extraire_email
from information.competence import extraire_competences
from information.experiences import extraire_experiences
import lecteurfichiers.pdf2text as pdf2text


def generer_xml(nom, numero_telephone, email, education, competences, experiences, chemin_sortie):
    root = ET.Element("CV")

    identite = ET.SubElement(root, "Identite")
    ET.SubElement(identite, "Nom").text = nom if nom else "Inconnu"
    ET.SubElement(identite, "Email").text = email if email else "Inconnu"
    ET.SubElement(identite, "Telephone").text = numero_telephone if numero_telephone else "Inconnu"

    formations = ET.SubElement(root, "Formations")
    for formation in education:
        ET.SubElement(formations, "Formation").text = formation

    competences_xml = ET.SubElement(root, "Competences")
    for comp in competences:
        ET.SubElement(competences_xml, "Competence").text = comp

    experiences_xml = ET.SubElement(root, "Experiences")
    for exp in experiences:
        ET.SubElement(experiences_xml, "Experience").text = exp

    tree = ET.ElementTree(root)
    tree.write(chemin_sortie, encoding='utf-8', xml_declaration=True)


def process(initial_filepath, root):
    from tkinter import filedialog as fd
    from tkinter import messagebox
    import re
    import time
    import os

    # Sélection du fichier PDF
    chemin_fichier = fd.askopenfilename(
        initialdir=initial_filepath,
        title='Sélectionner le fichier',
        filetypes=(('fichiers PDF', '*.pdf'),)
    )
    if not chemin_fichier:
        return

    # Extraction du texte du CV
    texte = pdf2text.get_Text(chemin_fichier)

    # Création du dossier output s’il n’existe pas
    dossier_output = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(dossier_output, exist_ok=True)

    # Sauvegarde du texte brut dans un fichier rapport
    chemin_rapport = os.path.join(dossier_output, "rapport_analyse_cv.txt")
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(texte)

    # Affichage d'un extrait du texte dans le terminal
    print("------ TEXTE BRUT EXTRAIT ------")
    print(texte[:1000])
    print("------ FIN EXTRAIT TEXTE ------\n")

    # Extraction des informations
    nom              = extraire_prenom_nom(texte)
    numero_telephone = extraire_numero_telephone(texte)
    email            = extraire_email(texte)
    education        = extraire_education(texte)
    competences      = extraire_competences(texte)
    experiences      = extraire_experiences(texte)

    # Nettoyage et génération du nom de fichier XML sécurisé
    if nom:
        nom_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', nom)
        if len(nom_clean) < 3:
            nom_clean = f"cv_inconnu_{int(time.time())}"
    else:
        nom_clean = f"cv_inconnu_{int(time.time())}"

    nom_fichier_xml = f"{nom_clean}.xml"
    chemin_sortie = os.path.join(dossier_output, nom_fichier_xml)

    # Génération du fichier XML
    generer_xml(nom, numero_telephone, email, education, competences, experiences, chemin_sortie)

    # Message de confirmation
    messagebox.showinfo("Terminé", f"Fichier XML généré dans :\n{chemin_sortie}")

if __name__ == '__main__':
    largeur = 600
    hauteur = 300

    root = tk.Tk()
    root.title("Analyseur de CV")

    largeur_ecran = root.winfo_screenwidth()
    hauteur_ecran = root.winfo_screenheight()
    x = (largeur_ecran / 2) - (largeur / 2)
    y = (hauteur_ecran / 2) - (hauteur / 2)

    root.geometry(f"{largeur}x{hauteur}+{int(x)}+{int(y)}")

    bouton = ttk.Button(root, text='Parcourir le fichier')
    bouton.config(command=lambda chemin_fichier='.': process(chemin_fichier, root))
    bouton.pack(fill=X)

    root.mainloop()
