// ── CONFIGURAÇÕES DE CONEXÃO ──────────────────
var baseUrl = "http://192.168.43.100";
let running = false;
let readings = [];
let topSpeed = 0;
let startTime = null;
let uptimeInt = null;
let pollInterval = null; 

// ── ELEMENTOS DA UI ───────────────────────────
const startBtn = document.getElementById('startButton');
const stopBtn = document.getElementById('stopButton');
const clearBtn = document.getElementById('clearBtn');
const tbody = document.getElementById('historyTableBody');
const connDot = document.getElementById('connDot');
const connLabel = document.getElementById('connLabel');
const gaugeFill = document.getElementById('gaugeFill');
const gaugeText = document.getElementById('gaugeText');

// ── LÓGICA DE CONEXÃO (CHECKER) ───────────────
async function verificarConexao() {

    try {

        const controller = new AbortController();

        const timeoutId = setTimeout(() => controller.abort(), 3000);

        const resp = await fetch(`${baseUrl}/`, {
            method: 'GET',
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (resp.ok) {

            connDot.classList.add('active');
            connLabel.textContent = 'Online';
            connLabel.style.color = '#00ff00';

            return true;
        }

    } catch (err) {

        connDot.classList.remove('active');
        connLabel.textContent = 'Offline';
        connLabel.style.color = 'rgba(255,255,255,0.5)';

        return false;
    }
}

setInterval(verificarConexao, 5000);

function mudarIP() {

    let inputUrl = document.getElementById('ipInput').value.trim();

    if (!inputUrl.startsWith('http')) {
        baseUrl = "http://" + inputUrl;
    } else {
        baseUrl = inputUrl;
    }

    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }

    console.log("Tentando conectar em:", baseUrl);

    verificarConexao();
}

// ── COMUNICAÇÃO COM O ESP32 ───────────────────
async function dispararAcao(rota) {

    try {

        const resposta = await fetch(`${baseUrl}${rota}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                timestamp: Date.now()
            })
        });

        return resposta.ok;

    } catch (erro) {

        console.error(`Erro na rota ${rota}:`, erro);

        return false;
    }
}

async function buscarDadosDoESP() {

    try {

        const resposta = await fetch(`${baseUrl}/historico`, {
            method: 'GET'
        });

        if (resposta.ok) {

            const dados = await resposta.json();

            if (Array.isArray(dados) && dados.length > readings.length) {

                const novaVelocidade = dados[dados.length - 1];

                addReading(parseFloat(novaVelocidade));
            }
        }

    } catch (erro) {

        console.error("Erro ao buscar histórico:", erro);
    }
}

// ── LÓGICA DO DASHBOARD (UI) ──────────────────
function updateGauge(speed, max = 80) {

    const pct = Math.min(speed / max, 1);

    const offset = (157 * (1 - pct)).toFixed(1);

    gaugeFill.setAttribute('stroke-dashoffset', offset);

    if (pct < 0.5) {
        gaugeFill.setAttribute('stroke', '#009DDC');
    } else if (pct < 0.8) {
        gaugeFill.setAttribute('stroke', '#FF7F11');
    } else {
        gaugeFill.setAttribute('stroke', '#FF1B1C');
    }

    gaugeText.textContent = speed.toFixed(1);
}

function updateUI() {

    const cur = readings.length
        ? readings[readings.length - 1].speed
        : null;

    document.getElementById('currentSpeed').innerHTML =
        cur !== null
            ? `${cur.toFixed(1)}<span class="unit">km/h</span>`
            : `—<span class="unit">km/h</span>`;

    document.getElementById('topSpeed').innerHTML =
        topSpeed > 0
            ? `${topSpeed.toFixed(1)}<span class="unit">km/h</span>`
            : `—<span class="unit">km/h</span>`;

    document.getElementById('lapCount').innerHTML =
        `${readings.length}<span class="unit">total</span>`;

    document.getElementById('countBadge').textContent =
        `${readings.length} leituras`;

    document.getElementById('tickCurrent').textContent =
        cur !== null
            ? `${cur.toFixed(1)} km/h`
            : '— km/h';

    document.getElementById('tickPeak').textContent =
        topSpeed > 0
            ? `${topSpeed.toFixed(1)} km/h`
            : '— km/h';

    document.getElementById('tickLaps').textContent =
        readings.length;
}

function addReading(speed) {

    const now = new Date();

    const timeStr = now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });

    const prev = readings.length
        ? readings[readings.length - 1].speed
        : null;

    const diff = prev !== null
        ? speed - prev
        : null;

    readings.push({
        speed,
        time: timeStr
    });

    if (speed > topSpeed) {
        topSpeed = speed;
    }

    const placeholder = tbody.querySelector('td[colspan]');

    if (placeholder) {
        tbody.innerHTML = '';
    }

    const tr = document.createElement('tr');

    const deltaColor =
        diff === null
            ? 'rgba(255,255,255,0.3)'
            : diff >= 0
                ? '#FF7F11'
                : '#009DDC';

    const deltaStr =
        diff !== null
            ? (diff >= 0
                ? `+${diff.toFixed(1)}`
                : diff.toFixed(1))
            : '—';

    tr.innerHTML = `
        <td style="color:rgba(255,255,255,0.3);font-size:0.78rem;">
            ${readings.length}
        </td>

        <td>${timeStr}</td>

        <td class="speed-cell">
            ${speed.toFixed(1)} km/h
        </td>

        <td style="color:${deltaColor};font-weight:700;">
            ${deltaStr}
        </td>

        <td>
            <span class="status-pill ${speed > 60 ? 'pill-record' : 'pill-pass'}">
                ${speed > 60 ? 'Recorde' : 'Pass'}
            </span>
        </td>
    `;

    tbody.insertBefore(tr, tbody.firstChild);

    updateGauge(speed);

    updateUI();
}

// ── EVENTOS DOS BOTÕES ────────────────────────
startBtn.addEventListener('click', async () => {

    const sucesso = await dispararAcao('/lancar');

    if (sucesso) {

        running = !running;

        if (running) {

            startBtn.textContent = 'Parar';

            startBtn.classList.add('running');

            if (!startTime) {
                startTime = Date.now();
            }

            pollInterval = setInterval(buscarDadosDoESP, 1000);

            if (!uptimeInt) {

                uptimeInt = setInterval(() => {

                    const elapsed =
                        Math.floor((Date.now() - startTime) / 1000);

                    const m = Math.floor(elapsed / 60);

                    const s = elapsed % 60;

                    document.getElementById('tickTime').textContent =
                        `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;

                }, 1000);
            }

        } else {

            paraMonitoramento();
        }

    } else {

        alert("Erro: ESP32 não respondeu ao comando /lancar");
    }
});

