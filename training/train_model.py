# training/train_model.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle

# Chargement des données réelles
data_path = "../data/IoTProcessed_Data.csv"
data = pd.read_csv(data_path)

# Vérification des colonnes disponibles
print("Colonnes disponibles :", data.columns.tolist())

# Supposons que les colonnes pertinentes sont :
# 'Temperature', 'Humidity', 'Water_Level', 'N', 'P', 'K', 'Pump_Action'

# Séparation des caractéristiques et de la cible
X = data[["tempreature", "humidity", "water_level", "N", "P", "K"]]
y = data["Water_pump_actuator_ON"]  # 0: Désactiver, 1: Activer

# Division des données en ensemble d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Création du modèle Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Entraînement du modèle
model.fit(X_train, y_train)

# Prédictions sur l'ensemble de test
y_pred = model.predict(X_test)

# Évaluation du modèle
print("\nRapport de classification:")
print(classification_report(y_test, y_pred))
print(f"\nPrécision du modèle : {accuracy_score(y_test, y_pred) * 100:.2f}%")

# Sauvegarde du modèle entraîné
with open("../data/model.pkl", "wb") as file:
    pickle.dump(model, file)

print("\nModèle entraîné et sauvegardé sous 'data/model.pkl'")
