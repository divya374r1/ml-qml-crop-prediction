# utils/llm_explainer.py

def explain_prediction(
    crop,
    temperature,
    rainfall,
    ml_yield,
    qml_yield,
    suitability,
    advice,
    top_crops,
    language="en"
):

    texts = {
        "en": {
            "title": "Crop Yield Prediction",
            "temp": "Temperature",
            "rain": "Rainfall",
            "ml": "Classical ML Yield",
            "qml": "Quantum ML Yield",
            "suitability": "Suitability",
            "advice": "Advice",
            "recommendation": "Recommendation",
            "top": "Best Alternative Crops"
        },

        "hi": {
            "title": "फसल उत्पादन पूर्वानुमान",
            "temp": "तापमान",
            "rain": "वर्षा",
            "ml": "एमएल उत्पादन",
            "qml": "क्यूएमएल उत्पादन",
            "suitability": "उपयुक्तता",
            "advice": "सलाह",
            "recommendation": "सिफारिश",
            "top": "वैकल्पिक फसलें"
        },

        "te": {
            "title": "పంట దిగుబడి అంచనా",
            "temp": "ఉష్ణోగ్రత",
            "rain": "వర్షపాతం",
            "ml": "ML దిగుబడి",
            "qml": "QML దిగుబడి",
            "suitability": "అనుకూలత",
            "advice": "సలహా",
            "recommendation": "సిఫార్సు",
            "top": "ప్రత్యామ్నాయ పంటలు"
        },

        "ta": {
            "title": "பயிர் விளைச்சல் கணிப்பு",
            "temp": "வெப்பநிலை",
            "rain": "மழைப்பொழிவு",
            "ml": "ML விளைச்சல்",
            "qml": "QML விளைச்சல்",
            "suitability": "தகுதி",
            "advice": "ஆலோசனை",
            "recommendation": "பரிந்துரை",
            "top": "மாற்று பயிர்கள்"
        },

        "kn": {
            "title": "ಬೆಳೆ ಉತ್ಪಾದನೆ ಮುನ್ಸೂಚನೆ",
            "temp": "ತಾಪಮಾನ",
            "rain": "ಮಳೆಯ ಪ್ರಮಾಣ",
            "ml": "ML ಇಳುವರಿ",
            "qml": "QML ಇಳುವರಿ",
            "suitability": "ಯೋಗ್ಯತೆ",
            "advice": "ಸಲಹೆ",
            "recommendation": "ಶಿಫಾರಸು",
            "top": "ಪರ್ಯಾಯ ಬೆಳೆಗಳು"
        }
    }

    t = texts.get(language, texts["en"])

    # Format top crops safely
    top_text = ", ".join(top_crops) if top_crops else "No alternatives"

    explanation = f"""
🌾 {t['title']}

🌱 Crop: {crop}

🌡 {t['temp']}: {round(temperature,1)} °C  
🌧 {t['rain']}: {round(rainfall,1)} mm  

📊 {t['ml']}: {round(ml_yield,2)} tons  
⚛ {t['qml']}: {round(qml_yield,2)} tons  

📌 {t['suitability']}: {suitability}  

💡 {t['advice']}: {advice}

🌿 {t['top']}: {top_text}
"""

    return explanation