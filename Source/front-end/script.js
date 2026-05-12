let running     = false;
let readings    = [];
let topSpeed    = 0;
let simInterval = null;
let startTime   = null;
let uptimeInt   = null;
 
const startBtn  = document.getElementById('startButton');
const stopBtn   = document.getElementById('stopButton');
const clearBtn  = document.getElementById('clearBtn');
const tbody     = document.getElementById('historyTableBody');
const connDot   = document.getElementById('connDot');
const connLabel = document.getElementById('connLabel');
const gaugeFill = document.getElementById('gaugeFill');
const gaugeText = document.getElementById('gaugeText');
 
// ── Gauge ────────────────────────────────────
function updateGauge(speed, max = 80) {
  const pct    = Math.min(speed / max, 1);
  const offset = (157 * (1 - pct)).toFixed(1);
 
  gaugeFill.setAttribute('stroke-dashoffset', offset);
 
  if      (pct < 0.5) gaugeFill.setAttribute('stroke', '#009DDC'); // light-blue
  else if (pct < 0.8) gaugeFill.setAttribute('stroke', '#FF7F11'); // orange
  else                gaugeFill.setAttribute('stroke', '#FF1B1C'); // red
 
  gaugeText.textContent = speed.toFixed(1);
}
 
// ── Ticker / stat cards ───────────────────────
function updateUI() {
  const cur = readings.length ? readings[readings.length - 1].speed : null;
 
  document.getElementById('currentSpeed').innerHTML =
    cur !== null ? `${cur.toFixed(1)}<span class="unit">km/h</span>` : `—<span class="unit">km/h</span>`;
 
  document.getElementById('topSpeed').innerHTML =
    topSpeed > 0 ? `${topSpeed.toFixed(1)}<span class="unit">km/h</span>` : `—<span class="unit">km/h</span>`;
 
  document.getElementById('lapCount').innerHTML =
    `${readings.length}<span class="unit">total</span>`;
 
  document.getElementById('countBadge').textContent = `${readings.length} leituras`;
  document.getElementById('tickCurrent').textContent = cur !== null ? `${cur.toFixed(1)} km/h` : '— km/h';
  document.getElementById('tickPeak').textContent    = topSpeed > 0  ? `${topSpeed.toFixed(1)} km/h` : '— km/h';
  document.getElementById('tickLaps').textContent    = readings.length;
}
 
// ── Status pill ───────────────────────────────
function getStatusPill(speed, prev) {
  if (speed > 60)                        return '<span class="status-pill pill-record">Recorde</span>';
  if (prev !== null && speed > prev * 1.1) return '<span class="status-pill pill-fast">Rápido</span>';
  return '<span class="status-pill pill-pass">Pass</span>';
}
 
// ── Add reading row ───────────────────────────
function addReading(speed) {
  const now     = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const prev    = readings.length ? readings[readings.length - 1].speed : null;
  const diff    = prev !== null ? speed - prev : null;
  const deltaStr = diff !== null ? (diff >= 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1)) : '—';
  const deltaColor = diff === null ? 'rgba(255,255,255,0.3)' : diff >= 0 ? '#FF7F11' : '#009DDC';
 
  readings.push({ speed, time: timeStr });
  if (speed > topSpeed) topSpeed = speed;
 
  // Remove empty-state row
  const placeholder = tbody.querySelector('td[colspan]');
  if (placeholder) tbody.innerHTML = '';
 
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td style="color:rgba(255,255,255,0.3);font-size:0.78rem;">${readings.length}</td>
    <td>${timeStr}</td>
    <td class="speed-cell">${speed.toFixed(1)} km/h</td>
    <td style="color:${deltaColor};font-family:'Barlow Condensed',sans-serif;font-weight:700;">${deltaStr}</td>
    <td>${getStatusPill(speed, prev)}</td>
  `;
 
  tbody.insertBefore(tr, tbody.firstChild); // newest on top
  updateGauge(speed);
  updateUI();
}
 
// ── Demo: simulate sensor readings ───────────
function simSpeed() {
  const speed = Math.round((20 + Math.random() * 55) * 10) / 10;
  addReading(speed);
}
 
// ── Start / Stop ──────────────────────────────
startBtn.addEventListener('click', () => {
  running = !running;
 
  if (running) {
    startBtn.textContent = 'Parar';
    startBtn.classList.add('running');
    connDot.classList.add('active');
    connLabel.textContent = 'Online';
 
    if (!startTime) startTime = Date.now();
 
    // ── Replace setInterval below with your ESP32 fetch/WebSocket ──
    simInterval = setInterval(simSpeed, 1800 + Math.random() * 600);
 
    // Uptime counter
    if (!uptimeInt) {
      uptimeInt = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const m = Math.floor(elapsed / 60);
        const s = elapsed % 60;
        document.getElementById('tickTime').textContent =
          `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
      }, 1000);
    }
  } else {
    startBtn.textContent = 'Iniciar';
    startBtn.classList.remove('running');
    connDot.classList.remove('active');
    connLabel.textContent = 'Paused';
    clearInterval(simInterval);
    simInterval = null;
  }
});
 
