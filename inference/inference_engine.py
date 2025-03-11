import pickle
import numpy as np

class InferenceEngine:
    def __init__(self, model_path):
        """
        Load the pre-trained model for irrigation decision-making.
        :param model_path: Path to the saved machine learning model.
        """
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print("✅ Inference model successfully loaded.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None

    def preprocess_data(self, sensor_data):
        """
        Preprocess sensor data before feeding it to the model.
        :param sensor_data: Dictionary containing sensor readings.
        :return: Preprocessed data as numpy array.
        """
        try:
            features = np.array([
                sensor_data.get("temperature", 0),
                sensor_data.get("humidity", 0),
                sensor_data.get("soil_moisture", 0),
                sensor_data.get("rainfall", 0),
            ]).reshape(1, -1)
            return features
        except Exception as e:
            print(f"❌ Error in data preprocessing: {e}")
            return None

    def predict_action(self, sensor_data):
        """
        Predict irrigation action based on sensor input.
        :param sensor_data: Dictionary containing sensor readings.
        :return: Suggested irrigation action (e.g., 'START', 'STOP', 'INCREASE').
        """
        preprocessed_data = self.preprocess_data(sensor_data)
        if preprocessed_data is not None and self.model:
            prediction = self.model.predict(preprocessed_data)[0]
            if prediction == 1:
                return "START"
            elif prediction == 0:
                return "STOP"
            else:
                return "UNKNOWN"
        else:
            return "ERROR"

if __name__ == "__main__":
    engine = InferenceEngine("../data/model.pkl")

    # Simulated sensor data
    test_data = {
        "temperature": 28,
        "humidity": 60,
        "soil_moisture": 35,
        "rainfall": 0
    }

    decision = engine.predict_action(test_data)
    print(f"Decision: {decision}")
