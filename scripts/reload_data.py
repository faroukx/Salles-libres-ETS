import requests
import os
import sys
import argparse

def reload_pdf(file_path, semester, api_url="http://localhost:8000/api/v1"):
    """Envoie un PDF à l'API pour recharger les données."""
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} n'existe pas.")
        return False

    url = f"{api_url}/upload-pdf"
    params = {"semester": semester}
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/pdf")}
            response = requests.post(url, params=params, files=files)
            
        if response.status_code == 200:
            print(f"Succès : {response.json()['message']}")
            return True
        else:
            print(f"Erreur {response.status_code} : {response.text}")
            return False
            
    except Exception as e:
        print(f"Erreur de connexion : {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recharger les horaires ETS depuis un PDF")
    parser.add_argument("file", help="Chemin vers le fichier PDF")
    parser.add_argument("--semester", default="Hiver 2024", help="Nom du semestre")
    parser.add_argument("--url", default="http://localhost:8000/api/v1", help="URL de l'API")
    
    args = parser.parse_args()
    reload_pdf(args.file, args.semester, args.url)
