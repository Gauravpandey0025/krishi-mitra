import os
import io
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pickle
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# =========================
# LOAD CROP MODEL
# =========================
CROP_MODEL_PATH = os.path.join('models', 'crop_model.pkl')
crop_bundle = None

try:
    crop_bundle = joblib.load(CROP_MODEL_PATH)
    print("[OK] Crop model loaded successfully")
except Exception as e:
    print(f"[FAIL] Crop model error: {e}")

# =========================
# LOAD DISEASE MODEL
# =========================
DISEASE_MODEL_PATH = os.path.join('models', 'plant_disease_model_cpu.pth')
disease_model = None

# 10 disease classes (matches model output layer out_features=10)
DISEASE_CLASSES = [
    'Bacterial Leaf Blight',
    'Brown Spot',
    'Healthy',
    'Leaf Blast',
    'Leaf Scald',
    'Narrow Brown Spot',
    'Neck Blast',
    'Rice Hispa',
    'Sheath Blight',
    'Tungro',
]

try:
    disease_model = torch.load(DISEASE_MODEL_PATH, map_location='cpu', weights_only=False)
    disease_model.eval()
    print(f"[OK] Disease model loaded on CPU. Type: {type(disease_model).__name__}")
except Exception as e:
    print(f"[FAIL] Failed to load disease model: {e}")

# Image transforms matching EfficientNet-B3 training
disease_transform = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return "Krishi Setu Backend Running 🚀"

@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "crop_model": crop_bundle is not None,
        "disease_model": disease_model is not None
    })

# =========================
# CROP PREDICTION
# =========================
@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    if crop_bundle is None:
        return jsonify({'error': 'Crop model not loaded'}), 500

    try:
        data = request.get_json()

        N = float(data['N'])
        P = float(data['P'])
        K = float(data['K'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])

        # Feature engineering
        NPK_sum = N + P + K
        NK_ratio = N / (K + 1e-8)
        temp_hum = temperature * humidity
        rain_hum = rainfall * humidity
        ph_N = ph * N
        fertility = (N + P + K) / 3.0

        features = np.array([[
            N, P, K, temperature, humidity, ph, rainfall,
            NPK_sum, NK_ratio, temp_hum, rain_hum, ph_N, fertility
        ]])

        scaler = crop_bundle['scaler']
        rf = crop_bundle['rf']
        le = crop_bundle['le']

        X_scaled = scaler.transform(features)

        pred = rf.predict(X_scaled)
        label = le.inverse_transform(pred)[0]

        return jsonify({
            "success": True,
            "prediction": label,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# DISEASE PREDICTION
# =========================
@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    if disease_model is None:
        return jsonify({'error': 'Disease model not loaded'}), 500

    print("FILES:", request.files)

    # Accept both 'file' and 'image' field names
    file = request.files.get('file') or request.files.get('image')
    if file is None:
        return jsonify({'error': 'No image provided'}), 400

    if file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    try:
        image_bytes = file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = disease_transform(img).unsqueeze(0)  # [1, 3, 300, 300]

        with torch.no_grad():
            output = disease_model(input_tensor)
            probabilities = F.softmax(output, dim=1)[0]
            max_prob, max_idx = torch.max(probabilities, 0)

        predicted_class = DISEASE_CLASSES[max_idx.item()]
        confidence = float(max_prob.item()) * 100

        return jsonify({
            'success': True,
            'prediction': predicted_class,
            'confidence': round(confidence, 2),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# =========================
# RUN LOCALHOST
# =========================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
