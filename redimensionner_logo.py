"""
Redimensionner le logo pour les différents besoins
"""

from PIL import Image
import os


def redimensionner_logo():
    """Crée toutes les tailles nécessaires à partir du logo principal"""

    # Vérifier que le logo existe
    if not os.path.exists('static/images/logo.png'):
        print("❌ Erreur : Place d'abord ton logo dans static/images/logo.png")
        return

    # Ouvrir le logo
    logo = Image.open('static/images/logo.png').convert('RGBA')

    # Tailles à créer
    tailles = {
        'logo_192.new.png': (192, 'PNG'),
        'logo_512.png': (512, 'PNG'),
        'logo_1024.png': (1024, 'PNG'),
    }

    for nom, (taille, format_img) in tailles.items():
        # Redimensionner en gardant les proportions
        logo_resize = logo.resize((taille, taille), Image.Resampling.LANCZOS)

        # Sauvegarder
        chemin = f'static/images/{nom}'
        logo_resize.save(chemin, format=format_img)
        print(f"✅ Créé : {chemin}")

    # Créer le favicon (16x16, 32x32, 48x48 dans un seul .ico)
    logo_16 = logo.resize((16, 16), Image.Resampling.LANCZOS)
    logo_32 = logo.resize((32, 32), Image.Resampling.LANCZOS)
    logo_48 = logo.resize((48, 48), Image.Resampling.LANCZOS)

    # Sauvegarder en .ico avec plusieurs tailles
    logo_32.save('static/images/favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"✅ Créé : static/images/favicon.ico")

    print("\n🎉 Tous les logos créés avec succès !")


if __name__ == '__main__':
    redimensionner_logo()
