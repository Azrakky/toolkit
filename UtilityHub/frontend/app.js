const buttons = document.querySelectorAll('nav button');
const pages = document.querySelectorAll('.page');
buttons.forEach(button => button.addEventListener('click', () => {
  buttons.forEach(b => b.classList.toggle('active', b === button));
  pages.forEach(page => page.classList.toggle('hidden', page.id !== button.dataset.page));
}));
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json' } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}
async function initialize() {
  const status = document.querySelector('.status');
  try {
    const health = await api('/api/health');
    status.textContent = health.ok ? '● Python backend connected' : '● Backend unavailable';
    const { gadgets } = await api('/api/gadgets');
    const list = document.getElementById('gadget-list');
    list.replaceChildren();
    for (const gadget of gadgets) {
      const article = document.createElement('article');
      const heading = document.createElement('h3'); heading.textContent = gadget.name;
      const description = document.createElement('p'); description.textContent = gadget.description;
      const tag = document.createElement('span'); tag.className = 'tag'; tag.textContent = gadget.status;
      article.append(heading, description, tag);
      if (gadget.id === 'connection-test') {
        const button = document.createElement('button');
        button.textContent = 'Run backend test';
        button.addEventListener('click', async () => {
          const result = document.getElementById('gadget-result');
          try { result.textContent = (await api('/api/gadgets/connection-test', { method: 'POST', body: '{}' })).message; }
          catch (error) { result.textContent = 'Test failed: ' + error.message; }
        });
        article.append(button);
      }
      if (gadget.id === 'video-converter') {
        const button = document.createElement('button');
        button.textContent = 'Open Video Converter';
        button.addEventListener('click', () => {
          document.getElementById('converter-panel').classList.remove('hidden');
          document.getElementById('converter-panel').scrollIntoView({ behavior: 'smooth' });
          checkDependencies();
        });
        article.append(button);
      }
      list.append(article);
    }
    document.getElementById('gadget-result').textContent = 'Choose “Run backend test” to verify the gadget framework.';
    const settings = await api('/api/settings');
    document.getElementById('display-name').value = settings.display_name;
    document.getElementById('download-folder').value = settings.download_folder;
  } catch (error) {
    status.textContent = '● Backend disconnected';
    document.getElementById('gadget-result').textContent = 'Backend error: ' + error.message;
  }
}
document.getElementById('settings-form').addEventListener('submit', async event => {
  event.preventDefault();
  const result = document.getElementById('settings-result');
  try {
    await api('/api/settings', { method: 'POST', body: JSON.stringify({
      display_name: document.getElementById('display-name').value,
      download_folder: document.getElementById('download-folder').value
    }) });
    result.textContent = 'Settings saved successfully.';
  } catch (error) { result.textContent = 'Save failed: ' + error.message; }
});
initialize();

async function checkDependencies() {
  const result = document.getElementById('dependency-result');
  try {
    const deps = await api('/api/converter/dependencies');
    result.textContent = `yt-dlp: ${deps.yt_dlp ? 'Ready' : 'Not installed'} | FFmpeg: ${deps.ffmpeg ? 'Ready' : 'Not installed'}`;
    if (!deps.yt_dlp || !deps.ffmpeg) result.textContent += ' — See README.txt for setup instructions.';
  } catch (error) { result.textContent = 'Dependency check failed: ' + error.message; }
}
document.getElementById('video-format').addEventListener('change', event => {
  document.getElementById('video-quality').disabled = event.target.value === 'mp3';
});
let polling = null;
document.getElementById('converter-form').addEventListener('submit', async event => {
  event.preventDefault();
  const result = document.getElementById('conversion-result');
  const button = document.getElementById('convert-button');
  const progress = document.getElementById('conversion-progress');
  if (polling) clearInterval(polling);
  button.disabled = true;
  progress.style.width = '0%';
  result.textContent = 'Starting…';
  try {
    const job = await api('/api/converter/start', {method:'POST', body: JSON.stringify({
      url: document.getElementById('video-url').value.trim(),
      format: document.getElementById('video-format').value,
      quality: document.getElementById('video-quality').value
    })});
    async function refresh() {
      try {
        const state = await api('/api/converter/jobs/' + job.id);
        progress.style.width = state.progress + '%';
        result.textContent = state.message + (state.file ? ' | File: ' + state.file : '');
        if (state.status === 'complete' || state.status === 'failed') {
          clearInterval(polling); polling = null; button.disabled = false;
        }
      } catch (error) {
        clearInterval(polling); polling = null; button.disabled = false;
        result.textContent = 'Could not check progress: ' + error.message;
      }
    }
    await refresh();
    if (button.disabled) polling = setInterval(refresh, 1000);
  } catch (error) { result.textContent = error.message; button.disabled = false; }
});

// Payment Plan Generator gadget (client-side, no backend changes required).
(() => {
  const list = document.getElementById('gadget-list');
  if (!list || document.getElementById('payment-plan-gadget-card')) return;
  const article = document.createElement('article');
  article.id = 'payment-plan-gadget-card';
  const title = document.createElement('h3');
  title.textContent = 'Payment Plan Agreement Generator';
  const description = document.createElement('p');
  description.textContent = 'Create an installment schedule and print a resident payment agreement as PDF.';
  const tag = document.createElement('span');
  tag.className = 'tag';
  tag.textContent = 'ready';
  const button = document.createElement('button');
  button.textContent = 'Open Payment Plan Generator';
  button.addEventListener('click', () => window.open('/gadgets/payment-plan.html', '_blank', 'noopener'));
  article.append(title, description, tag, button);
  // initialize() fetches gadgets asynchronously and clears the list.
  // Wait for its request to finish before inserting our standalone card.
  const observer = new MutationObserver(() => {
    if (!list.contains(article)) list.append(article);
  });
  observer.observe(list, {childList: true});
  list.append(article);
})();
