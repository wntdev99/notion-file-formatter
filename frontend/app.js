const API = "";  // 같은 origin에서 서빙되므로 prefix 불필요

const dropZone     = document.getElementById("dropZone");
const fileInput    = document.getElementById("fileInput");
const uploadSection = document.getElementById("uploadSection");
const statusSection = document.getElementById("statusSection");
const fileName     = document.getElementById("fileName");
const fileSize     = document.getElementById("fileSize");
const progressBar  = document.getElementById("progressBar");
const statusMsg    = document.getElementById("statusMessage");
const resultInfo   = document.getElementById("resultInfo");
const originalSizeEl  = document.getElementById("originalSize");
const convertedSizeEl = document.getElementById("convertedSize");
const downloadBtn  = document.getElementById("downloadBtn");
const resetBtn     = document.getElementById("resetBtn");
const errorBox     = document.getElementById("errorBox");

let pollingTimer = null;

// --- 드래그 앤 드롭 ---
dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) startUpload(file);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) startUpload(fileInput.files[0]);
});

// --- 리셋 ---
resetBtn.addEventListener("click", reset);

// --- 업로드 시작 ---
async function startUpload(file) {
  showStatusSection(file);

  const formData = new FormData();
  formData.append("file", file);

  let jobId;
  try {
    const res = await fetch(`${API}/api/upload`, { method: "POST", body: formData });
    if (!res.ok) throw new Error((await res.json()).detail || "업로드 실패");
    const data = await res.json();
    jobId = data.job_id;
  } catch (err) {
    showError(err.message);
    return;
  }

  pollStatus(jobId);
}

// --- 상태 폴링 ---
function pollStatus(jobId) {
  setProgress(10, "변환 작업 대기 중...");

  pollingTimer = setInterval(async () => {
    try {
      const res = await fetch(`${API}/api/status/${jobId}`);
      if (!res.ok) throw new Error("상태 조회 실패");
      const data = await res.json();
      handleStatus(data, jobId);
    } catch (err) {
      clearInterval(pollingTimer);
      showError(err.message);
    }
  }, 1500);
}

function handleStatus(data, jobId) {
  if (data.status === "pending") {
    setProgress(15, "대기 중...");
    return;
  }
  if (data.status === "processing") {
    setProgress(55, "변환 중...");
    return;
  }
  clearInterval(pollingTimer);

  if (data.status === "done") {
    setProgress(100, data.message);
    showResult(data, jobId);
  } else {
    showError(data.message);
  }
}

// --- UI 헬퍼 ---
function showStatusSection(file) {
  uploadSection.classList.add("hidden");
  statusSection.classList.remove("hidden");
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  errorBox.classList.add("hidden");
  resultInfo.classList.add("hidden");
  downloadBtn.classList.add("hidden");
  setProgress(0, "업로드 중...");
}

function setProgress(pct, msg) {
  progressBar.style.width = pct + "%";
  statusMsg.textContent = msg;
}

function showResult(data, jobId) {
  const isSplit = data.message.includes("ZIP");
  const convertedLabel = document.getElementById("convertedLabel");

  originalSizeEl.textContent = formatBytes(data.original_size);
  convertedSizeEl.textContent = formatBytes(data.converted_size);
  convertedLabel.textContent = isSplit ? "파트당 최대" : "변환 후";

  if (isSplit) {
    downloadBtn.textContent = "ZIP 다운로드";
  } else {
    downloadBtn.textContent = "다운로드";
  }

  resultInfo.classList.remove("hidden");
  downloadBtn.classList.remove("hidden");
  downloadBtn.onclick = () => { window.location.href = `${API}/api/download/${jobId}`; };
}

function showError(msg) {
  errorBox.textContent = "오류: " + msg;
  errorBox.classList.remove("hidden");
  setProgress(0, "변환 실패");
}

function reset() {
  clearInterval(pollingTimer);
  uploadSection.classList.remove("hidden");
  statusSection.classList.add("hidden");
  fileInput.value = "";
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}
