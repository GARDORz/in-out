const $ = (selector) => document.querySelector(selector);
const monthNames = [
  "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
];

function localDateTime(date) {
  const pad = (number) => String(number).padStart(2, "0");
  return date.getFullYear() + "-" + pad(date.getMonth() + 1) + "-" +
    pad(date.getDate()) + "T" + pad(date.getHours()) + ":" + pad(date.getMinutes());
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "เกิดข้อผิดพลาด");
  return data;
}

function showMessage(message, isError) {
  const node = $("#message");
  node.textContent = message;
  node.className = "message " + (isError ? "error" : "success");
}

function addStat(label, value) {
  const box = document.createElement("div");
  box.className = "stat";
  const strong = document.createElement("strong");
  strong.textContent = value;
  const span = document.createElement("span");
  span.textContent = label;
  box.append(strong, span);
  $("#summary").append(box);
}

async function loadReport() {
  const year = Number($("#year").value);
  const month = Number($("#month").value);
  const data = await requestJson("/api/report?year=" + year + "&month=" + month);
  const body = $("#report-body");
  body.replaceChildren();
  $("#summary").replaceChildren();
  const rows = Object.entries(data);
  $("#report-empty").hidden = rows.length > 0;
  let days = 0;
  let hours = 0;
  let overtime = 0;
  for (const [emp, record] of rows) {
    days += record.days;
    hours += record.total_hours;
    overtime += record.overtime_hours;
    const tr = document.createElement("tr");
    for (const value of [
      emp, record.days, record.total_hours.toFixed(2),
      record.late_days, record.overtime_hours.toFixed(2)
    ]) {
      const td = document.createElement("td");
      td.textContent = value;
      tr.append(td);
    }
    body.append(tr);
  }
  addStat("พนักงาน", rows.length);
  addStat("วันทำงานรวม", days);
  addStat("ชั่วโมงรวม", hours.toFixed(2));
  addStat("โอทีรวม", overtime.toFixed(2));
}

async function loadEvents() {
  const events = await requestJson("/api/events");
  const list = $("#events");
  list.replaceChildren();
  $("#events-empty").hidden = events.length > 0;
  for (const event of events) {
    const item = document.createElement("li");
    const badge = document.createElement("span");
    badge.className = "badge" + (event.type === "out" ? " out" : "");
    badge.textContent = event.type === "in" ? "เข้างาน" : "ออกงาน";
    const emp = document.createElement("strong");
    emp.className = "event-meta";
    emp.textContent = event.emp;
    const ts = document.createElement("time");
    ts.className = "event-time";
    ts.textContent = event.ts.replace("T", " ");
    item.append(badge, emp, ts);
    list.append(item);
  }
}

async function refresh() {
  await Promise.all([loadReport(), loadEvents()]);
}

async function submitAction(action) {
  const form = $("#entry-form");
  if (!form.reportValidity()) return;
  const buttons = [$("#clock-in"), $("#clock-out")];
  buttons.forEach((button) => button.disabled = true);
  try {
    const payload = {
      emp: $("#employee").value.trim(),
      ts: $("#timestamp").value
    };
    await requestJson("/api/clock-" + action, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    showMessage(action === "in" ? "บันทึกเข้างานแล้ว" : "บันทึกออกงานแล้ว", false);
    await refresh();
  } catch (error) {
    showMessage(error.message, true);
  } finally {
    buttons.forEach((button) => button.disabled = false);
  }
}

for (let i = 0; i < monthNames.length; i++) {
  const option = document.createElement("option");
  option.value = i + 1;
  option.textContent = monthNames[i];
  $("#month").append(option);
}
const today = new Date();
$("#timestamp").value = localDateTime(today);
$("#year").value = today.getFullYear();
$("#month").value = today.getMonth() + 1;
$("#clock-in").addEventListener("click", () => submitAction("in"));
$("#clock-out").addEventListener("click", () => submitAction("out"));
$("#report-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await loadReport();
  } catch (error) {
    showMessage(error.message, true);
  }
});
refresh().catch((error) => showMessage(error.message, true));