// ── Buzzer ────────────────────────────────────
stopBtn.addEventListener('click', () => {
  // Flash button red
  stopBtn.style.background   = '#FF1B1C';
  stopBtn.style.color        = '#fff';
  stopBtn.style.borderColor  = '#FF1B1C';
  setTimeout(() => {
    stopBtn.style.background  = '';
    stopBtn.style.color       = '#009DDC';
    stopBtn.style.borderColor = '#009DDC';
  }, 600);
 
  // Log buzzer event in table
  const placeholder = tbody.querySelector('td[colspan]');
  if (placeholder) tbody.innerHTML = '';
 
  const now     = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const tr      = document.createElement('tr');
  tr.innerHTML  = `
    <td style="color:rgba(255,255,255,0.3);font-size:0.78rem;">—</td>
    <td>${now}</td>
    <td class="speed-cell">—</td>
    <td>—</td>
    <td><span class="status-pill pill-stop">Buzina</span></td>
  `;
  tbody.insertBefore(tr, tbody.firstChild);
});
 
// ── Clear ─────────────────────────────────────
clearBtn.addEventListener('click', () => {
  readings  = [];
  topSpeed  = 0;
  startTime = null;
 
  clearInterval(simInterval);
  clearInterval(uptimeInt);
  simInterval = null;
  uptimeInt   = null;
 
  if (running) {
    running = false;
    startBtn.textContent = 'Start';
    startBtn.classList.remove('running');
    connDot.classList.remove('active');
    connLabel.textContent = 'Offline';
  }
 
  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Não há leituras ainda. Clique em Início para começar.</td></tr>';
 
  updateGauge(0);
  gaugeText.textContent = '0';
  gaugeFill.setAttribute('stroke-dashoffset', '157');
 
  document.getElementById('currentSpeed').innerHTML = '—<span class="unit">km/h</span>';
  document.getElementById('topSpeed').innerHTML     = '—<span class="unit">km/h</span>';
  document.getElementById('lapCount').innerHTML     = '0<span class="unit">total</span>';
  document.getElementById('countBadge').textContent = '0 readings';
  document.getElementById('tickCurrent').textContent = '— km/h';
  document.getElementById('tickPeak').textContent    = '— km/h';
  document.getElementById('tickLaps').textContent    = '0';
  document.getElementById('tickTime').textContent    = '00:00';
});

document.getElementById('ipInput').addEventListener('input', function(e) {
  let v = this.value;
  
  // 1. Remove qualquer caractere que não seja número ou ponto
  v = v.replace(/[^\d.]/g, '');
  
  let blocos = v.split('.');
  
  // 2. Limita a no máximo 4 blocos de números (ex: 192.168.1.100)
  if (blocos.length > 4) {
    blocos = blocos.slice(0, 4);
  }
  
  // 3. Garante que nenhum bloco tenha mais de 3 números
  for (let i = 0; i < blocos.length; i++) {
    if (blocos[i].length > 3) {
      blocos[i] = blocos[i].substring(0, 3);
    }
  }
  
  v = blocos.join('.');
  
  // 4. Adiciona o ponto automaticamente ao atingir 3 dígitos (se não estiver apagando)
  if (e.inputType !== 'deleteContentBackward') {
    let ultimoBloco = blocos[blocos.length - 1];
    if (ultimoBloco.length === 3 && blocos.length < 4) {
      v += '.';
    }
  }
  
  this.value = v;
});