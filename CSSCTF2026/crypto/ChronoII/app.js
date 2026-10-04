const $ = (selector) => document.querySelector(selector);
let paused = false;
let capture = null;
let lastTimestamp = null;
let liveEpoch = null;
let liveStarted = 0;
let timer;
let generation = 0;

for (let i = 0; i < 60; i++) {
  const tick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  const major = i % 5 === 0;
  tick.setAttribute('x1', '150'); tick.setAttribute('x2', '150');
  tick.setAttribute('y1', '15'); tick.setAttribute('y2', major ? '27' : '21');
  tick.setAttribute('transform', `rotate(${i * 6} 150 150)`);
  tick.setAttribute('class', major ? 'tick major' : 'tick');
  $('#tick-marks').append(tick);
}

function setClock(epoch) {
  const date = new Date(epoch);
  const seconds = date.getUTCSeconds() + date.getUTCMilliseconds() / 1000;
  const minutes = date.getUTCMinutes() + seconds / 60;
  const hours = date.getUTCHours() % 12 + minutes / 60;
  $('#second-hand').setAttribute('transform', `rotate(${seconds * 6} 150 150)`);
  $('#minute-hand').setAttribute('transform', `rotate(${minutes * 6} 150 150)`);
  $('#hour-hand').setAttribute('transform', `rotate(${hours * 30} 150 150)`);
  $('#clock-time').textContent = date.toISOString().slice(11, 19);
  $('#clock-date').textContent = date.toISOString().slice(0, 10);
}

function animate() {
  if (liveEpoch !== null && !paused) {
    // Interpolate only within the current tick; a failed feed never fabricates time.
    setClock(liveEpoch + Math.min(performance.now() - liveStarted, 999));
  }
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

function render(data) {
  const log = $('#log');
  const previousScroll = log.scrollTop;
  const fragment = document.createDocumentFragment();
  for (const record of [...data].reverse()) {
    const row = document.createElement('div'); row.className = 'log-row';
    const time = document.createElement('time'); time.dateTime = record.timestamp;
    time.append(record.timestamp.slice(11, 19));
    const date = document.createElement('small'); date.textContent = record.timestamp.slice(0, 10); time.append(date);
    const code = document.createElement('code'); code.textContent = record.ciphertext;
    row.append(time, code); fragment.append(row);
  }
  log.replaceChildren(fragment);
  log.scrollTop = previousScroll;
  $('#log-status').textContent = `${data.length} records / 60 consecutive seconds`;
}

async function poll() {
  clearTimeout(timer);
  if (paused) return;
  const requestGeneration = generation;
  try {
    const response = await fetch('/api/feed', {cache: 'no-store'});
    if (!response.ok) throw new Error('Receiver unavailable');
    const data = await response.json();
    if (paused || requestGeneration !== generation) return;
    capture = data;
    const timestamp = data.at(-1).timestamp;
    if (timestamp !== lastTimestamp) {
      lastTimestamp = timestamp;
      liveEpoch = Date.parse(timestamp); liveStarted = performance.now();
      render(data);
    }
    $('#connection').textContent = 'SIGNAL LIVE';
  } catch (error) {
    if (paused || requestGeneration !== generation) return;
    $('#connection').textContent = 'RECONNECTING';
    $('#log-status').textContent = 'Signal lost. Retrying; saved evidence remains available.';
  } finally {
    if (!paused && requestGeneration === generation) timer = setTimeout(poll, 1000);
  }
}

$('#pause').addEventListener('click', () => {
  paused = !paused;
  generation += 1;
  document.body.classList.toggle('paused', paused);
  $('#pause').textContent = paused ? 'Resume display' : 'Pause display';
  $('#pause').setAttribute('aria-pressed', String(paused));
  $('#connection').textContent = paused ? 'DISPLAY PAUSED' : 'CONNECTING';
  if (paused) clearTimeout(timer); else poll();
});

$('#download').addEventListener('click', (event) => {
  if (!capture) return;
  event.preventDefault();
  const blob = new Blob([JSON.stringify(capture, null, 2) + '\n'], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a'); anchor.href = url; anchor.download = 'chrono-ii-capture.json';
  anchor.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
});

poll();
