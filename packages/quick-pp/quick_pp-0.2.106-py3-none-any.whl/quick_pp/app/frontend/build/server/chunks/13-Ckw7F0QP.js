const load = ({ params }) => {
  const projectId = params.project_id ?? null;
  return {
    title: "Well Analysis",
    subtitle: projectId ? `ID: ${projectId}` : void 0
  };
};

var _page_ts = /*#__PURE__*/Object.freeze({
  __proto__: null,
  load: load
});

const index = 13;
let component_cache;
const component = async () => component_cache ??= (await import('./_page.svelte-C9zhtrre.js')).default;
const universal_id = "src/routes/wells/[project_id]/[well_id]/+page.ts";
const imports = ["_app/immutable/nodes/13.hIIpLiVA.js","_app/immutable/chunks/tJ-1PvYF.js","_app/immutable/chunks/BNO5OzLn.js","_app/immutable/chunks/BJMC0GYJ.js","_app/immutable/chunks/lD6GhGUL.js","_app/immutable/chunks/PPVm8Dsz.js","_app/immutable/chunks/DAWgyOON.js"];
const stylesheets = ["_app/immutable/assets/vendor.S5W4ZllZ.css","_app/immutable/assets/DepthFilterStatus.CMzVkwfb.css"];
const fonts = [];

export { component, fonts, imports, index, stylesheets, _page_ts as universal, universal_id };
//# sourceMappingURL=13-Ckw7F0QP.js.map
