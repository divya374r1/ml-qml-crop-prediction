from utils.weather import get_weather

temp, rain = get_weather("Bangalore", "Karnataka")

print("Temperature:", temp)
print("Rainfall:", rain)