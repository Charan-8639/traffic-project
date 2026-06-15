from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

# Load model and encoder
with open('model/traffic_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('model/label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)

# Load dataset for chart stats
df = pd.read_csv('model/traffic_dataset.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    hour        = int(data['hour'])
    vehicles    = int(data['vehicle_count'])
    weather_str = data['weather']

    weather_enc = le.transform([weather_str])[0]
    features = pd.DataFrame([[hour, vehicles, weather_enc]],
                            columns=['hour', 'vehicle_count', 'weather_enc'])

    prediction = model.predict(features)[0]
    proba      = model.predict_proba(features)[0]
    classes    = model.classes_

    proba_dict = {cls: round(float(p) * 100, 1) for cls, p in zip(classes, proba)}

    # Extra stats based on level
    stats = {
        'Low':    {'speed': 55, 'delay': 2,  'signal': 30, 'color': '#16a34a'},
        'Medium': {'speed': 30, 'delay': 10, 'signal': 55, 'color': '#ca8a04'},
        'High':   {'speed': 12, 'delay': 25, 'signal': 90, 'color': '#dc2626'},
    }

    tips = {
        'Low':    ['Roads clear — good time to travel.', 'No delays expected.', 'Normal signal timing (30s).', 'Ideal for heavy vehicles.'],
        'Medium': ['Allow extra 10 min travel time.', 'Consider alternate routes.', 'Green extended to 55s.', 'Monitor — may worsen.'],
        'High':   ['Severe congestion — avoid if possible.', 'Deploy traffic personnel.', 'Max green signal 90s.', 'Consider road diversions.'],
    }

    return jsonify({
        'prediction': prediction,
        'probabilities': proba_dict,
        'stats': stats[prediction],
        'tips': tips[prediction],
        'color': stats[prediction]['color']
    })

@app.route('/chart-data')
def chart_data():
    # Traffic by hour
    hourly = df.groupby(['hour', 'traffic_level']).size().unstack(fill_value=0).reset_index()
    hours = hourly['hour'].tolist()

    def safe_col(col):
        return hourly[col].tolist() if col in hourly.columns else [0]*len(hours)

    # Distribution pie
    dist = df['traffic_level'].value_counts().to_dict()

    # Weather vs traffic
    wt = df.groupby(['weather', 'traffic_level']).size().unstack(fill_value=0).reset_index()

    return jsonify({
        'hourly': {
            'hours': hours,
            'low':    safe_col('Low'),
            'medium': safe_col('Medium'),
            'high':   safe_col('High'),
        },
        'distribution': dist,
        'weather': {
            'labels': wt['weather'].tolist(),
            'low':    safe_col('Low') if False else (wt['Low'].tolist()    if 'Low'    in wt.columns else []),
            'medium': safe_col('Medium') if False else (wt['Medium'].tolist() if 'Medium' in wt.columns else []),
            'high':   safe_col('High') if False else (wt['High'].tolist()   if 'High'   in wt.columns else []),
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
