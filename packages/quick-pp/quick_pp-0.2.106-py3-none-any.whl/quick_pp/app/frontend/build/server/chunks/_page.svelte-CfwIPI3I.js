import { o as onDestroy, a as attr, v as escape_html, c as bind_props } from './error.svelte-DqMYEJMd.js';
import { B as Button } from './button-B4nvwarG.js';
import { w as workspace, c as applyDepthFilter, b as applyZoneFilter } from './workspace-DPIadIP6.js';
import { D as DepthFilterStatus } from './DepthFilterStatus-09LDbYxV.js';
import { P as ProjectWorkspace } from './ProjectWorkspace-DgKKwrTz.js';
import './WsWellPlot-DL2reMkT.js';

function WsSaturation($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let projectId = $$props["projectId"];
    let wellName = $$props["wellName"];
    const API_BASE = "http://localhost:6312";
    let depthFilter = { enabled: false, minDepth: null, maxDepth: null };
    let zoneFilter = { enabled: false, zones: [] };
    let visibleRows = [];
    let measSystem = "metric";
    let waterSalinity = 35e3;
    let mParam = 2;
    let rwParam = 0.1;
    let slopeParam = 2;
    let useSlopeForQv = false;
    let loading = false;
    let error = null;
    let dataLoaded = false;
    let dataCache = /* @__PURE__ */ new Map();
    let fullRows = [];
    let tempGradResults = [];
    let rwResults = [];
    let archieResults = [];
    let waxmanResults = [];
    let bList = [];
    let qvnList = [];
    let mStarList = [];
    let archieChartData = [];
    let waxmanChartData = [];
    let saveLoadingSat = false;
    let saveMessageSat = null;
    let _pollTimer = null;
    let _pollAttempts = 0;
    let _maxPollAttempts = 120;
    let pollStatus = null;
    const POLL_INTERVAL = 1e3;
    async function loadWellData() {
      if (!projectId || !wellName) return;
      const cacheKey = `${projectId}_${wellName}`;
      if (dataCache.has(cacheKey)) {
        fullRows = dataCache.get(cacheKey);
        dataLoaded = true;
        return;
      }
      loading = true;
      error = null;
      pollStatus = null;
      try {
        pollStatus = "Initiating well data loading...";
        const initResponse = await initiateMergedDataGeneration();
        const { task_id, result } = initResponse;
        let rows;
        if (result) {
          rows = result;
        } else {
          pollStatus = "Waiting for well data...";
          rows = await pollForMergedDataResult(task_id);
        }
        if (!Array.isArray(rows)) throw new Error("Unexpected data format from backend");
        fullRows = rows;
        dataCache.set(cacheKey, rows);
        dataLoaded = true;
      } catch (e) {
        console.warn("Failed to load well data", e);
        error = String(e?.message ?? e);
      } finally {
        loading = false;
        pollStatus = null;
      }
    }
    async function initiateMergedDataGeneration() {
      const res = await fetch(`${API_BASE}/quick_pp/database/projects/${projectId}/wells/${encodeURIComponent(String(wellName))}/merged/generate`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (!data.task_id) throw new Error("No task_id returned from server");
      return { task_id: data.task_id, result: data.result };
    }
    function clearMergedDataPollTimer() {
      if (_pollTimer) {
        clearInterval(_pollTimer);
        _pollTimer = null;
      }
      pollStatus = null;
    }
    async function pollForMergedDataResult(taskId) {
      const url = `${API_BASE}/quick_pp/database/projects/${projectId}/wells/${encodeURIComponent(String(wellName))}/merged/result/${taskId}`;
      return new Promise((resolve, reject) => {
        _pollAttempts = 0;
        const poll = async () => {
          if (_pollAttempts >= _maxPollAttempts) {
            const msg = "Well data loading timed out after 2 minutes";
            console.error(msg);
            clearMergedDataPollTimer();
            reject(new Error(msg));
            return;
          }
          try {
            const res = await fetch(url);
            if (!res.ok) {
              throw new Error(`Poll failed with status ${res.status}`);
            }
            const data = await res.json();
            if (data.status === "success") {
              clearMergedDataPollTimer();
              resolve(data.result);
            } else if (data.status === "error") {
              clearMergedDataPollTimer();
              reject(new Error(data.error || "Task failed with unknown error"));
            } else if (data.status === "pending") {
              pollStatus = `Loading well data... (${_pollAttempts}s)`;
              _pollAttempts++;
            } else {
              clearMergedDataPollTimer();
              reject(new Error(`Unknown task status: ${data.status}`));
            }
          } catch (err) {
            console.error("Poll request failed:", err);
            pollStatus = `Retrying... (attempt ${_pollAttempts})`;
            _pollAttempts++;
          }
        };
        poll();
        _pollTimer = window.setInterval(poll, POLL_INTERVAL);
      });
    }
    function extractTVDSSRows() {
      const filteredRows = visibleRows;
      const rows = [];
      for (const r of filteredRows) {
        const tvd = r.tvdss ?? r.TVDSS ?? r.tvd ?? r.TVD ?? r.depth ?? r.DEPTH ?? NaN;
        const tvdNum = Number(tvd);
        if (!isNaN(tvdNum)) rows.push({ tvdss: tvdNum });
      }
      return rows;
    }
    async function estimateTempGradAndRw() {
      const tvdRows = extractTVDSSRows();
      if (!tvdRows.length) {
        error = "No TVD/DEPTH values found in well data";
        return;
      }
      loading = true;
      error = null;
      tempGradResults = [];
      rwResults = [];
      try {
        const tempPayload = { meas_system: measSystem, data: tvdRows };
        const tempRes = await fetch(`${API_BASE}/quick_pp/saturation/temp_grad`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(tempPayload)
        });
        if (!tempRes.ok) throw new Error(await tempRes.text());
        const tvals = await tempRes.json();
        const grads = Array.isArray(tvals) ? tvals.map((d) => Number(d.TEMP_GRAD ?? d.temp_grad ?? d.value ?? NaN)) : [];
        tempGradResults = grads;
        const rwPayload = {
          water_salinity: Number(waterSalinity),
          data: grads.map((g) => ({ temp_grad: g }))
        };
        const rwRes = await fetch(`${API_BASE}/quick_pp/saturation/rw`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(rwPayload)
        });
        if (!rwRes.ok) throw new Error(await rwRes.text());
        const rvals = await rwRes.json();
        rwResults = Array.isArray(rvals) ? rvals.map((d) => Number(d.RW ?? d.rw ?? NaN)) : [];
      } catch (e) {
        console.warn("TempGrad/Rw error", e);
        error = String(e?.message ?? e);
      } finally {
        loading = false;
      }
    }
    async function estimateWaterSaturation() {
      tempGradResults = [];
      rwResults = [];
      archieResults = [];
      waxmanResults = [];
      bList = [];
      qvnList = [];
      mStarList = [];
      error = null;
      loading = true;
      try {
        await estimateTempGradAndRw();
        if (error) return;
        await estimateArchieSw();
        if (error) return;
        await estimateWaxmanSw();
      } catch (e) {
        console.warn("Estimate Water Saturation error", e);
        error = String(e?.message ?? e);
      } finally {
        loading = false;
      }
    }
    async function estimateArchieSw() {
      if (!rwResults || rwResults.length === 0) {
        error = "Please compute Rw first";
        return;
      }
      const filteredRows = visibleRows;
      const rows = [];
      const depths = [];
      let idx = 0;
      for (const r of filteredRows) {
        const depth = Number(r.depth ?? r.DEPTH ?? NaN);
        const rt = Number(r.rt ?? r.RT ?? r.Rt ?? r.res ?? r.RES ?? NaN);
        const phit = Number(r.phit ?? r.PHIT ?? r.Phit ?? NaN);
        const m = Number(mParam);
        if (isNaN(rt) || isNaN(phit)) continue;
        const rw = rwResults[idx++] ?? NaN;
        if (isNaN(rw)) continue;
        rows.push({ rt, rw, phit, m });
        depths.push(depth);
      }
      if (!rows.length) {
        error = "No RT/PHIT rows available for Archie";
        return;
      }
      loading = true;
      error = null;
      archieResults = [];
      try {
        const payload = { data: rows };
        const res = await fetch(`${API_BASE}/quick_pp/saturation/archie`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        const out = await res.json();
        archieResults = Array.isArray(out) ? out.map((d) => Number(d.SWT ?? d.swt ?? NaN)) : [];
        archieChartData = archieResults.map((v, i) => ({ depth: depths[i], SWT: v })).filter((d) => !isNaN(Number(d.depth)));
      } catch (e) {
        console.warn("Archie error", e);
        error = String(e?.message ?? e);
      } finally {
        loading = false;
      }
    }
    async function estimateWaxmanSw() {
      if (!rwResults || rwResults.length === 0 || !tempGradResults || tempGradResults.length === 0) {
        error = "Please compute Temp Grad and Rw first";
        return;
      }
      const qvnRows = [];
      const shalePoroRows = [];
      const bRows = [];
      const finalRows = [];
      const filteredRows = visibleRows;
      for (const r of filteredRows) {
        const nphi = Number(r.nphi ?? r.NPHI ?? r.Nphi ?? NaN);
        const phit = Number(r.phit ?? r.PHIT ?? r.Phit ?? NaN);
        const vclay = Number(r.vclay ?? r.VCLAY ?? r.vcld ?? r.VCLD ?? NaN);
        if (!isNaN(nphi) && !isNaN(phit)) shalePoroRows.push({ nphi, phit });
        if (!isNaN(vclay) && !isNaN(phit)) qvnRows.push({ vclay, phit });
      }
      for (let i = 0; i < tempGradResults.length; i++) {
        const tg = tempGradResults[i];
        const rw = rwResults[i];
        if (!isNaN(Number(tg)) && !isNaN(Number(rw))) bRows.push({ temp_grad: tg, rw });
      }
      bList = [];
      if (bRows.length) {
        try {
          const payload = { data: bRows };
          const res = await fetch(`${API_BASE}/quick_pp/saturation/b_waxman_smits`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          if (!res.ok) throw new Error(await res.text());
          const out = await res.json();
          bList = Array.isArray(out) ? out.map((d) => Number(d.B ?? d.b ?? NaN)) : [];
        } catch (e) {
          console.warn("B estimation error", e);
        }
      }
      qvnList = [];
      {
        let shalePoroList = [];
        if (shalePoroRows.length) {
          try {
            const payload = { data: shalePoroRows };
            const res = await fetch(`${API_BASE}/quick_pp/porosity/shale_porosity`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            const out = await res.json();
            shalePoroList = Array.isArray(out) ? out.map((d) => Number(d.PHIT_SH ?? d.phit_sh ?? NaN)) : [];
          } catch (e) {
            console.warn("Shale porosity error", e);
          }
        }
        if (qvnRows.length && shalePoroList.length) {
          try {
            const qvnPayloadData = qvnRows.map((row, i) => ({
              vclay: row.vclay,
              phit: row.phit,
              phit_clay: shalePoroList[i]
            }));
            const payload = { data: qvnPayloadData };
            const res = await fetch(`${API_BASE}/quick_pp/saturation/estimate_qvn`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            if (!res.ok) throw new Error(await res.text());
            const out = await res.json();
            qvnList = Array.isArray(out) ? out.map((d) => Number(d.QVN ?? d.qvn ?? NaN)) : [];
          } catch (e) {
            console.warn("Qvn error", e);
          }
        }
      }
      let qi = 0;
      let bi = 0;
      let ri = 0;
      mStarList = [];
      const depthsFinal = [];
      for (const r of filteredRows) {
        const depth = Number(r.depth ?? r.DEPTH ?? NaN);
        const rt = Number(r.rt ?? r.RT ?? r.res ?? r.RES ?? NaN);
        const phit = Number(r.phit ?? r.PHIT ?? r.Phit ?? NaN);
        const vclay = Number(r.vclay ?? r.VCLAY ?? r.vcld ?? r.VCLD ?? NaN);
        if (isNaN(rt) || isNaN(phit)) continue;
        const rw = rwResults[ri++] ?? NaN;
        const qv = qvnList[qi++] ?? NaN;
        const b = bList[bi++] ?? NaN;
        if (isNaN(rw) || isNaN(qv) || isNaN(b)) continue;
        const cw = 1 / rw;
        const clayCorrection = 1 + b * qv / cw;
        let mStar = Number(mParam);
        if (phit > 0 && phit < 1 && clayCorrection > 0) {
          mStar = Number(mParam) + Math.log(clayCorrection) / Math.log(phit);
        }
        mStarList.push(mStar);
        finalRows.push({ rt, rw, phit, qv, b, m: mStar, vclay });
        depthsFinal.push(depth);
      }
      if (!finalRows.length) {
        error = "Insufficient data to run Waxman-Smits (need rt, phit, rw, qvn, b)";
        return;
      }
      loading = true;
      error = null;
      waxmanResults = [];
      try {
        const payload = { data: finalRows };
        const res = await fetch(`${API_BASE}/quick_pp/saturation/waxman_smits`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        const out = await res.json();
        waxmanResults = Array.isArray(out) ? out.map((d) => Number(d.SWT ?? d.swt ?? NaN)) : [];
        waxmanChartData = waxmanResults.map((v, i) => ({ depth: depthsFinal[i], SWT: v })).filter((d) => !isNaN(Number(d.depth)));
      } catch (e) {
        console.warn("Waxman-Smits error", e);
        error = String(e?.message ?? e);
      } finally {
        loading = false;
      }
    }
    function updateCwaVclPhiData() {
      for (const r of visibleRows) {
        Number(r.rt ?? r.RT ?? r.res ?? r.RES ?? NaN);
        Number(r.phit ?? r.PHIT ?? r.Phit ?? NaN);
        Number(r.vclay ?? r.VCLAY ?? r.vcld ?? r.VCLD ?? NaN);
      }
    }
    async function saveSaturationResults() {
      if (!projectId || !wellName) {
        error = "Project and well must be selected before saving";
        return;
      }
      const archMap = /* @__PURE__ */ new Map();
      for (const a of archieChartData) {
        const d = Number(a.depth);
        if (!isNaN(d)) archMap.set(d, Number(a.SWT));
      }
      const waxMap = /* @__PURE__ */ new Map();
      for (const w of waxmanChartData) {
        const d = Number(w.depth);
        if (!isNaN(d)) waxMap.set(d, Number(w.SWT));
      }
      const depths = Array.from(/* @__PURE__ */ new Set([...archMap.keys(), ...waxMap.keys()])).sort((a, b) => a - b);
      if (!depths.length) {
        error = "No saturation results to save";
        return;
      }
      const rows = depths.map((d) => {
        const row = { DEPTH: d };
        if (archMap.has(d)) row.SWT_ARCHIE = archMap.get(d);
        if (waxMap.has(d)) row.SWT = waxMap.get(d);
        return row;
      });
      saveLoadingSat = true;
      saveMessageSat = null;
      error = null;
      try {
        const payload = { data: rows };
        const url = `${API_BASE}/quick_pp/database/projects/${projectId}/wells/${encodeURIComponent(String(wellName))}/data`;
        const res = await fetch(url, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        const resp = await res.json().catch(() => null);
        saveMessageSat = resp && resp.message ? String(resp.message) : "Saturation results saved";
        try {
          window.dispatchEvent(new CustomEvent("qpp:data-updated", { detail: { projectId, wellName, kind: "saturation" } }));
        } catch (e) {
        }
      } catch (e) {
        console.warn("Save saturation error", e);
        saveMessageSat = null;
        error = String(e?.message ?? e);
      } finally {
        saveLoadingSat = false;
      }
    }
    function computeStats(arr) {
      const clean = arr.filter((v) => !isNaN(v));
      const count = clean.length;
      if (count === 0) return null;
      const sum = clean.reduce((a, b) => a + b, 0);
      const mean = sum / count;
      const min = Math.min(...clean);
      const max = Math.max(...clean);
      const sorted = clean.slice().sort((a, b) => a - b);
      const median = (sorted[Math.floor((count - 1) / 2)] + sorted[Math.ceil((count - 1) / 2)]) / 2;
      const variance = clean.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / count;
      const std = Math.sqrt(variance);
      return { count, mean, min, max, median, std };
    }
    const unsubscribeWorkspace = workspace.subscribe((w) => {
      if (w?.depthFilter) {
        depthFilter = { ...w.depthFilter };
      }
      if (w?.zoneFilter) {
        zoneFilter = { ...w.zoneFilter };
      }
    });
    onDestroy(() => {
      unsubscribeWorkspace();
      clearMergedDataPollTimer();
    });
    let previousWellKey = "";
    visibleRows = (() => {
      let rows = fullRows || [];
      rows = applyDepthFilter(rows, depthFilter);
      rows = applyZoneFilter(rows, zoneFilter);
      return rows;
    })();
    if (visibleRows) {
      updateCwaVclPhiData();
    }
    {
      const currentKey = `${projectId}_${wellName}`;
      if (projectId && wellName && currentKey !== previousWellKey) {
        previousWellKey = currentKey;
        if (!dataLoaded || !dataCache.has(currentKey)) {
          loadWellData();
        }
      }
    }
    $$renderer2.push(`<div class="ws-saturation"><div class="mb-2"><div class="font-semibold">Water Saturation</div> <div class="text-sm text-muted-foreground">Water saturation calculations and displays.</div></div> `);
    DepthFilterStatus($$renderer2);
    $$renderer2.push(`<!----> `);
    if (wellName) {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="bg-panel rounded p-3">`);
      if (loading) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-sm text-blue-600">${escape_html(pollStatus ? pollStatus : "Loading well log…")}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        if (error) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-sm text-red-500 mb-2">Error: ${escape_html(error)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      }
      $$renderer2.push(`<!--]--> <div class="grid grid-cols-2 gap-2 mb-3"><div><label class="text-sm" for="m-param">Cementation exponent, m</label> <input id="m-param" type="number" class="input"${attr("value", mParam)}/></div> <div><label class="text-sm" for="rw-param">Formation water resistivity, Rw</label> <input id="rw-param" type="number" class="input"${attr("value", rwParam)}/></div></div> <div class="font-medium text-sm mb-1">Pickett Plot</div> <div class="bg-surface rounded p-2"><div class="w-full h-[300px]"></div></div> <div class="font-medium text-sm mb-1 mt-3">Cwa vs Vclay/PHIT Plot</div> <div class="mb-3"><label class="text-sm" for="slope-param">Slope</label> <input id="slope-param" type="number" class="input"${attr("value", slopeParam)}/></div> <div class="bg-surface rounded p-2"><div class="w-full h-[300px]"></div></div> <div class="flex items-center pt-4 space-x-2"><input id="use-slope-for-qv" type="checkbox"${attr("checked", useSlopeForQv, true)}/> <label for="use-slope-for-qv" class="text-sm font-medium">Use slope to calc BQv</label></div> <div class="grid grid-cols-2 gap-2 mb-3"><div><label class="text-sm" for="meas-system">Measurement system</label> `);
      $$renderer2.select({ id: "meas-system", value: measSystem, class: "input" }, ($$renderer3) => {
        $$renderer3.option({ value: "metric" }, ($$renderer4) => {
          $$renderer4.push(`Metric`);
        });
        $$renderer3.option({ value: "imperial" }, ($$renderer4) => {
          $$renderer4.push(`Imperial`);
        });
      });
      $$renderer2.push(`</div> <div><label class="text-sm" for="water-salinity">Water salinity</label> <input id="water-salinity" type="number" class="input"${attr("value", waterSalinity)}/></div></div> <div class="mb-3 flex gap-2 items-center">`);
      Button($$renderer2, {
        class: "btn btn-primary",
        onclick: estimateWaterSaturation,
        disabled: loading,
        style: loading ? "opacity:0.5; pointer-events:none;" : "",
        children: ($$renderer3) => {
          $$renderer3.push(`<!---->Estimate Water Saturation`);
        },
        $$slots: { default: true }
      });
      $$renderer2.push(`<!----> `);
      Button($$renderer2, {
        class: "btn ml-2 bg-emerald-700",
        onclick: saveSaturationResults,
        disabled: loading || saveLoadingSat,
        style: loading || saveLoadingSat ? "opacity:0.5; pointer-events:none;" : "",
        children: ($$renderer3) => {
          if (saveLoadingSat) {
            $$renderer3.push("<!--[-->");
            $$renderer3.push(`Saving...`);
          } else {
            $$renderer3.push("<!--[!-->");
            $$renderer3.push(`Save Saturation`);
          }
          $$renderer3.push(`<!--]-->`);
        },
        $$slots: { default: true }
      });
      $$renderer2.push(`<!----> `);
      if (saveMessageSat) {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="text-xs text-green-600 ml-3">${escape_html(saveMessageSat)}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]--></div> <div class="space-y-3"><div><div class="font-medium text-sm mb-1">TVD Data</div> `);
      if (visibleRows.length) {
        $$renderer2.push("<!--[-->");
        const tvdValues = visibleRows.map((r) => Number(r.tvdss ?? r.TVDSS ?? r.tvd ?? r.TVD ?? r.depth ?? r.DEPTH)).filter((v) => !isNaN(v));
        if (tvdValues.length > 0) {
          $$renderer2.push("<!--[-->");
          const minTvd = Math.min(...tvdValues);
          const maxTvd = Math.max(...tvdValues);
          $$renderer2.push(`<div class="text-sm">Min: ${escape_html(minTvd.toFixed(2))} | Max: ${escape_html(maxTvd.toFixed(2))} | Count: ${escape_html(tvdValues.length)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="text-sm text-gray-500">No TVD/DEPTH data available</div>`);
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="text-sm text-gray-500">No TVD/DEPTH data available</div>`);
      }
      $$renderer2.push(`<!--]--></div> <div><div class="font-medium text-sm mb-1">Temp Gradient</div> `);
      if (tempGradResults.length) {
        $$renderer2.push("<!--[-->");
        const s = computeStats(tempGradResults);
        if (s) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-sm">Avg: ${escape_html(s.mean.toFixed(2))} | Min: ${escape_html(s.min.toFixed(2))} | Max: ${escape_html(s.max.toFixed(2))} | Median: ${escape_html(s.median.toFixed(2))} | Std: ${escape_html(s.std.toFixed(2))} | Count: ${escape_html(s.count)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="text-sm text-gray-500">No temp gradient computed</div>`);
      }
      $$renderer2.push(`<!--]--></div> <div><div class="font-medium text-sm mb-1">Estimated Rw</div> `);
      if (rwResults.length) {
        $$renderer2.push("<!--[-->");
        const s2 = computeStats(rwResults);
        if (s2) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-sm">Avg: ${escape_html(s2.mean.toFixed(3))} | Min: ${escape_html(s2.min.toFixed(3))} | Max: ${escape_html(s2.max.toFixed(3))} | Median: ${escape_html(s2.median.toFixed(3))} | Std: ${escape_html(s2.std.toFixed(3))} | Count: ${escape_html(s2.count)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="text-sm text-gray-500">No Rw computed</div>`);
      }
      $$renderer2.push(`<!--]--></div> `);
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div><div class="font-medium text-sm mb-1">Estimated B</div> `);
        if (bList.length) {
          $$renderer2.push("<!--[-->");
          const sb = computeStats(bList);
          if (sb) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<div class="text-sm">Avg: ${escape_html(sb.mean.toFixed(3))} | Min: ${escape_html(sb.min.toFixed(3))} | Max: ${escape_html(sb.max.toFixed(3))} | Median: ${escape_html(sb.median.toFixed(3))} | Std: ${escape_html(sb.std.toFixed(3))} | Count: ${escape_html(sb.count)}</div>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]-->`);
        } else {
          $$renderer2.push("<!--[!-->");
          $$renderer2.push(`<div class="text-sm text-gray-500">No B computed</div>`);
        }
        $$renderer2.push(`<!--]--></div>`);
      }
      $$renderer2.push(`<!--]--> <div><div class="font-medium text-sm mb-1">Estimated ${escape_html("Qv")}</div> `);
      if (qvnList.length) {
        $$renderer2.push("<!--[-->");
        const sq = computeStats(qvnList);
        if (sq) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-sm">Avg: ${escape_html(sq.mean.toFixed(3))} | Min: ${escape_html(sq.min.toFixed(3))} | Max: ${escape_html(sq.max.toFixed(3))} | Median: ${escape_html(sq.median.toFixed(3))} | Std: ${escape_html(sq.std.toFixed(3))} | Count: ${escape_html(sq.count)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="text-sm text-gray-500">No ${escape_html("Qv")} computed</div>`);
      }
      $$renderer2.push(`<!--]--></div> <div><div class="font-medium text-sm mb-1">Estimated m*</div> `);
      if (mStarList.length) {
        $$renderer2.push("<!--[-->");
        const sm = computeStats(mStarList);
        if (sm) {
          $$renderer2.push("<!--[-->");
          $$renderer2.push(`<div class="text-sm">Avg: ${escape_html(sm.mean.toFixed(3))} | Min: ${escape_html(sm.min.toFixed(3))} | Max: ${escape_html(sm.max.toFixed(3))} | Median: ${escape_html(sm.median.toFixed(3))} | Std: ${escape_html(sm.std.toFixed(3))} | Count: ${escape_html(sm.count)}</div>`);
        } else {
          $$renderer2.push("<!--[!-->");
        }
        $$renderer2.push(`<!--]-->`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div class="text-sm text-gray-500">No m* computed</div>`);
      }
      $$renderer2.push(`<!--]--></div> <div><div class="font-medium text-sm mb-1">Saturation Plot (Archie vs Waxman-Smits)</div> <div class="bg-surface rounded p-2"><div class="h-[220px] w-full overflow-hidden"><div class="w-full h-[220px]"></div></div></div> <div class="text-xs text-muted-foreground-foreground space-y-1 mt-3">`);
      if (archieResults.length > 0) {
        $$renderer2.push("<!--[-->");
        const aVals = archieResults;
        const avgA = aVals.reduce((a, b) => a + b, 0) / aVals.length;
        const minA = Math.min(...aVals);
        const maxA = Math.max(...aVals);
        $$renderer2.push(`<div><strong>Archie SWT:</strong> Avg: ${escape_html(avgA.toFixed(2))} | Min: ${escape_html(minA.toFixed(2))} | Max: ${escape_html(maxA.toFixed(2))} | Count: ${escape_html(aVals.length)}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div><strong>Archie SWT:</strong> No data</div>`);
      }
      $$renderer2.push(`<!--]--> `);
      if (waxmanResults.length > 0) {
        $$renderer2.push("<!--[-->");
        const wVals = waxmanResults;
        const avgW = wVals.reduce((a, b) => a + b, 0) / wVals.length;
        const minW = Math.min(...wVals);
        const maxW = Math.max(...wVals);
        $$renderer2.push(`<div><strong>Waxman-Smits SWT:</strong> Avg: ${escape_html(avgW.toFixed(2))} | Min: ${escape_html(minW.toFixed(2))} | Max: ${escape_html(maxW.toFixed(2))} | Count: ${escape_html(wVals.length)}</div>`);
      } else {
        $$renderer2.push("<!--[!-->");
        $$renderer2.push(`<div><strong>Waxman-Smits SWT:</strong> No data</div>`);
      }
      $$renderer2.push(`<!--]--></div></div></div></div>`);
    } else {
      $$renderer2.push("<!--[!-->");
      $$renderer2.push(`<div class="text-sm">Select a well to view water saturation tools.</div>`);
    }
    $$renderer2.push(`<!--]--></div>`);
    bind_props($$props, { projectId, wellName });
  });
}
function _page($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let selectedProject = null;
    let selectedWell = null;
    const unsubscribe = workspace.subscribe((w) => {
      selectedProject = w?.project ?? null;
      selectedWell = w?.selectedWell ?? null;
    });
    onDestroy(() => unsubscribe());
    ProjectWorkspace($$renderer2, {
      selectedWell,
      project: selectedProject,
      $$slots: {
        left: ($$renderer3) => {
          $$renderer3.push(`<div slot="left">`);
          WsSaturation($$renderer3, {
            projectId: selectedProject?.project_id ?? "",
            wellName: selectedWell?.name ?? ""
          });
          $$renderer3.push(`<!----></div>`);
        }
      }
    });
  });
}

export { _page as default };
//# sourceMappingURL=_page.svelte-CfwIPI3I.js.map
