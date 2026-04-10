import os
import io
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import pickle
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image

app = Flask(__name__)
CORS(app)

# ──────────────────────────────────────────────
# 1. CROP RECOMMENDATION MODEL  (sklearn)
# ──────────────────────────────────────────────
CROP_MODEL_PATH = os.path.join('models', 'crop_model.pkl')
crop_bundle = None

try:
    crop_bundle = joblib.load(CROP_MODEL_PATH)
    print(f"[OK] Crop model loaded. Keys: {crop_bundle.keys()}")
    print(f"     Features expected: {crop_bundle['features']}")
except Exception as e:
    print(f"[FAIL] Failed to load crop model: {e}")

# ──────────────────────────────────────────────
# 2. PLANT DISEASE MODEL  (PyTorch EfficientNet)
# ──────────────────────────────────────────────
DISEASE_MODEL_PATH = os.path.join('models', 'plant_disease_model.pkl')
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
    with open(DISEASE_MODEL_PATH, 'rb') as f:
        disease_model = pickle.load(f)
    # Model was trained on CUDA; move all parameters to CPU
    disease_model = disease_model.to('cpu')
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


# ══════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    """Predict the best crop based on soil + climate features."""
    if crop_bundle is None:
        return jsonify({'error': 'Crop model not loaded on the server'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Raw inputs
        N = float(data['N'])
        P = float(data['P'])
        K = float(data['K'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])

        # Engineered features (must match training)
        NPK_sum = N + P + K
        NK_ratio = N / (K + 1e-8)
        temp_hum = temperature * humidity
        rain_hum = rainfall * humidity
        ph_N = ph * N
        fertility = (N + P + K) / 3.0

        feature_vector = np.array([[
            N, P, K, temperature, humidity, ph, rainfall,
            NPK_sum, NK_ratio, temp_hum, rain_hum, ph_N, fertility
        ]])

        # Scale
        scaler = crop_bundle['scaler']
        X_scaled = scaler.transform(feature_vector)

        # Predict with Random Forest (primary model)
        rf = crop_bundle['rf']
        le = crop_bundle['le']

        prediction_encoded = rf.predict(X_scaled)
        prediction_label = le.inverse_transform(prediction_encoded)[0]

        # Confidence from RF
        confidence = None
        if hasattr(rf, 'predict_proba'):
            probs = rf.predict_proba(X_scaled)[0]
            confidence = float(np.max(probs)) * 100

        return jsonify({
            'success': True,
            'prediction': str(prediction_label),
            'confidence': confidence,
        })

    except KeyError as e:
        return jsonify({'error': f'Missing field: {e}'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """Predict plant disease from an uploaded leaf image."""
    if disease_model is None:
        return jsonify({'error': 'Disease model not loaded on the server'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
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


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'crop_model_loaded': crop_bundle is not None,
        'disease_model_loaded': disease_model is not None,
    })


if __name__ == '__main__':
    print("Starting KrishiMitra Backend Server...")
    app.run(debug=True, port=5000)
