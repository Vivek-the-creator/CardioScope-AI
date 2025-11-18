const toggleBtn = document.getElementById("toggleSidebar");
const sidebar = document.getElementById("sidebar");
const uploadForm = document.getElementById("uploadForm");
const patientList = document.getElementById("patientList");
const uploadArea = document.getElementById("uploadArea");
const ecgFileInput = document.getElementById("ecgFile");
const uploadBtn = document.getElementById("uploadBtn");
const backBtn = document.getElementById("backBtn");
const saveChangesBtn = document.getElementById("saveChangesBtn");
const updateFileBtn = document.getElementById("updateFileBtn");

let patients = JSON.parse(localStorage.getItem("patients") || "[]");
let lastUploadedRecord = null;  
let ecgData = {};
let timePoints = [];
let chart = null;

function formatKeyValueLines(data) {
  if (!data || typeof data !== "object") {
    return data ? String(data) : "--";
  }
  return Object.entries(data)
    .map(([k, v]) => `${k}: ${v}`)
    .join("\n");
}

toggleBtn.onclick = () => {
  sidebar.classList.toggle("show");
};

function generatePatientId(name) {
  const prefix = name.trim().toUpperCase().substring(0, 4).padEnd(4, "X");
  const randomDigits = Math.floor(100 + Math.random() * 900);
  return `${prefix}${randomDigits}`;
}

function generateUniquePatientId(name) {
  let id;
  do {
    id = generatePatientId(name);
  } while (patients.some(p => p.id === id));
  return id;
}

function refreshPatientList() {
  patientList.innerHTML = "";

  if (patients.length === 0) {
    const li = document.createElement("li");
    li.innerText = "No patients yet";
    li.style.color = "#888";
    li.style.fontStyle = "italic";
    li.style.pointerEvents = "none"; // make it non-clickable
    patientList.appendChild(li);
    return;
  }

  patients.forEach(p => {
    const li = document.createElement("li");
    li.classList.add("patient-item");

    const span = document.createElement("span");
    span.textContent = `${p.name} (${p.id})`;
    span.classList.add("patient-name");
    span.onclick = () => loadPatient(p.id);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.textContent = "🗑️";
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      deletePatient(p.id);
    };

    li.appendChild(span);
    li.appendChild(deleteBtn);
    patientList.appendChild(li);
  });
}


document.addEventListener("DOMContentLoaded", () => {
  refreshPatientList();
});


document.getElementById("browseBtn").onclick = () => {
  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();
  const gender = document.getElementById("gender").value;
  if (!name || !age || !gender) {
    alert("Please fill in Patient Name, Age, and Gender before uploading ECG.");
    return;
  }
  ecgFileInput.click();
};

ecgFileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();
  const gender = document.getElementById("gender").value;
  if (!name || !age || !gender) {
    alert("Please fill in Patient Name, Age, and Gender before selecting an ECG.");
    e.target.value = "";
    return;
  }

  uploadBtn.classList.remove("hidden");
  updateFileBtn.classList.add("hidden");

  if (file && file.name.endsWith(".csv")) {
    const reader = new FileReader();
    reader.onload = (e) => {
      parseCSV(e.target.result);
      document.getElementById("csvPreview").classList.remove("hidden");
      document.getElementById("ecgContent").classList.add("hidden");
      document.getElementById("chartSection").classList.add("hidden");
    };
    reader.readAsText(file);
  } else if (file && file.type.startsWith("image/")) {
    const reader = new FileReader();
    reader.onload = (e) => {
      document.getElementById("previewImage").src = e.target.result;
      uploadArea.classList.add("hidden");
      document.getElementById("ecgContent").classList.remove("hidden");
      document.getElementById("csvPreview").classList.add("hidden");
      document.getElementById("chartSection").classList.add("hidden");
    };
    reader.readAsDataURL(file);
  }
});

uploadArea.addEventListener("dragover", (e) => e.preventDefault());

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  if (!file) return;

  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  ecgFileInput.files = dataTransfer.files;

  ecgFileInput.dispatchEvent(new Event("change"));
});

uploadForm.onsubmit = async (e) => {
  e.preventDefault();
  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();
  const gender = document.getElementById("gender").value;
  const file = ecgFileInput.files[0];
  if (!name || !age || !gender || !file) {
    alert("Fill all fields and upload an ECG file.");
    return;
  }

  const existing = patients.find(p => p.name.toLowerCase() === name.toLowerCase() && p.age === age);
  if (existing) {
    const isMatch = await showModal(`Are you ${existing.id}?`);
    if (isMatch) {
      const update = await showModal("Do you want to update your previous record?");
      const id = update ? existing.id : generateUniquePatientId(name);
      proceedUpload(id);
    } else {
      proceedUpload(generateUniquePatientId(name));
    }
  } else {
    proceedUpload(generateUniquePatientId(name));
  }
};

