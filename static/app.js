async function loadQueue() {
  const table = document.getElementById("queueBody");
  if (!table) return; // IMPORTANT: page-safe

  const res = await fetch("/patients");
  const data = await res.json();

  table.innerHTML = "";
  data.patients.forEach(p => {
    table.innerHTML += `
      <tr>
        <td>${p.name}</td>
        <td>${p.urgency}</td>
        <td>${p.wait_minutes}</td>
        <td>
          <span class="badge ${p.sla_breached ? "high" : "ok"}">
            ${p.sla_breached ? "SLA BREACH" : "OK"}
          </span>
        </td>
        <td>${p.priority_score}</td>
      </tr>
    `;
  });
}

async function loadDashboard() {
  const total = document.getElementById("totalPatients");
  if (!total) return;

  const res = await fetch("/dashboard");
  const d = await res.json();

  total.innerText = d.total;
  document.getElementById("slaBreaches").innerText = d.sla_breaches;
  document.getElementById("avgWait").innerText = d.avg_wait;
}

async function loadDoctorStats() {
  const el = document.getElementById("availableDoctors");
  if (!el) return;

  const res = await fetch("/dashboard/doctors");
  const d = await res.json();
  el.innerText = d.available;
}

loadQueue();
loadDashboard();
loadDoctorStats();

setInterval(loadQueue, 5000);
