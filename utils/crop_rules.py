def check_crop_suitability(crop, temperature, rainfall, state=None):

    crop = crop.lower()

    rules = {

        "rice": {
            "temp": (18, 38),
            "rain": (50, 350),
            "states": ["karnataka", "tamil nadu", "andhra pradesh", "west bengal"]
        },

        "wheat": {
            "temp": (10, 30),
            "rain": (30, 200),
            "states": ["punjab", "haryana", "uttar pradesh"]
        },

        "maize": {
            "temp": (15, 35),
            "rain": (30, 250),
            "states": ["karnataka", "maharashtra", "bihar"]
        },

        "cotton": {
            "temp": (20, 40),
            "rain": (30, 200),
            "states": ["maharashtra", "gujarat", "telangana"]
        },

        "sugarcane": {
            "temp": (20, 40),
            "rain": (80, 300),
            "states": ["uttar pradesh", "maharashtra", "karnataka"]
        },

        "coffee": {
            "temp": (15, 32),
            "rain": (80, 300),
            "states": ["karnataka", "kerala"]
        },

        "tea": {
            "temp": (15, 35),
            "rain": (80, 300),
            "states": ["assam", "west bengal"]
        }
    }

    if crop not in rules:
        return "Unknown", "No data available"

    rule = rules[crop]

    # ✅ REGION CHECK
    if state and state.lower() not in rule["states"]:
        return "Not Suitable", "This crop is not commonly grown in this region"

    temp_min, temp_max = rule["temp"]
    rain_min, rain_max = rule["rain"]

    if temp_min <= temperature <= temp_max and rain_min <= rainfall <= rain_max:
        return "Suitable", "Good climatic conditions"

    if temp_min <= temperature <= temp_max:
        return "Moderately Suitable", "Irrigation or water management required"

    return "Not Suitable", "Climate conditions not ideal"