import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Configuration
BASE_URL = "https://www.etsmtl.ca/etudier-a-lets/inscription-aux-cours/horaire-cours"
UPLOAD_DIR = "data/uploads"

def get_current_semester_info():
    """Retourne le nom et le code de la session actuelle."""
    month = datetime.now().month
    year = datetime.now().year
    
    if 1 <= month <= 4:
        return "Hiver", "H", year
    elif 5 <= month <= 8:
        return "Été", "E", year
    else:
        return "Automne", "A", year

def normalize(text):
    if not text: return ""
    text = text.lower()
    accents = {'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'î': 'i', 'ï': 'i', 'ô': 'o', 'û': 'u', 'ù': 'u', 'é': 'e'}
    for char, replacement in accents.items():
        text = text.replace(char, replacement)
    return text

def fetch_all_schedules(filter_current=True):
    sem_full, sem_code, sem_year = get_current_semester_info()
    # Sur le site de l'ETS, ils utilisent souvent "H-2026" ou "É-2026"
    target_pattern = f"{sem_code}-{sem_year}"
    target_pattern_alt = f"{sem_full} {sem_year}"
    
    print(f"🔍 Recherche des horaires pour : {sem_full} {sem_year} ({target_pattern})")
    
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    try:
        # On utilise un User-Agent pour éviter d'être bloqué
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erreur accès site : {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = []
    
    # On cherche tous les liens PDF
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.text.strip()
        
        if href.lower().endswith('.pdf'):
            full_url = urljoin(BASE_URL, href)
            search_area = normalize(text + " " + href)
            
            # Détection ultra-souple :
            # 1. Cherche le code (ex: H-2026)
            # 2. OU cherche le nom complet (ex: hiver 2026)
            # 3. OU cherche le code sans tiret (ex: H2026)
            is_match = (normalize(target_pattern) in search_area) or \
                       (normalize(target_pattern_alt) in search_area) or \
                       (normalize(sem_code + str(sem_year)) in search_area)

            if not filter_current or is_match:
                pdf_links.append((text or "Horaire", full_url))

    if not pdf_links:
        print(f"⚠️ Aucun PDF trouvé avec les filtres stricts. Tentative de secours...")
        # Secours : on prend tous les PDFs qui ont "horaire" dans le nom
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.lower().endswith('.pdf') and 'horaire' in normalize(href):
                pdf_links.append(("Horaire Secours", urljoin(BASE_URL, href)))

    # Supprimer les doublons
    unique_pdfs = {}
    for name, url in pdf_links:
        unique_pdfs[url] = name
    
    if not unique_pdfs:
        print("❌ Aucun horaire trouvé sur la page.")
        return []

    print(f"✅ {len(unique_pdfs)} fichier(s) identifié(s).")
    
    downloaded = []
    for url, name in unique_pdfs.items():
        filename = url.split('/')[-1]
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        print(f"⬇️ Téléchargement : {filename}...")
        try:
            pdf_res = requests.get(url, timeout=30)
            pdf_res.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(pdf_res.content)
            downloaded.append(filepath)
        except Exception as e:
            print(f"❌ Erreur sur {filename} : {e}")

    return downloaded

if __name__ == "__main__":
    fetch_all_schedules()