async function proceedUpload(id) {
  const name = document.getElementById("name").value.trim();
  const age = document.getElementById("age").value.trim();
  const gender = document.getElementById("gender").value;
  const file = ecgFileInput.files[0];
  const isCSV = file.name.endsWith(".csv");
  const isImage = file.type.startsWith("image/");

  // Default placeholders before AI
  document.getElementById("diagnosis").innerText = "AI processing...";
  document.getElementById("score").innerText = "--";
  document.getElementById("notes").innerText = "--";

  // Call AI analyzer
  const aiResult = await analyzeWithAI(file);
  if (!aiResult) return; // Abort if AI failed

  const diagnosisObj = aiResult.diagnosis || { Assessment: "Unavailable" };
  const scoreObj = aiResult.score || { Confidence: "--" };
  const notesText = aiResult.doctors_notes || "No notes";
  const diagnosisText = formatKeyValueLines(diagnosisObj);
  const scoreText = formatKeyValueLines(scoreObj);

  const record = {
    id,
    name,
    age,
    gender,
    fileType: isCSV ? "csv" : "image",
    previewSrc: isImage ? document.getElementById("previewImage").src : null,
    previewTable: isCSV ? document.getElementById("csvTableWrapper").innerHTML : null,
    ecgData: isCSV ? ecgData : {},
    timePoints: isCSV ? timePoints : [],
    diagnosis: diagnosisObj,
    score: scoreObj,
    diagnosisText,
    scoreText,
    notes: notesText
  };
  lastUploadedRecord = record;


  // Save to localStorage
  const index = patients.findIndex(p => p.id === id);
  if (index !== -1) patients[index] = record;
  else patients.push(record);

  localStorage.setItem("patients", JSON.stringify(patients));
  refreshPatientList();

  // Update UI
  document.getElementById("diagnosis").innerText = diagnosisText;
  document.getElementById("score").innerText = scoreText;
  document.getElementById("notes").innerText = notesText;
  document.getElementById("exportPdfBtn").classList.remove("hidden");


  document.getElementById("chartSection").classList.toggle("hidden", !isCSV);
  document.getElementById("detectedLeads").innerHTML = isCSV
    ? ["I", "II", "III", "aVR", "aVL", "aVF", "V1", "V2", "V3", "V4", "V5", "V6"]
        .map(lead => `<span>${lead}</span>`).join("")
    : "";

  backBtn.classList.remove("hidden");
  uploadBtn.classList.add("hidden");
  saveChangesBtn.classList.remove("hidden");
  updateFileBtn.classList.remove("hidden");

  uploadForm.dataset.editingId = id;
}


saveChangesBtn.onclick = () => {
  const id = uploadForm.dataset.editingId;
  const index = patients.findIndex(p => p.id === id);
  if (index === -1) return;

  const patient = patients[index];
  patient.name = document.getElementById("name").value.trim();
  patient.age = document.getElementById("age").value.trim();
  patient.gender = document.getElementById("gender").value;
  patient.diagnosisText = document.getElementById("diagnosis").innerText;
  patient.scoreText = document.getElementById("score").innerText;
  patient.notes = document.getElementById("notes").innerText;

  localStorage.setItem("patients", JSON.stringify(patients));
  refreshPatientList();
  alert("Changes saved.");
};

updateFileBtn.onclick = () => {
  ecgFileInput.click();
  updateFileBtn.classList.add("hidden");
};

backBtn.onclick = () => {
  uploadArea.classList.remove("hidden");
  document.getElementById("ecgContent").classList.add("hidden");
  document.getElementById("csvPreview").classList.add("hidden");
  document.getElementById("chartSection").classList.add("hidden");

  uploadBtn.classList.remove("hidden");
  backBtn.classList.add("hidden");
  saveChangesBtn.classList.add("hidden");
  updateFileBtn.classList.add("hidden");

  document.getElementById("uploadForm").reset();
  document.getElementById("previewImage").src = "";
  document.getElementById("detectedLeads").innerHTML = "";
  document.getElementById("diagnosis").innerText = "--";
  document.getElementById("score").innerText = "--";
  document.getElementById("notes").innerText = "--";

  if (chart) chart.destroy();
  chart = null;
  ecgData = {};
  timePoints = [];
};

