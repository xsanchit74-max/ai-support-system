/* ---------------------------------------------------------------
   script.js — Person 3's work (Frontend)
   Talks to the Flask backend (Person 2) which calls the AI engine
   (Person 1). No frameworks — plain fetch + DOM updates.
------------------------------------------------------------------ */

const API_BASE = "http://localhost:5000/api";

// ---------- index.html: complaint submission ----------

const form = document.getElementById("complaint-form");
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = document.getElementById("submit-btn");
    const errorMsg = document.getElementById("error-msg");
    errorMsg.style.display = "none";

    const payload = {
      customer: document.getElementById("customer").value.trim(),
      order_id: document.getElementById("order_id").value.trim(),
      text: document.getElementById("text").value.trim(),
    };

    if (!payload.text) return;

    btn.disabled = true;
    btn.textContent = "Analyzing...";

    try {
      const res = await fetch(`${API_BASE}/complaints`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error((await res.json()).error || "Request failed");
      const result = await res.json();
      renderResult(result);
    } catch (err) {
      errorMsg.textContent = `Couldn't reach the backend: ${err.message}. Is app.py running on port 5000?`;
      errorMsg.style.display = "block";
    } finally {
      btn.disabled = false;
      btn.textContent = "Analyze complaint";
    }
  });
}

function renderResult(result) {
  const card = document.getElementById("result-card");
  card.className = `result-card urgency-${result.urgency}`;
  card.style.display = "block";

  document.getElementById("r-category").innerHTML = `<span class="tag">${result.category}</span>`;
  document.getElementById("r-urgency").innerHTML = `<span class="tag urgency-${result.urgency}">${result.urgency}</span>`;
  document.getElementById("r-summary").textContent = result.summary;
  document.getElementById("r-department").innerHTML = `<span class="tag">${result.department}</span>`;
  document.getElementById("r-action").textContent = result.suggested_action;
  document.getElementById("r-reply").textContent = result.reply;

  card.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------- dashboard.html: table + charts ----------

async function initDashboard() {
  try {
    const [complaints, analytics] = await Promise.all([
      fetch(`${API_BASE}/complaints`).then((r) => r.json()),
      fetch(`${API_BASE}/analytics`).then((r) => r.json()),
    ]);
    renderStats(analytics);
    renderTable(complaints);
    renderBarChart("chart-category", analytics.by_category);
    renderBarChart("chart-urgency", analytics.by_urgency, {
      High: "var(--accent-high)",
      Medium: "var(--accent-medium)",
      Low: "var(--accent)",
    });
  } catch (err) {
    document.getElementById("table-wrap").innerHTML =
      `<div class="empty-state">Couldn't reach the backend at ${API_BASE}. Start it with "python app.py" and refresh.</div>`;
  }
}

function renderStats(analytics) {
  document.getElementById("stat-total").textContent = analytics.total;
  document.getElementById("stat-high").textContent = analytics.high_urgency;
  document.getElementById("stat-categories").textContent = Object.keys(analytics.by_category).length;
  document.getElementById("stat-departments").textContent = Object.keys(analytics.by_department).length;
}

function renderTable(complaints) {
  const tbody = document.getElementById("complaints-tbody");
  const emptyState = document.getElementById("empty-state");
  tbody.innerHTML = "";

  if (!complaints.length) {
    emptyState.style.display = "block";
    return;
  }
  emptyState.style.display = "none";

  for (const c of complaints) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="id">#${c.id}</td>
      <td>${escapeHtml(c.customer)}</td>
      <td class="summary">${escapeHtml(c.summary)}</td>
      <td><span class="tag">${c.category}</span></td>
      <td><span class="tag urgency-${c.urgency}">${c.urgency}</span></td>
      <td class="dept">${c.department}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderBarChart(containerId, counts, colorMap) {
  const el = document.getElementById(containerId);
  el.innerHTML = "";
  const entries = Object.entries(counts);
  if (!entries.length) {
    el.innerHTML = `<div class="empty-state">No data yet.</div>`;
    return;
  }
  const max = Math.max(...entries.map(([, v]) => v));

  for (const [label, count] of entries) {
    const pct = max ? Math.round((count / max) * 100) : 0;
    const color = colorMap && colorMap[label] ? colorMap[label] : "var(--accent)";
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-label">${label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%; background:${color};"></div></div>
      <div class="bar-count">${count}</div>
    `;
    el.appendChild(row);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
