/* ================= Config: กำหนดพารามิเตอร์เวลาและข้อมูล ================= */
async function fetchData() {
  try {
    const res = await fetch("http://localhost:8000/api/counts/latest");
    const data = await res.json();
    // update dataset
    DATA.series.cars.push(data.cars);
    DATA.series.humans.push(data.humans);
    // keep only last N slots
    DATA.series.cars = takeTail(DATA.series.cars, DATA.slots);
    DATA.series.humans = takeTail(DATA.series.humans, DATA.slots);
    renderAll();
  } catch (err) {
    console.error("Fetch error:", err);
  }
}

// refresh every 5 minutes
setInterval(fetchData, 5 * 60 * 1000);


/* ============== Render KPI ตอนนี้ (ค่าล่าสุด) ============== */
function renderKPINow(){
  const { cars, humans } = getCurrentWindow();

  const nowCars    = cars[cars.length - 1]   ?? 0;
  const prevCars   = cars[cars.length - 2]   ?? nowCars;
  const nowHumans  = humans[humans.length - 1] ?? 0;
  const prevHumans = humans[humans.length - 2] ?? nowHumans;

  document.getElementById("kpiNowCars").textContent   = nowCars.toLocaleString("th-TH");
  document.getElementById("kpiNowHumans").textContent = nowHumans.toLocaleString("th-TH");

  const carsTrendEl   = document.getElementById("kpiNowCarsTrend");
  const humansTrendEl = document.getElementById("kpiNowHumansTrend");

  if (carsTrendEl){
    carsTrendEl.textContent = nowCars > prevCars ? "↑" : (nowCars < prevCars ? "↓" : "→");
  }
  if (humansTrendEl){
    humansTrendEl.textContent = nowHumans > prevHumans ? "↑" : (nowHumans < prevHumans ? "↓" : "→");
  }
}

/* ================= Utilities ================= */
const fmtPct = (n) => (Math.round(n * 10) / 10).toFixed(1);
function sum(arr){ return arr.reduce((a,b)=>a+b,0); }
function floorToStep(date, stepMin = 5) {
  const d = new Date(date);
  d.setSeconds(0,0);
  const m = d.getMinutes();
  d.setMinutes(m - (m % stepMin));
  return d;
}
function buildPastTimes({ slots = 6, stepMin = 5, locale = 'th-TH' } = {}) {
  const end = floorToStep(new Date(), stepMin); // เวลาปัจจุบัน ปัดลง
  const out = [];
  for (let i = slots - 1; i >= 0; i--) {
    const t = new Date(end.getTime() - i * stepMin * 60_000);
    out.push(t.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' }));
  }
  return out; // เก่าก่อน -> ใหม่สุด
}
function takeTail(arr, n) { return (arr.length <= n) ? arr.slice() : arr.slice(arr.length - n); }

/* ============== Header time + Date buttons ============== */
(function setHeaderTime(){
  const el = document.getElementById('headerTime');
  const d = new Date();
  const th = d.toLocaleDateString('th-TH', {year:'numeric', month:'long', day:'numeric'});
  const tm = d.toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit'});
  if (el) el.textContent = `วันที่: ${th}, ${tm} น.`;
})();
(function initDate(){
  const dp = document.getElementById('datePick');
  const iso = new Date().toISOString().slice(0,10);
  if (dp) dp.value = iso;
  document.getElementById('btnToday')?.addEventListener('click', () => { if (dp) dp.value = iso; renderAll(); });
  document.getElementById('btnRefresh')?.addEventListener('click', () => renderAll());
})();

/* ============== Current window (times + slice data) ============== */
function getCurrentWindow() {
  const times  = buildPastTimes({ slots: DATA.slots, stepMin: DATA.stepMin });
  const cars   = takeTail(DATA.series.cars,   times.length);
  const humans = takeTail(DATA.series.humans, times.length);
  return { times, cars, humans };
}

/* ============== Table Render ============== */
function renderTable(){
  const body = document.getElementById('detailRows');
  if (!body) return;

  const { times, cars, humans } = getCurrentWindow();

  const rows = times.map((t,i)=>({
    time: t,
    car: cars[i] ?? 0,
    human: humans[i] ?? 0
  })).reverse();

  body.innerHTML = rows.map(r=>`
    <tr>
      <td>${r.time}</td>
      <td>${r.car}</td>
      <td>${r.human}</td>
    </tr>
  `).join('');
}

/* ============== KPIs + Window Hint ============== */
function renderKPI(){
  const { cars, humans, times } = getCurrentWindow();
  const carsTotal   = sum(cars);
  const humansTotal = sum(humans);
  const total       = carsTotal + humansTotal;

  document.getElementById('kpiCars').textContent   = carsTotal.toLocaleString('th-TH');
  document.getElementById('kpiHumans').textContent = humansTotal.toLocaleString('th-TH');
  document.getElementById('kpiTotal').textContent  = total.toLocaleString('th-TH');

  const hint = document.getElementById('windowHint');
  if (hint && times.length){
    hint.textContent = `${times[0]} – ${times[times.length - 1]} (ย้อนหลัง ${DATA.slots*DATA.stepMin} นาที)`;
  }
}

/* ============== Charts ============== */
let lineChart, donutChart;

function makeOrUpdateLine(){
  const ctx = document.getElementById('lineChart');
  if (!ctx) return;
  const { times, cars, humans } = getCurrentWindow();

  const cfg = {
    type: 'line',
    data: {
      labels: times,
      datasets: [
        {
          label: 'คน',
          data: humans,
          borderColor: '#2f80ed',
          backgroundColor: 'rgba(47,128,237,.15)',
          fill: true, tension: .35, pointRadius: 3
        },
        {
          label: 'รถ',
          data: cars,
          borderColor: '#f2994a',
          backgroundColor: 'rgba(242,153,74,.18)',
          fill: true, tension: .35, pointRadius: 3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: '#eef2f7' } },
        y: { grid: { color: '#eef2f7' }, beginAtZero:true, ticks:{ stepSize:5 } }
      },
      plugins: {
        legend: { position: 'bottom' },
        tooltip: { mode: 'index', intersect: false }
      }
    }
  };

  if (lineChart){
    lineChart.data.labels = cfg.data.labels;
    lineChart.data.datasets[0].data = humans;
    lineChart.data.datasets[1].data = cars;
    lineChart.update();
  } else {
    lineChart = new Chart(ctx, cfg);
  }
}

