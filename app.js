const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const submitBtn = document.getElementById('calculate-btn');
const uploadStatus = document.getElementById('upload-status');
const sourceUrlWrap = document.getElementById('source-url-wrap');
const sourceUrlEl = document.getElementById('source-url');
// Configurable API base for static hosting: prefer window.API_BASE if provided
const API_BASE = (typeof window !== 'undefined' && window.API_BASE)
  ? window.API_BASE
  : ((location.port === '8080') ? 'http://localhost:5053' : '');
// CBAM-oriented result elements
const fiOrigin = document.getElementById('fi-origin');
const fiDestination = document.getElementById('fi-destination');
const fiMode = document.getElementById('fi-mode');
const fiWeight = document.getElementById('fi-weight');
const fiHscode = document.getElementById('fi-hscode');
const fiProduct = document.getElementById('fi-product');

const cbamResult = document.getElementById('cbam-result');
const cbamExplain = document.getElementById('cbam-explain');

const cbamCategory = document.getElementById('cbam-category');
const cbamSubtype = document.getElementById('cbam-subtype');
const cbamEmissionFactor = document.getElementById('cbam-emission-factor');
const cbamWeightTon = document.getElementById('cbam-weight-ton');
const cbamEmbeddedEmission = document.getElementById('cbam-embedded-emission');
const cbamFee = document.getElementById('cbam-fee');
const cbamFormula = document.getElementById('cbam-formula');
const cbamSuggestions = document.getElementById('cbam-suggestions');
const cbamBestOption = document.getElementById('cbam-best-option');

function setText(el, text) { if (el) el.textContent = text; }
function setHTML(el, html) { if (el) el.innerHTML = html; }
function fmt(n) { if (n === null || n === undefined || Number.isNaN(n)) return '—';
  if (typeof n === 'number') return n.toLocaleString(undefined, { maximumFractionDigits: 2 });
  return String(n); }
function pct(n) { if (n === null || n === undefined) return '—';
  const v = typeof n === 'string' && n.endsWith('%') ? n : `${fmt(n)}%`; return v; }

function isURL(v) {
  try { const u = new URL(v); return !!u.protocol && !!u.host; } catch { return false; }
}

function clearResults() {
  [fiOrigin, fiDestination, fiMode, fiWeight, fiHscode, fiProduct,
   cbamResult, cbamExplain,
   cbamCategory, cbamSubtype, cbamEmissionFactor, cbamWeightTon, cbamEmbeddedEmission, cbamFee, cbamFormula, cbamBestOption]
   .forEach(el => setText(el, '—'));
  if (cbamSuggestions) cbamSuggestions.innerHTML = '';
}

function getPayload(data) {
  // Try common locations
  const candidates = [data?.data?.outputs, data?.outputs, data?.data, data];

  function hasSignature(obj) {
    if (!obj || typeof obj !== 'object') return false;
    const keys = Object.keys(obj);
    return (
      (keys.includes('file_info') && keys.includes('cbam_applicability') && keys.includes('cbam_detail'))
    );
  }

  function tryParseJSON(val) {
    if (typeof val === 'string') {
      try { return JSON.parse(val); } catch { return null; }
    }
    return null;
  }

  // First pass: direct candidates
  for (const c of candidates) {
    if (!c) continue;
    if (hasSignature(c)) return c;
    const parsed = tryParseJSON(c);
    if (parsed && hasSignature(parsed)) return parsed;
  }

  // Second pass: look inside objects for a nested structured result
  for (const c of candidates) {
    if (!c || typeof c !== 'object') continue;
    for (const v of Object.values(c)) {
      if (!v) continue;
      const parsed = tryParseJSON(v) || v;
      if (hasSignature(parsed)) return parsed;
      if (parsed && typeof parsed === 'object') {
        // one more shallow level
        for (const vv of Object.values(parsed)) {
          const p2 = tryParseJSON(vv) || vv;
          if (hasSignature(p2)) return p2;
        }
      }
    }
  }

  // Fallback: return first non-null candidate
  for (const c of candidates) { if (c) return c; }
  return {};
}