function paraMonitoramento() {

    startBtn.textContent = 'Iniciar';

    startBtn.classList.remove('running');

    clearInterval(pollInterval);

    pollInterval = null;

    running = false;
}

stopBtn.addEventListener('click', async () => {

    const sucesso = await dispararAcao('/buzinar');

    if (sucesso) {

        stopBtn.style.background = '#FF1B1C';

        setTimeout(() => {
            stopBtn.style.background = '';
        }, 600);

        const now = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td colspan="2">—</td>
            <td>${now}</td>
            <td>—</td>
            <td>
                <span class="status-pill pill-stop">
                    Buzina
                </span>
            </td>
        `;

        tbody.insertBefore(tr, tbody.firstChild);
    }
});

clearBtn.addEventListener('click', () => {

    readings = [];

    topSpeed = 0;

    startTime = null;

    paraMonitoramento();

    clearInterval(uptimeInt);

    uptimeInt = null;

    tbody.innerHTML =
        '<tr><td colspan="5" class="empty-state">Não há leituras ainda.</td></tr>';

    updateGauge(0);

    updateUI();

    document.getElementById('tickTime').textContent = '00:00';
});

// ── INPUT MASK ────────────────────────────────
document.getElementById('ipInput').addEventListener('input', function(e) {

    let v = this.value;

    if (!v.toLowerCase().startsWith('h')) {

        v = v.replace(/[^\d.]/g, '');

        let blocos = v.split('.');

        if (blocos.length > 4) {
            blocos = blocos.slice(0, 4);
        }

        for (let i = 0; i < blocos.length; i++) {

            if (blocos[i].length > 3) {
                blocos[i] = blocos[i].substring(0, 3);
            }
        }

        v = blocos.join('.');
    }

    this.value = v;
});