function makeOrUpdateDonut(){
  const ctx = document.getElementById('donutChart');
  if (!ctx) return;

  const { cars, humans } = getCurrentWindow();
  const carsTotal   = sum(cars);
  const humansTotal = sum(humans);
  const total = carsTotal + humansTotal || 1;
  const carsPct   = (carsTotal/total)*100;
  const humansPct = (humansTotal/total)*100;

  const labels = [
    `รถยนต์ ${fmtPct(carsPct)}%`,
    `คน ${fmtPct(humansPct)}%`
  ];
  const data = [carsTotal, humansTotal];

  const cfg = {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: ['#2f80ed','#f2994a'],
        borderWidth: 0
      }]
    },
    options: {
      responsive:true,
      maintainAspectRatio:false,
      cutout:'70%',
      plugins:{
        legend:{
          position:'bottom',
          labels:{ boxWidth:12, padding:8, font:{ size:17 } }
        },
        tooltip:{
          callbacks:{
            label: (c)=>{
              const v = c.raw ?? 0;
              const pct = (v / (data[0]+data[1] || 1)) * 100;
              return `${c.label} : ${v.toLocaleString('th-TH')} (${fmtPct(pct)}%)`;
            }
          }
        }
      }
    }
  };

  if (donutChart){
    donutChart.data.labels = labels;
    donutChart.data.datasets[0].data = data;
    donutChart.update();
  } else {
    donutChart = new Chart(ctx, cfg);
  }
}

/* ============== Controls ============== */
function flashButton(btn){
  if (!btn) return;
  btn.classList.add("clicked");
  setTimeout(()=> btn.classList.remove("clicked"), 400);
}

(function initControls(){
  const btnToday   = document.getElementById('btnToday');
  const btnRefresh = document.getElementById('btnRefresh');
  const btnRoute   = document.querySelector('.controls .btn:nth-of-type(2)'); 
  const btnSearch  = document.querySelector('.controls .btn-primary');       
  const dp         = document.getElementById('datePick');

  btnToday?.addEventListener('click', ()=>{
    flashButton(btnToday);
    const iso = new Date().toISOString().slice(0,10);
    if (dp) dp.value = iso;
    renderAll();
  });

  btnRefresh?.addEventListener('click', ()=>{
    flashButton(btnRefresh);
    renderAll();
  });

  btnRoute?.addEventListener('click', ()=>{
    flashButton(btnRoute);
    alert("ฟีเจอร์แนะนำเส้นทาง: เลือกเส้นทางที่การจราจรเบาที่สุด 🚗");
  });

  btnSearch?.addEventListener('click', ()=>{
    flashButton(btnSearch);
    if (dp && dp.value){
      alert("ค้นหาข้อมูลประจำวันที่ " + dp.value + " 📊");
    } else {
      alert("กรุณาเลือกวันที่ก่อนค้นหา ❗");
    }
  });
})();

/* ============== Render All ============== */
function renderAll(){
  renderTable();
  renderKPI();
  renderKPINow(); 
  makeOrUpdateLine();
  makeOrUpdateDonut();
}

/* ============== Initial & Auto Refresh ============== */
renderAll();
setInterval(renderAll, 60_000);
