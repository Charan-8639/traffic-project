import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os
os.makedirs('model', exist_ok=True)
np.random.seed(42)
n = 2000

hours = np.random.randint(0, 24, n)
vehicles = np.random.randint(10, 300, n)
weather_options = ['clear', 'cloudy', 'rain', 'heavy_rain', 'fog', 'snow']
weather = np.random.choice(weather_options, n)

weather_score = {'clear': 0, 'cloudy': 5, 'rain': 15, 'heavy_rain': 25, 'fog': 20, 'snow': 30}

labels = []
for i in range(n):
    score = 0
    h = hours[i]
    if (7 <= h <= 9) or (17 <= h <= 20):
        score += 40
    elif h >= 23 or h <= 5:
        score += 5
    else:
        score += 20

    v = vehicles[i]
    if v < 50:   score += 10
    elif v < 100: score += 25
    elif v < 150: score += 40
    else:         score += 55

    score += weather_score[weather[i]]
    score = min(score, 100)

    if score <= 40:   labels.append('Low')
    elif score <= 70: labels.append('Medium')
    else:             labels.append('High')

df = pd.DataFrame({
    'hour': hours,
    'vehicle_count': vehicles,
    'weather': weather,
    'traffic_level': labels
})

df.to_csv('model/traffic_dataset.csv', index=False)
print("Dataset created:", df['traffic_level'].value_counts().to_dict())

le = LabelEncoder()
df['weather_enc'] = le.fit_transform(df['weather'])

X = df[['hour', 'vehicle_count', 'weather_enc']]
y = df['traffic_level']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {acc*100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

with open('model/traffic_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('model/label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("\nModel saved to model/traffic_model.pkl")
