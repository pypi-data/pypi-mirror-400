import { ak as fallback, o as onDestroy, s as store_get, a as attr, aj as attr_style, u as unsubscribe_stores, c as bind_props, i as stringify } from './error.svelte-DqMYEJMd.js';
import { d as depthFilter, z as zoneFilter } from './workspace-DPIadIP6.js';
import { D as DepthFilterStatus } from './DepthFilterStatus-09LDbYxV.js';

function WsWellPlot($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    var $$store_subs;
    let projectId = $$props["projectId"];
    let wellName = $$props["wellName"];
    let container = null;
    let minWidth = fallback($$props["minWidth"], "480px");
    let loading = false;
    let autoRefresh = false;
    let _refreshTimer = null;
    let lastDepthFilter = null;
    let lastZoneFilter = null;
    function clearPollTimer(session) {
    }
    onDestroy(() => {
      try {
        if (container && container._plotlyResizeObserver) ;
        if (_refreshTimer) {
          clearInterval(_refreshTimer);
          _refreshTimer = null;
        }
        clearPollTimer();
      } catch (e) {
      }
    });
    if (store_get($$store_subs ??= {}, "$depthFilter", depthFilter) && JSON.stringify(store_get($$store_subs ??= {}, "$depthFilter", depthFilter)) !== JSON.stringify(lastDepthFilter)) {
      lastDepthFilter = {
        ...store_get($$store_subs ??= {}, "$depthFilter", depthFilter)
      };
    }
    if (store_get($$store_subs ??= {}, "$zoneFilter", zoneFilter) && JSON.stringify(store_get($$store_subs ??= {}, "$zoneFilter", zoneFilter)) !== JSON.stringify(lastZoneFilter)) {
      lastZoneFilter = {
        ...store_get($$store_subs ??= {}, "$zoneFilter", zoneFilter)
      };
    }
    $$renderer2.push(`<div class="ws-well-plot">`);
    DepthFilterStatus($$renderer2);
    $$renderer2.push(`<!----> <div class="mb-2 flex items-center gap-2"><button class="btn px-3 py-1 text-sm bg-gray-800 text-white rounded" aria-label="Refresh plot"${attr(
      "disabled",
      // Trigger initial render now that the DOM is ready
      // ignore
      // Listen for updates dispatched from other components (e.g., save actions)
      // Only refresh if the event refers to the same project/well
      // Force refresh when data is updated
      // remove listener on destroy
      loading,
      true
    )}>Refresh</button> <label class="text-sm flex items-center gap-1"><input type="checkbox"${attr("checked", autoRefresh, true)}/> Auto-refresh</label> `);
    {
      $$renderer2.push("<!--[!-->");
    }
    $$renderer2.push(`<!--]--></div> `);
    {
      $$renderer2.push("<!--[!-->");
      {
        $$renderer2.push("<!--[!-->");
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--> <div${attr_style(`width:100%; min-width: ${stringify(minWidth)}; height:900px;`)}></div></div>`);
    if ($$store_subs) unsubscribe_stores($$store_subs);
    bind_props($$props, { projectId, wellName, minWidth });
  });
}

export { WsWellPlot as default };
//# sourceMappingURL=WsWellPlot-DL2reMkT.js.map
