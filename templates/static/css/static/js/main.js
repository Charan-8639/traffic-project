// ── Sync slider with number input ──
function syncSlider(val) {
  document.getElementById('inp-vehicles').value = val;
  document.getElementById('slider-display').textContent = val;
}

document.getElementById('inp-vehicles').addEventListener('input', function () {
  document.getElementById('slider-vehicles').value = this.value;
  document.getElementById('slider-display').textContent = this.value;
});

// ── Predict ──
async function predict() {
  const timeVal   = document.getElementById('inp-time').value;
  const vehicles  = parseInt(document.getElementById('inp-vehicles').value) || 0;
  const weather   = document.getElementById('inp-weather').value;
  const weatherTxt = document.getElementById('inp-weather').options[document.getElementById('inp-weather').selectedIndex].text;

  const hour = parseInt(timeVal.split(':')[0]);

  document.getElementById('btn-text').textContent = 'Predicting...';

  try {
    const res  = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hour, vehicle_count: vehicles, weather })
    });

    const data = await res.json();
    showResult(data, timeVal, vehicles, weatherTxt);
  } catch (err) {
    alert('Prediction failed. Make sure the Flask server is running.');
  }

  document.getElementById('btn-text').textContent = 'Predict Traffic Level';
}

// ── Show result ──
function showResult(data, timeVal, vehicles, weatherTxt) {
  const { prediction, probabilities, stats, tips, color } = data;

  const icons = { Low: '🟢', Medium: '🟡', High: '🔴' };
  const cls   = prediction.toLowerCase();

  // Meta
  document.getElementById('result-meta').textContent =
    `Time: ${timeVal}  ·  Vehicles: ${vehicles}/min  ·  ${weatherTxt}`;

  // Level icon & text
  const icon = document.getElementById('level-icon');
  icon.textContent = icons[prediction];
  icon.style.background = cls === 'low' ? '#dcfce7' : cls === 'medium' ? '#fef9c3' : '#fee2e2';

  const lvlText = document.getElementById('level-text');
  lvlText.textContent = prediction.toUpperCase() + ' TRAFFIC';
  lvlText.style.color = color;

  // Probability bars
  ['Low', 'Medium', 'High'].forEach(l => {
    const lc = l.toLowerCase();
    const pct = probabilities[l] || 0;
    document.getElementById('prob-' + lc).style.width = pct + '%';
    document.getElementById('pct-' + lc).textContent  = pct + '%';
  });

  // Stats
  const sv = document.getElementById('stat-speed');
  const dv = document.getElementById('stat-delay');
  const sig = document.getElementById('stat-signal');
  sv.textContent  = stats.speed;  sv.style.color  = color;
  dv.textContent  = stats.delay;  dv.style.color  = color;
  sig.textContent = stats.signal; sig.style.color = color;

  // Tips
  document.getElementById('tips-box').innerHTML =
    `<div class="tip-title">Recommendations</div>` +
    tips.map(t => `
      <div class="tip-item">
        <div class="tip-dot ${cls}"></div>
        <span>${t}</span>
      </div>`).join('');

  // Scroll to result
  document.getElementById('result-card').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Charts ──
async function loadCharts() {
  const res  = await fetch('/chart-data');
  const data = await res.json();

  // 1. Hourly line chart
  new Chart(document.getElementById('chartHourly'), {
    type: 'line',
    data: {
      labels: data.hourly.hours.map(h => h + ':00'),
      datasets: [
        { label: 'Low',    data: data.hourly.low,    borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.1)',   fill: true, tension: 0.4, pointRadius: 3 },
        { label: 'Medium', data: data.hourly.medium, borderColor: '#eab308', backgroundColor: 'rgba(234,179,8,0.1)',   fill: true, tension: 0.4, pointRadius: 3 },
        { label: 'High',   data: data.hourly.high,   borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,0.1)',   fill: true, tension: 0.4, pointRadius: 3 },
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: {
        x: { grid: { color: '#f1f5f9' } },
        y: { grid: { color: '#f1f5f9' }, beginAtZero: true }
      }
    }
  });

  // 2. Doughnut distribution
  const dist = data.distribution;
  new Chart(document.getElementById('chartDist'), {
    type: 'doughnut',
    data: {
      labels: Object.keys(dist),
      datasets: [{
        data: Object.values(dist),
        backgroundColor: ['#22c55e', '#eab308', '#ef4444'],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.raw} records`
          }
        }
      }
    }
  });

  // 3. Weather grouped bar
  new Chart(document.getElementById('chartWeather'), {
    type: 'bar',
    data: {
      labels: data.weather.labels,
      datasets: [
        { label: 'Low',    data: data.weather.low,    backgroundColor: '#22c55e' },
        { label: 'Medium', data: data.weather.medium, backgroundColor: '#eab308' },
        { label: 'High',   data: data.weather.high,   backgroundColor: '#ef4444' },
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true, grid: { color: '#f1f5f9' } }
      }
    }
  });
}

loadCharts();
