let allJobs = [];
let currentPage = 1;
const PER_PAGE = 15;

const LOGO_COLORS = ['#0A66C2','#E7341A','#1DB954','#FF6900','#7B61FF','#00A4EF','#C0392B','#16A085'];

function logoColor(name) {
  let h = 0;
  for (let c of name) h = (h * 31 + c.charCodeAt(0)) & 0xFFFFFF;
  return LOGO_COLORS[Math.abs(h) % LOGO_COLORS.length];
}

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 3600)   return `${Math.floor(diff / 60)} min. ago`;
  if (diff < 86400)  return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}z ago`;
  return new Date(dateStr).toLocaleDateString('ro-RO');
}

function highlight(text, term) {
  if (!term) return text;
  const re = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(re, '<mark>$1</mark>');
}

// Salvare jobs
function getSaved() { return JSON.parse(localStorage.getItem('savedJobs') || '[]'); }
function toggleSave(url, btn) {
  let saved = getSaved();
  if (saved.includes(url)) {
    saved = saved.filter(u => u !== url);
    btn.textContent = 'Salveaza';
    btn.classList.remove('saved');
  } else {
    saved.push(url);
    btn.textContent = '✓ Salvat';
    btn.classList.add('saved');
  }
  localStorage.setItem('savedJobs', JSON.stringify(saved));
}
function isSaved(url) { return getSaved().includes(url); }

// Skeleton
function renderSkeletons(n = 5) {
  document.getElementById('jobsList').innerHTML = Array(n).fill(`
    <div class="skeleton">
      <div style="display:flex;gap:14px">
        <div class="skel-line" style="width:52px;height:52px;border-radius:6px;flex-shrink:0"></div>
        <div style="flex:1">
          <div class="skel-line" style="width:55%;height:17px;margin-bottom:8px"></div>
          <div class="skel-line" style="width:35%;height:13px;margin-bottom:8px"></div>
          <div class="skel-line" style="width:70%;height:12px"></div>
        </div>
      </div>
    </div>`).join('');
}

// Render jobs
function renderJobs(jobs, searchTerm = '') {
  const list  = document.getElementById('jobsList');
  const empty = document.getElementById('emptyState');
  const label = document.getElementById('resultsLabel');

  document.getElementById('totalCount').textContent = `${jobs.length} anunturi`;

  if (!jobs.length) {
    list.innerHTML = '';
    empty.style.display = 'block';
    label.textContent = 'Niciun anunt gasit';
    document.getElementById('pagination').innerHTML = '';
    return;
  }

  empty.style.display = 'none';

  const totalPages = Math.ceil(jobs.length / PER_PAGE);
  if (currentPage > totalPages) currentPage = 1;
  const paginated = jobs.slice((currentPage - 1) * PER_PAGE, currentPage * PER_PAGE);

  label.textContent = `${jobs.length} anunturi — pagina ${currentPage} din ${totalPages}`;

  list.innerHTML = paginated.map(job => {
    const initials = job.company.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
    const color    = logoColor(job.company);
    const saved    = isSaved(job.url);
    const tags     = (job.tags || []).map((t, i) =>
      `<span class="tag${i < 2 ? ' highlight' : ''}">${t}</span>`).join('');

    return `
    <div class="job-card" onclick="window.open('${job.url}','_blank')">
      <div class="card-top">
        <div class="company-logo" style="background:${color}">${initials}</div>
        <div class="card-info">
          <h2 title="${job.title}">${highlight(job.title, searchTerm)}</h2>
          <div class="company-name">${highlight(job.company, searchTerm)}</div>
          <div class="card-meta">
            <span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              ${job.location}
            </span>
            <span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2"/>
                <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
              </svg>
              Stagiatură
            </span>
          </div>
        </div>
        <div class="card-source">
          <span class="source-badge">${job.source}</span>
          <span class="date-posted">${timeAgo(job.posted_at)}</span>
        </div>
      </div>
      ${tags ? `<div class="card-tags">${tags}</div>` : ''}
      <div class="card-footer">
        <button class="btn-save${saved ? ' saved' : ''}"
          onclick="event.stopPropagation();toggleSave('${job.url}',this)">
          ${saved ? '✓ Salvat' : 'Salveaza'}
        </button>
        <a class="btn-apply" href="${job.url}" target="_blank"
          onclick="event.stopPropagation()">Aplica acum</a>
      </div>
    </div>`;
  }).join('');

  renderPagination(jobs.length, totalPages, searchTerm);
}

// Paginare
function renderPagination(total, totalPages, searchTerm) {
  const el = document.getElementById('pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }

  let html = `<div class="page-info">${(currentPage - 1) * PER_PAGE + 1}–${Math.min(currentPage * PER_PAGE, total)} din ${total}</div>`;
  html += '<div class="page-btns">';

  html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''}
    onclick="goPage(${currentPage - 1}, '${searchTerm}')">&#8592; Inapoi</button>`;

  const start = Math.max(1, currentPage - 2);
  const end   = Math.min(totalPages, currentPage + 2);

  if (start > 1) html += `<button class="page-btn" onclick="goPage(1,'${searchTerm}')">1</button>`;
  if (start > 2) html += `<span class="page-dots">…</span>`;

  for (let i = start; i <= end; i++) {
    html += `<button class="page-btn${i === currentPage ? ' active' : ''}"
      onclick="goPage(${i},'${searchTerm}')">${i}</button>`;
  }

  if (end < totalPages - 1) html += `<span class="page-dots">…</span>`;
  if (end < totalPages) html += `<button class="page-btn" onclick="goPage(${totalPages},'${searchTerm}')">${totalPages}</button>`;

  html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''}
    onclick="goPage(${currentPage + 1},'${searchTerm}')">Inainte &#8594;</button>`;

  html += '</div>';
  el.innerHTML = html;
}

