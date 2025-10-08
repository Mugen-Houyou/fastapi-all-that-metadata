const API_BASE = "/api"; // FastAPI에 맞게 조정. 예: "http://localhost:8000/api"

const els = {
  dropzone: document.getElementById("dropzone"),
  fileInput: document.getElementById("fileInput"),
  selectBtn: document.getElementById("selectBtn"),
  analyzeBtn: document.getElementById("analyzeBtn"),
  progressWrap: document.getElementById("progressWrap"),
  progressBar: document.getElementById("progressBar"),
  progressText: document.getElementById("progressText"),
  previewSection: document.getElementById("previewSection"),
  previewImg: document.getElementById("previewImg"),
  basicInfo: document.getElementById("basicInfo"),
  cameraInfo: document.getElementById("cameraInfo"),
  captureInfo: document.getElementById("captureInfo"),
  gpsInfo: document.getElementById("gpsInfo"),
  mapLinkWrap: document.getElementById("mapLinkWrap"),
  mapLink: document.getElementById("mapLink"),
  rawSection: document.getElementById("rawSection"),
  rawJson: document.getElementById("rawJson"),
  rowTpl: document.getElementById("rowTpl"),
  clearBtn: document.getElementById("clearBtn"),
  mockToggle: document.getElementById("mockToggle"),
};

let file = null;

const acceptTypes = [
  "image/jpeg", "image/jpg",
  "image/heic", "image/heif",
  "image/png",
];

function bytes(n){
  if(n < 1024) return `${n} B`;
  if(n < 1024*1024) return `${(n/1024).toFixed(1)} KB`;
  if(n < 1024*1024*1024) return `${(n/1024/1024).toFixed(1)} MB`;
  return `${(n/1024/1024/1024).toFixed(1)} GB`;
}

function setProgress(p){
  els.progressWrap.classList.remove("hidden");
  els.progressBar.style.width = `${p}%`;
  els.progressText.textContent = `${Math.round(p)}%`;
  if(p >= 100){
    setTimeout(()=>els.progressWrap.classList.add("hidden"), 800);
  }
}

function resetUI(){
  file = null;
  els.fileInput.value = "";
  els.previewSection.classList.add("hidden");
  els.rawSection.classList.add("hidden");
  els.analyzeBtn.disabled = true;
  els.progressWrap.classList.add("hidden");
  els.progressBar.style.width = "0%";
  els.progressText.textContent = "0%";
  els.basicInfo.innerHTML = "";
  els.cameraInfo.innerHTML = "";
  els.captureInfo.innerHTML = "";
  els.gpsInfo.innerHTML = "";
  els.mapLinkWrap.classList.add("hidden");
  els.previewImg.removeAttribute("src");
}

function isAcceptType(f){
  return acceptTypes.includes(f.type) || f.name.toLowerCase().endsWith(".heic") || f.name.toLowerCase().endsWith(".heif");
}

function fillKV(dl, entries){
  for(const [k,v] of entries){
    if(v == null || v === "" || Number.isNaN(v)) continue;
    const frag = els.rowTpl.content.cloneNode(true);
    frag.querySelector("dt").textContent = k;
    frag.querySelector("dd").textContent = String(v);
    dl.appendChild(frag);
  }
}

function toDMS(dec){
  const abs = Math.abs(dec);
  const d = Math.floor(abs);
  const mFloat = (abs - d) * 60;
  const m = Math.floor(mFloat);
  const s = ((mFloat - m) * 60).toFixed(2);
  return `${d}° ${m}' ${s}"`;
}

function renderResult(json, chosenFile){
  // 이미지 미리보기
  if(chosenFile){
    const url = URL.createObjectURL(chosenFile);
    els.previewImg.src = url;
  }

  const b = json?.image ?? {};
  const exif = json?.exif ?? {};
  const gps = json?.gps ?? {};

  // 기본 정보
  els.basicInfo.innerHTML = "";
  fillKV(els.basicInfo, [
    ["파일명", chosenFile?.name],
    ["MIME", b.mime],
    ["용량", chosenFile ? bytes(chosenFile.size) : (b.size ? bytes(b.size) : null)],
    ["해상도", (b.width && b.height) ? `${b.width} × ${b.height}` : null],
    ["색 공간", exif.ColorSpace],
    ["Orientation", exif.Orientation],
  ]);

  // 카메라
  els.cameraInfo.innerHTML = "";
  fillKV(els.cameraInfo, [
    ["제조사", exif.Make],
    ["모델", exif.Model],
    ["렌즈", exif.LensModel || exif.LensMake && `${exif.LensMake} ${exif.LensModel}`],
    ["소프트웨어", exif.Software],
    ["펌웨어", exif.Firmware || null],
  ]);

  // 촬영
  els.captureInfo.innerHTML = "";
  fillKV(els.captureInfo, [
    ["원본 촬영 시각", exif.DateTimeOriginal || exif.CreateDate || exif.DateTime],
    ["노출", exif.ExposureTime ? `1/${Math.round(1/Number(exif.ExposureTime))}s` : null],
    ["조리개", exif.FNumber ? `f/${exif.FNumber}` : null],
    ["ISO", exif.ISO],
    ["초점거리", exif.FocalLength ? `${exif.FocalLength}mm` : null],
    ["화이트밸런스", exif.WhiteBalance],
    ["플래시", exif.Flash],
  ]);

  // GPS
  els.gpsInfo.innerHTML = "";
  let lat = gps.lat ?? exif.GPSLatitude;
  let lon = gps.lon ?? exif.GPSLongitude;

  if(typeof lat === "string") lat = Number(lat);
  if(typeof lon === "string") lon = Number(lon);

  fillKV(els.gpsInfo, [
    ["위도", (lat!=null) ? `${lat} (${toDMS(lat)})` : null],
    ["경도", (lon!=null) ? `${lon} (${toDMS(lon)})` : null],
    ["고도", (gps.alt!=null) ? `${gps.alt} m` : (exif.GPSAltitude!=null ? `${exif.GPSAltitude} m` : null)],
  ]);

  if(lat!=null && lon!=null){
    els.mapLink.href = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}#map=16/${lat}/${lon}`;
    els.mapLinkWrap.classList.remove("hidden");
  } else {
    els.mapLinkWrap.classList.add("hidden");
  }

  // RAW
  els.rawJson.textContent = JSON.stringify(json, null, 2);

  els.previewSection.classList.remove("hidden");
  els.rawSection.classList.remove("hidden");
}