function loadPatient(id) {
  const patient = patients.find(p => p.id === id);
  if (!patient) return;

  document.getElementById("name").value = patient.name;
  document.getElementById("age").value = patient.age;
  document.getElementById("gender").value = patient.gender;
  const diagnosisText = patient.diagnosisText || formatKeyValueLines(patient.diagnosis);
  const scoreText = patient.scoreText || formatKeyValueLines(patient.score);
  document.getElementById("diagnosis").innerText = diagnosisText;
  document.getElementById("score").innerText = scoreText;
  document.getElementById("notes").innerText = patient.notes;

  uploadForm.dataset.editingId = patient.id;

  if (patient.fileType === "image") {
    document.getElementById("previewImage").src = patient.previewSrc;
    document.getElementById("ecgContent").classList.remove("hidden");
    document.getElementById("csvPreview").classList.add("hidden");
    document.getElementById("chartSection").classList.add("hidden");
  } else {
    document.getElementById("csvTableWrapper").innerHTML = patient.previewTable;
    document.getElementById("csvPreview").classList.remove("hidden");
    document.getElementById("ecgContent").classList.add("hidden");
    document.getElementById("chartSection").classList.remove("hidden");
    ecgData = patient.ecgData;
    timePoints = patient.timePoints;
  }

  uploadArea.classList.add("hidden");
  uploadBtn.classList.add("hidden");
  backBtn.classList.remove("hidden");
  saveChangesBtn.classList.remove("hidden");
  updateFileBtn.classList.remove("hidden");
}

function parseCSV(csv) {
  const lines = csv.trim().split("\n");
  const headers = lines[0].split(",");

  ecgData = {};
  timePoints = [];

  headers.slice(1).forEach(lead => {
    ecgData[lead.trim()] = [];
  });

  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(",");
    timePoints.push(parseFloat(parts[0]));
    headers.slice(1).forEach((lead, j) => {
      ecgData[lead.trim()].push(parseFloat(parts[j + 1]));
    });
  }

  const previewLimit = 5;
  const table = document.createElement("table");
  const headerRow = document.createElement("tr");
  headers.forEach(h => {
    const th = document.createElement("th");
    th.innerText = h;
    headerRow.appendChild(th);
  });
  table.appendChild(headerRow);

  for (let i = 1; i <= previewLimit && i < lines.length; i++) {
    const row = document.createElement("tr");
    const cells = lines[i].split(",");
    cells.forEach(c => {
      const td = document.createElement("td");
      td.innerText = c;
      row.appendChild(td);
    });
    table.appendChild(row);
  }

  const wrapper = document.getElementById("csvTableWrapper");
  wrapper.innerHTML = "";
  wrapper.appendChild(table);

  document.getElementById("uploadArea").classList.add("hidden");
  document.getElementById("csvPreview").classList.remove("hidden");
}

document.getElementById("leadSelect").addEventListener("change", function () {
  const lead = this.value;
  if (!lead || !ecgData[lead]) return;

  if (chart) chart.destroy();

  const ctx = document.getElementById("ecgChart").getContext("2d");
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: timePoints,
      datasets: [{
        label: `ECG Lead ${lead}`,
        data: ecgData[lead],
        borderColor: "blue",
        backgroundColor: "rgba(0, 123, 255, 0.1)",
        tension: 0.3,
        pointRadius: 0
      }]
    },
    options: {
      scales: {
        x: { title: { display: true, text: "Time (s)" } },
        y: { title: { display: true, text: "Amplitude (mV)" } }
      },
      responsive: true
    }
  });
});

function showModal(message) {
  return new Promise((resolve) => {
    const modal = document.getElementById("customModal");
    document.getElementById("modalMessage").innerText = message;
    modal.classList.remove("hidden");

    const yesBtn = document.getElementById("modalYes");
    const noBtn = document.getElementById("modalNo");

    const cleanup = () => {
      modal.classList.add("hidden");
      yesBtn.removeEventListener("click", yesHandler);
      noBtn.removeEventListener("click", noHandler);
    };

    const yesHandler = () => {
      cleanup();
      resolve(true);
    };
    const noHandler = () => {
      cleanup();
      resolve(false);
    };

    yesBtn.addEventListener("click", yesHandler);
    noBtn.addEventListener("click", noHandler);
  });
}