function renderFileInfo(info) {
  if (!info) return;
  const origin = [info.origin_city, info.origin_country].filter(Boolean).join(', ');
  const dest = [info.destination_city, info.destination_country].filter(Boolean).join(', ');
  setText(fiOrigin, origin || '—');
  setText(fiDestination, dest || '—');
  setText(fiMode, info.transport_mode ?? '—');
  setText(fiWeight, fmt(info.weight_kg));
  setText(fiHscode, info.hs_code ?? '—');
  setText(fiProduct, info.product ?? '—');
}

function renderApplicability(app) {
  if (!app) return;
  setText(cbamResult, app.result ?? '—');
  setText(cbamExplain, app.explain ?? '—');
}

function renderCbamDetail(detail) {
  if (!detail) return;
  setText(cbamCategory, detail.category ?? '—');
  setText(cbamSubtype, detail.subtype ?? '—');
  setText(cbamEmissionFactor, fmt(detail.emission_factor_tCO2e_per_ton));
  setText(cbamWeightTon, fmt(detail.weight_ton));
  setText(cbamEmbeddedEmission, fmt(detail.embedded_emission_tCO2e));
  setText(cbamFee, fmt(detail.cbam_fee_eur));
  setText(cbamFormula, detail.formula ?? '—');
  // suggestions
  cbamSuggestions.innerHTML = '';
  if (Array.isArray(detail.suggestions) && detail.suggestions.length > 0) {
    detail.suggestions.forEach(s => {
      const div = document.createElement('div');
      div.className = 'suggestion';
      div.textContent = s;
      cbamSuggestions.appendChild(div);
    });
  } else {
    cbamSuggestions.textContent = '—';
  }
  // best option
  cbamBestOption.textContent = detail.best_option ?? '—';
  if (detail.best_option) cbamBestOption.classList.add('best-option'); else cbamBestOption.classList.remove('best-option');
}

function renderCbamSections(payload) {
  renderFileInfo(payload.file_info);
  renderApplicability(payload.cbam_applicability);
  renderCbamDetail(payload.cbam_detail);
}

async function runWorkflow(src, user = 'demo-user') {
  if (!src) { alert('Missing source URL'); return; }
  uploadStatus.textContent = 'Running workflow...';
  clearResults();

  try {
    const res = await fetch(`${API_BASE}/api/workflow`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_url: src, user })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.error || res.statusText);
    uploadStatus.textContent = 'Workflow completed.';
    console.log('[workflow response]', data);
    const payload = getPayload(data);
    if (!payload || typeof payload !== 'object') {
      uploadStatus.textContent = 'Workflow completed, but no structured data found.';
    }
    renderCbamSections(payload);
  } catch (err) {
    uploadStatus.textContent = 'Workflow error: ' + err.message;
  }
}

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!fileInput.files || fileInput.files.length === 0) { alert('Please select a file to upload'); return; }
  const file = fileInput.files[0];

  uploadStatus.textContent = 'Uploading to Dify...';
  sourceUrlWrap.classList.add('hidden');
  sourceUrlEl.textContent = '';
  clearResults();
  if (submitBtn) { submitBtn.disabled = true; submitBtn.classList.add('loading'); }

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data?.error || res.statusText);
    const src = data?.source_url || data?.data?.source_url;
    uploadStatus.textContent = 'Upload succeeded.';
    if (src) {
      // Giữ Source URL ẩn theo yêu cầu
      sourceUrlEl.textContent = src;
      sourceUrlEl.href = src;
      // không còn input URL, tự chạy workflow luôn
      // Tự động chạy workflow ngay sau khi upload
      await runWorkflow(src, 'demo-user');
    } else {
      sourceUrlWrap.classList.add('hidden');
    }
  } catch (err) {
    uploadStatus.textContent = 'Upload failed: ' + err.message;
  } finally {
    if (submitBtn) { submitBtn.disabled = false; submitBtn.classList.remove('loading'); }
  }
});

// Đã xóa nút Run Workflow và input URL, workflow chạy tự động sau upload