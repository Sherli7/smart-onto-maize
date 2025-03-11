import pandas as pd
from fastapi import APIRouter, HTTPException
from pathlib import Path

router = APIRouter(prefix="",tags=["ioTDataReader"])

# 📌 Définition du chemin du fichier CSV
CSV_FILE_PATH = Path("../data/IoTProcessed_Data.csv")

@router.get("", tags=["IoT Data"])
def read_iot_data():
    """Retourne les données IoT traitées depuis le fichier CSV."""
    if not CSV_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Fichier IoTProcessed_Data.csv introuvable")

    try:
        # 📌 Charger le fichier CSV en DataFrame
        df = pd.read_csv(CSV_FILE_PATH)

        # 📌 Trier les données par date
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(by="date")

        # 📌 Convertir en JSON et renvoyer la réponse
        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de lecture du fichier CSV: {str(e)}")