function deletePatient(id) {
  const patient = patients.find(p => p.id === id);
  if (!patient) return;

  showCustomConfirm(`Do you want to delete <strong>${patient.name} (${id})</strong>?`, (confirmed) => {
    if (confirmed) {
      patients = patients.filter(p => p.id !== id);
      localStorage.setItem("patients", JSON.stringify(patients));
      refreshPatientList();
      backBtn.click();
    }
  });
}

function showCustomConfirm(message, callback) {
  const modal = document.createElement("div");
  modal.className = "custom-modal";
  modal.innerHTML = `
    <div class="modal-content">
      <p>${message}</p>
      <div class="modal-buttons">
        <button class="yes-btn">Yes</button>
        <button class="no-btn">No</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  modal.querySelector(".yes-btn").onclick = () => {
    callback(true);
    document.body.removeChild(modal);
  };
  modal.querySelector(".no-btn").onclick = () => {
    callback(false);
    document.body.removeChild(modal);
  };
}
async function analyzeWithAI(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      alert("AI Error: " + data.error);
      return null;
    }

    return data;
  } catch (err) {
    console.error("AI request failed:", err);
    alert("Failed to analyze ECG file with AI.");
    return null;
  }
}

document.getElementById("exportPdfBtn").addEventListener("click", () => {
  if (!lastUploadedRecord) return;

  const {
    name, age, gender, fileType, previewSrc, previewTable,
    diagnosis, score, diagnosisText, scoreText, notes
  } = lastUploadedRecord;

  const now = new Date();
  const dateTime = now.toLocaleString("en-IN", {
    year: "numeric", month: "long", day: "numeric",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true
  });

  // Create container for export
  const exportDiv = document.createElement("div");
  exportDiv.style.padding = "20px";
  exportDiv.style.fontFamily = "Arial, sans-serif";
  exportDiv.style.color = "#000";
  exportDiv.style.background = "#fff";

  exportDiv.innerHTML = `
    <h2 style="text-align:center;">ECG Analysis Report</h2>
    <p><strong>Date & Time:</strong> ${dateTime}</p>
    <p><strong>Patient Name:</strong> ${name}</p>
    <p><strong>Patient Age:</strong> ${age}</p>
    <p><strong>Patient Gender:</strong> ${gender}</p>
    <hr style="margin: 10px 0;">
  `;

  // Show Image or CSV
  if (fileType === "image" && previewSrc) {
    const img = document.createElement("img");
    img.src = previewSrc;
    img.style.maxWidth = "100%";
    img.style.margin = "12px 0";
    exportDiv.appendChild(img);
  } else if (fileType === "csv" && previewTable) {
    const csvWrapper = document.createElement("div");
    csvWrapper.innerHTML = `
      <h3>CSV Preview</h3>
      ${previewTable}
      <p style="margin-top: 8px;"><i>(CSV preview is limited to first few rows)</i></p>
    `;
    exportDiv.appendChild(csvWrapper);
  }

  // Diagnosis
  exportDiv.innerHTML += `<h3 style="margin-top: 20px;">Diagnosis</h3>`;
  const diagnosisLines = diagnosis && typeof diagnosis === "object"
    ? formatKeyValueLines(diagnosis)
    : (diagnosisText || "--");
  const diagnosisPre = document.createElement("pre");
  diagnosisPre.textContent = diagnosisLines;
  diagnosisPre.style.whiteSpace = "pre-wrap";
  diagnosisPre.style.fontSize = "14px";
  exportDiv.appendChild(diagnosisPre);

  // Score
  exportDiv.innerHTML += `<h3 style="margin-top: 12px;">Score</h3>`;
  const scoreLines = score && typeof score === "object"
    ? formatKeyValueLines(score)
    : (scoreText || "--");
  const scorePre = document.createElement("pre");
  scorePre.textContent = scoreLines;
  scorePre.style.whiteSpace = "pre-wrap";
  scorePre.style.fontSize = "14px";
  exportDiv.appendChild(scorePre);

  // Notes
  exportDiv.innerHTML += `<h3 style="margin-top: 12px;">Doctor’s Notes</h3>`;
  const notesPre = document.createElement("pre");
  notesPre.textContent = notes;
  notesPre.style.whiteSpace = "pre-wrap";
  notesPre.style.fontSize = "14px";
  exportDiv.appendChild(notesPre);

  // Attach temporarily & export
  document.body.appendChild(exportDiv);
  html2pdf().from(exportDiv).set({
    margin: 10,
    filename: `ECG_Report_${name.replace(/\s+/g, "_")}_${Date.now()}.pdf`,
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  }).save().then(() => {
    document.body.removeChild(exportDiv);
  });
});