function mockResponse(chosenFile){
  // 최소 Mock 데이터 (후에 FastAPI 스키마와 맞추기)
  return {
    image: {
      width: 4032,
      height: 3024,
      mime: chosenFile?.type || "image/jpeg",
      size: chosenFile?.size || 0
    },
    exif: {
      Make: "Apple",
      Model: "iPhone 13 Pro",
      LensModel: "iPhone 13 Pro back triple camera 5.7mm f/1.5",
      DateTimeOriginal: "2025:08:31 14:22:05",
      ExposureTime: 0.005,         // 1/200s
      FNumber: 1.5,
      ISO: 32,
      FocalLength: 5.7,
      ColorSpace: "sRGB",
      Orientation: "Horizontal (normal)",
      Flash: "Off, did not fire",
      WhiteBalance: "Auto",
      Software: "iOS 17.6"
    },
    gps: {
      lat: 37.5665,
      lon: 126.9780,
      alt: 38.2
    },
    raw: {
      // 백엔드에서 제공하는 모든 태그의 원본 키-값을 그대로 넣어주면 됨
    }
  };
}

function validateFile(f){
  const MAX = 25 * 1024 * 1024;
  if(!f) return "파일이 선택되지 않았습니다.";
  if(!isAcceptType(f)) return "지원하지 않는 파일 형식입니다.";
  if(f.size > MAX) return "파일 용량이 25MB를 초과합니다.";
  return null;
}

/** -------- events -------- */
els.selectBtn.addEventListener("click", () => els.fileInput.click());

els.dropzone.addEventListener("click", () => els.fileInput.click());
els.dropzone.addEventListener("keydown", (e)=>{
  if(e.key === "Enter" || e.key === " ") els.fileInput.click();
});
["dragenter","dragover"].forEach(ev=>{
  els.dropzone.addEventListener(ev, (e)=>{ e.preventDefault(); e.stopPropagation(); els.dropzone.classList.add("hover"); });
});
["dragleave","drop"].forEach(ev=>{
  els.dropzone.addEventListener(ev, (e)=>{ e.preventDefault(); e.stopPropagation(); els.dropzone.classList.remove("hover"); });
});
els.dropzone.addEventListener("drop", (e)=>{
  const f = e.dataTransfer.files?.[0];
  if(!f) return;
  const err = validateFile(f);
  if(err) { alert(err); return; }
  file = f;
  els.analyzeBtn.disabled = false;
  // 미리보기만 우선
  const url = URL.createObjectURL(file);
  els.previewImg.src = url;
  els.previewSection.classList.remove("hidden");
});

els.fileInput.addEventListener("change", (e)=>{
  const f = e.target.files?.[0];
  if(!f) return;
  const err = validateFile(f);
  if(err) { alert(err); e.target.value=""; return; }
  file = f;
  els.analyzeBtn.disabled = false;
  const url = URL.createObjectURL(file);
  els.previewImg.src = url;
  els.previewSection.classList.remove("hidden");
});

els.clearBtn.addEventListener("click", resetUI);

els.analyzeBtn.addEventListener("click", async ()=>{
  if(!file){ alert("파일을 선택해주세요."); return; }

  if(els.mockToggle.checked){
    setProgress(20);
    await new Promise(r=>setTimeout(r,200));
    setProgress(60);
    const data = mockResponse(file);
    setProgress(100);
    renderResult(data, file);
    return;
  }

  try{
    const form = new FormData();
    form.append("file", file);

    setProgress(10);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 60_000); // 60s timeout

    const res = await fetch(`${API_BASE}/exif`, {
      method: "POST",
      body: form,
      signal: controller.signal,
    });

    clearTimeout(timer);
    setProgress(70);

    if(!res.ok){
      const text = await res.text().catch(()=> "");
      throw new Error(`서버 오류 (${res.status}) ${text}`);
    }
    const json = await res.json();
    setProgress(100);
    renderResult(json, file);
  } catch(err){
    console.error(err);
    alert(err.message || "분석 중 오류가 발생했습니다.");
    els.progressWrap.classList.add("hidden");
  }
});

/** -------- minor UX polish -------- */
document.addEventListener("paste", (e)=>{
  const item = [...(e.clipboardData?.items || [])].find(i=>i.type.startsWith("image/"));
  if(!item) return;
  const f = item.getAsFile();
  const err = validateFile(f);
  if(err) { alert(err); return; }
  file = f;
  els.analyzeBtn.disabled = false;
  const url = URL.createObjectURL(file);
  els.previewImg.src = url;
  els.previewSection.classList.remove("hidden");
});