function goPage(page, searchTerm) {
  currentPage = page;
  window.scrollTo({ top: 0, behavior: 'smooth' });
  applyFilters();
}

// Filtre
function applyFilters() {
  const search   = document.getElementById('searchInput').value.trim();
  const searchLo = search.toLowerCase();
  const domain   = document.getElementById('filterDomain').value;
  const location = document.getElementById('filterLocation').value;
  const sortBy   = document.getElementById('sortBy').value;
  const sources  = [...document.querySelectorAll('.checkbox-group input:checked')].map(el => el.value);

  const banner = document.getElementById('searchBanner');
  if (search) {
    banner.style.display = 'flex';
    document.getElementById('searchBannerText').textContent = search;
  } else {
    banner.style.display = 'none';
  }

  let filtered = allJobs.filter(j => {
    const text = `${j.title} ${j.company} ${(j.tags || []).join(' ')}`.toLowerCase();
    return (
      (!searchLo || text.includes(searchLo)) &&
      (!domain   || (j.tags || []).some(t => t.toLowerCase().includes(domain.toLowerCase()))) &&
      (!location || j.location.includes(location)) &&
      sources.includes(j.source)
    );
  });

  filtered.sort((a, b) => {
    if (sortBy === 'date')    return new Date(b.posted_at) - new Date(a.posted_at);
    if (sortBy === 'company') return a.company.localeCompare(b.company);
    if (sortBy === 'title')   return a.title.localeCompare(b.title);
    return 0;
  });

  renderJobs(filtered, search);
}

function resetFilters() {
  document.getElementById('searchInput').value = '';
  document.getElementById('filterDomain').value = '';
  document.getElementById('filterLocation').value = '';
  document.getElementById('sortBy').value = 'date';
  document.querySelectorAll('.checkbox-group input').forEach(el => el.checked = true);
  currentPage = 1;
  applyFilters();
}

// Stats
async function loadStats() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('statTotal').textContent     = data.total;
    document.getElementById('statToday').textContent     = data.today;
    document.getElementById('statCompanies').textContent = data.companies;
    document.getElementById('lastUpdate').textContent    = `Ultima actualizare: ${data.last_update}`;
  } catch (_) {}
}

// Load jobs
async function loadJobs() {
  renderSkeletons();
  document.getElementById('resultsLabel').textContent = 'Se incarca anunturile...';
  try {
    const res  = await fetch('/api/jobs');
    const data = await res.json();
    allJobs = data.jobs || [];
    currentPage = 1;
    applyFilters();
    loadStats();
  } catch (_) {
    document.getElementById('jobsList').innerHTML =
      '<div class="empty-state"><p>Eroare la incarcare. Incearca din nou.</p></div>';
  }
}

// Actualizeaza manual
async function triggerScrape() {
  document.getElementById('statTotal').textContent = '...';
  await fetch('/api/scrape', { method: 'POST' });
  setTimeout(loadJobs, 3000);
}

document.getElementById('searchInput').addEventListener('input', () => {
  currentPage = 1;
  applyFilters();
});

loadJobs();
