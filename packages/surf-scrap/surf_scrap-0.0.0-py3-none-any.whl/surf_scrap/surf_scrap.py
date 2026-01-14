import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# --- 1. CONFIGURATION ---
url = "https://www.surf-report.com/meteo-surf/lacanau-s1043.html"  # Remplace par l'URL cible
output_folder = "data_surf"
output_filename = "data_surf.csv"

# 2. REQUÊTE ET ANALYSE ---
response = requests.get(url)

# Vérifier si la page a bien été récupérée
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Trouver les jours de prévisions
    days = soup.find_all('div', class_='forecast-tab')
    data = []

    # --- 3. EXTRACTION DES DONNÉES ---
    for day in days:
        titre = day.find('b')
        if titre:
            day_text = titre.text.strip()

            hours = day.find_all('div', class_='cell date with-border')
            waves = day.find_all('div', class_='cell large waves with-border')
            winds = day.select('div[class^="wind wind"]')
            wind_directions = day.find_all('img', alt=lambda alt: alt and 'Orientation vent' in alt)

            # Boucle sur les heures de la journée
            for i in range(len(hours)):
                try:
                    hour = hours[i].text.strip()
                    wave = waves[i].text.strip()
                    wind = winds[i].text.strip()
                    # On utilise .get('alt') pour éviter les erreurs si l'attribut manque
                    wind_dir = wind_directions[i].get('alt', '').strip()

                    data.append([day_text, hour, wave, wind, wind_dir])
                except IndexError:
                    # Au cas où une liste est plus courte qu'une autre
                    continue

    # --- 4. CRÉATION DU DATAFRAME ET SAUVEGARDE ---
    if data:
        df = pd.DataFrame(data, columns=['Day', 'Hour', 'Waves_size', 'Wind_speed', 'Wind_direction'])

        # Gestion du dossier de sortie
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        csv_path = os.path.join(output_folder, output_filename)
        df.to_csv(csv_path, index=False)

        print(f"Scraping terminé ! {len(df)} lignes sauvegardées dans : {csv_path}")
        
        # Afficher un aperçu
        print(df.head())
    else:
        print("⚠️ Aucune donnée n'a été trouvée. Vérifiez les classes HTML du site.")

else:
    print(f"❌ Erreur lors de l'accès au site (Code : {response.status_code})")

