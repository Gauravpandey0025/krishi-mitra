// Simple crop recommendation logic for demo
const form = document.getElementById('crop-form');
const resultsSection = document.getElementById('results-section');

function createResultCard(title, details) {
  return `
    <div class="bg-white rounded-xl shadow-lg p-6 mb-4">
      <h4 class="text-xl font-semibold text-gray-900 mb-2">${title}</h4>
      <p class="text-gray-700">${details}</p>
    </div>
  `;
}

function recommendCrop(values) {
  // Very simple heuristic-based recommendations for demo purposes
  const { ph, nitrogen, phosphorus, potassium, moisture, temperature, season } = values;
  const crops = [];

  // pH based suggestions
  if (ph >= 6 && ph <= 7.5) {
    crops.push({ name: 'Wheat', reason: 'Ideal pH for wheat and common in Rabi season' });
    crops.push({ name: 'Maize', reason: 'Suitable for neutral soils and multiple seasons' });
  } else if (ph < 6) {
    crops.push({ name: 'Rice', reason: 'Tolerates slightly acidic soils' });
  } else {
    crops.push({ name: 'Barley', reason: 'Prefers slightly alkaline soils' });
  }

  // Nitrogen check
  if (nitrogen < 150) {
    crops.push({ name: 'Legumes (e.g., Gram, Lentil)', reason: 'Fix nitrogen and suitable for low-N soils' });
  }

  // Moisture-driven suggestion
  if (moisture >= 50) {
    crops.push({ name: 'Paddy (Rice)', reason: 'Requires higher soil moisture (Kharif season)' });
  }

  // Temperature quick hint
  if (temperature >= 25 && temperature <= 32) {
    crops.push({ name: 'Maize (Sweet Corn)', reason: 'Performs well in warm temperatures' });
  }

  // Season hint
  if (season === 'kharif') {
    crops.push({ name: 'Sorghum', reason: 'Common Kharif crop' });
  } else if (season === 'rabi') {
    crops.push({ name: 'Mustard', reason: 'Common Rabi oilseed' });
  }

  // Deduplicate by name
  const unique = [];
  const seen = new Set();
  for (const c of crops) {
    if (!seen.has(c.name)) {
      seen.add(c.name);
      unique.push(c);
    }
  }

  return unique.slice(0, 5);
}

function parseNumber(input) {
  const v = Number(input);
  return Number.isFinite(v) ? v : NaN;
}

if (form) {
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const values = {
      district: form.querySelector('[data-id="district-select"]').value,
      area: parseNumber(form.querySelector('[data-id="area-input"]').value),
      ph: parseNumber(form.querySelector('[data-id="ph-input"]').value),
      nitrogen: parseNumber(form.querySelector('[data-id="nitrogen-input"]').value),
      phosphorus: parseNumber(form.querySelector('[data-id="phosphorus-input"]').value),
      potassium: parseNumber(form.querySelector('[data-id="potassium-input"]').value),
      moisture: parseNumber(form.querySelector('[data-id="moisture-input"]').value),
      temperature: parseNumber(form.querySelector('[data-id="temperature-input"]').value),
      season: form.querySelector('input[name="season"]:checked')?.value || ''
    };

    // Basic validation
    if (!values.district) {
      alert('Please select a district.');
      return;
    }

    const recs = recommendCrop(values);

    if (!recs || recs.length === 0) {
      resultsSection.innerHTML = '<div class="bg-white rounded-xl shadow-lg p-6">No recommendations available for the provided inputs.</div>';
      resultsSection.classList.remove('hidden');
      return;
    }

    let html = '<div class="mb-6"><h3 class="text-2xl font-bold text-gray-900">Recommended Crops</h3><p class="text-gray-600">Based on your inputs, these crops are suggested:</p></div>';
    for (const r of recs) {
      html += createResultCard(r.name, r.reason);
    }

    resultsSection.innerHTML = html;
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}
