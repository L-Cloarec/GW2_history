# ===========================
# Capture des prix du marché
# ===========================

#
# Import des bibliothèques
#

# pathlib : sert à manipuler des chemins de fichiers/dossiers proprement
from pathlib import Path

# datetime : sert à récupérer la date actuelle et l'heure actuelle
from datetime import datetime

# pandas : sert à manipuler des tableaux de données
import pandas as pd

# requests : sert à envoyer des requêtes HTTP vers des sites web ou des API (interface de traitement d'applications entre un serveur web et un navigateur web
import requests

#
# Création des dossiers
#

# création d'une variable contenant le chemin du dossier principal (le "r" permet de ne pas considérer les possibles caractères spéciaux)
BASE_DIR = Path(r"C:\Users\lilia\Desktop\github\jupyter\GW2_project")

# création d'un chemin vers le dossier data
DATA_DIR = BASE_DIR / "data"

# création d'un chemin vers le dossier historique
HISTORY_DIR = BASE_DIR / "history_v2" / "history"

# création du dossier parents s'ils n'existent pas, de même pas de création si le dossier existe déjà
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

#
# Chargement des objets
#

# lit le fichier créé dans le premier script
items = pd.read_parquet(DATA_DIR / "items_market.parquet")

# récupération uniquement des "id", supprime les doublons et transforme la liste en objet python
active_ids = items["id"].unique().tolist()

#
# Fonction API permettant de récupérer le prix des objets
#

# création d'une fonction qui en parcourant la liste des "ids" va les découper en lot de 200 stocké dans "chunks"
# "all_prices" va stocker de manière temporaire tous les prix récupérer via la boucle batch
# les prix de chaque objets vont être récupérer via des boucles de 200 ids
# transformation des prix en tableau pandas
def get_prices(active_ids):
    chunks = [active_ids[i:i+200] for i in range(0, len(active_ids), 200)]
    all_prices = []
    for batch in chunks:
        r = requests.get(
            "https://api.guildwars2.com/v2/commerce/prices",
            params={"ids": ",".join(map(str, batch))}
        )
        if r.status_code != 200:
            continue
        data = r.json()
        if isinstance(data, list):
            all_prices.extend(data)
    return pd.DataFrame(all_prices)

# Appel de la fonction get_prices pour les ids
df_prices = get_prices(active_ids)

#
# Obtention de la table final
#

# Fusion de la table items obtenu avec le code dans la section précédente et la table prix obtenus ici
df_analysis = df_prices.merge(items,on="id",how="left")

# Ajout des informations temporelles : date et date + heure
df_analysis["snapshot_date"] = datetime.today().date()
df_analysis["snapshot_datetime"] = datetime.now()

# Nom du fichier
filename = f"prices_snapshot_{datetime.now().strftime('%Y-%m-%d_%H')}.parquet"

# Sauvegarde du fichier
df_analysis.to_parquet(HISTORY_DIR / filename)

# Message final
print("Snapshot saved:", filename)