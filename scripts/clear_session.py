import os
import shutil
from pathlib import Path

# Configuration
UPLOAD_DIR = "data/uploads"
DB_FILE = "ets_rooms.db"

def clear_session():
    print("🧹 Nettoyage de la session en cours...")
    
    # 1. Supprimer la base de données
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print(f"✅ Base de données '{DB_FILE}' supprimée.")
        except Exception as e:
            print(f"❌ Erreur lors de la suppression de la base : {e}")
    else:
        print("ℹ️ Aucune base de données trouvée.")

    # 2. Nettoyer le dossier d'uploads
    if os.path.exists(UPLOAD_DIR):
        try:
            # On supprime le contenu du dossier sans supprimer le dossier lui-même
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print(f"✅ Dossier '{UPLOAD_DIR}' vidé.")
        except Exception as e:
            print(f"❌ Erreur lors du nettoyage du dossier d'uploads : {e}")
    else:
        print(f"ℹ️ Le dossier '{UPLOAD_DIR}' n'existe pas.")

    print("\n✨ Session nettoyée ! L'application est prête pour de nouvelles données.")

if __name__ == "__main__":
    clear_session()
