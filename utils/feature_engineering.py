"""
PHASE 3.3 — FEATURE ENGINEERING (IMPROVED)

Purpose:
Convert raw agricultural + climate inputs into a
numerical feature vector suitable for ML and QML.

NEW:
• Adds crop suitability logic (without increasing feature count)
• Prevents unrealistic predictions
• Keeps shape (1, 6) safe for ML/QML
"""

import numpy as np

# --- Encoding dictionaries ---
CROP_ENCODING = {
    "Rice": 0.1,
    "Wheat": 0.2,
    "Maize": 0.3,
    "Millets": 0.4,
    "Sorghum": 0.5,
    "Bajra": 0.55,
    "Barley": 0.6,
    "Pulses": 0.65,
    "Groundnut": 0.7,
    "Mustard": 0.75,
    "Soybean": 0.8,
    "Cotton": 0.85,
    "Sugarcane": 0.9,
    "Tea": 0.95,
    "Coffee": 1.0,
    "Other": 0.5
}

STATE_ENCODING = {
    "Karnataka": 0.1,
    "Tamil Nadu": 0.2,
    "Andhra Pradesh": 0.3,
    "Telangana": 0.4,
    "Maharashtra": 0.5,
    "Other": 0.9
}

# --- Crop suitability rules (REAL AGRI LOGIC) ---
CROP_RULES = {
    "Rice": {"temp": (20, 35), "rain": (100, 300)},
    "Wheat": {"temp": (10, 25), "rain": (50, 150)},
    "Maize": {"temp": (18, 30), "rain": (60, 200)},
    "Millets": {"temp": (25, 40), "rain": (30, 100)},
    "Sorghum": {"temp": (25, 35), "rain": (40, 100)},
    "Bajra": {"temp": (25, 40), "rain": (20, 80)},
    "Barley": {"temp": (12, 25), "rain": (30, 100)},
    "Pulses": {"temp": (20, 30), "rain": (30, 100)},
    "Groundnut": {"temp": (20, 30), "rain": (50, 125)},
    "Mustard": {"temp": (10, 25), "rain": (30, 80)},
    "Soybean": {"temp": (20, 30), "rain": (60, 150)},
    "Cotton": {"temp": (25, 35), "rain": (50, 150)},
    "Sugarcane": {"temp": (20, 35), "rain": (100, 250)},
    "Tea": {"temp": (18, 30), "rain": (150, 300)},
    "Coffee": {"temp": (18, 28), "rain": (150, 300)}
}


def apply_crop_logic(crop, temp, rain):
    """
    Adjusts inputs if crop conditions are unrealistic
    """
    rules = CROP_RULES.get(crop)

    if not rules:
        return temp, rain

    # Penalize unrealistic combinations
    if not (rules["temp"][0] <= temp <= rules["temp"][1]):
        temp = temp * 0.7  # reduce effect

    if not (rules["rain"][0] <= rain <= rules["rain"][1]):
        rain = rain * 0.6  # reduce effect

    return temp, rain


def build_feature_vector(data: dict):
    """
    Input:
        data = {
            'temperature': float (°C),
            'rainfall': float (mm),
            'crop': string,
            'state': string
        }

    Output:
        numpy array shape (1, 6)
    """

    try:
        # Raw values
        raw_temp = float(data.get("temperature", 0))
        raw_rain = float(data.get("rainfall", 0))
        crop = data.get("crop")
        state = data.get("state")

        # 🔥 APPLY CROP LOGIC HERE
        adjusted_temp, adjusted_rain = apply_crop_logic(crop, raw_temp, raw_rain)

        # Normalize
        temperature = adjusted_temp / 50.0
        rainfall = adjusted_rain / 500.0

        # Encode
        crop_val = CROP_ENCODING.get(crop, 0.5)
        state_val = STATE_ENCODING.get(state, 0.9)

        # Polynomial features
        temp_sq = temperature ** 2
        rain_sq = rainfall ** 2

        # Final vector (6 features only)
        feature_vector = np.array([
            temperature,
            rainfall,
            temp_sq,
            rain_sq,
            crop_val,
            state_val
        ], dtype=float)

        feature_vector = feature_vector.reshape(1, -1)

        return feature_vector

    except Exception as e:
        print("Feature Engineering Error:", e)
        return np.array([[0, 0, 0, 0, 0, 0]])