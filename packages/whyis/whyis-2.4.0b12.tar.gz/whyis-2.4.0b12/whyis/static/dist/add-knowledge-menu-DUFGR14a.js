import { V as e, n as i } from "./main-0dzOc6ov.js";
const a = e.component("add-knowledge-menu", {
  props: ["uri"],
  data: function() {
    return {
      whichAdd: ""
    };
  }
});
var o = function() {
  var t = this, d = t._self._c;
  return t._self._setupProxy, d("div", [d("div", { staticClass: "dropdown" }, [d("button", { staticClass: "btn btn-outline-primary dropdown-toggle", attrs: { type: "button", id: "addKnowledgeMenu", "data-bs-toggle": "dropdown", "aria-expanded": "false" }, on: { click: function(n) {
    t.whichAdd = "";
  } } }, [d("i", { staticClass: "bi bi-list" })]), d("ul", { staticClass: "dropdown-menu", attrs: { "aria-labelledby": "addKnowledgeMenu" } }, [d("li", [d("button", { staticClass: "dropdown-item", attrs: { type: "button" }, on: { click: function(n) {
    t.whichAdd = "addLink";
  } } }, [t._v("Add Link")])]), d("li", [d("button", { staticClass: "dropdown-item", attrs: { type: "button" }, on: { click: function(n) {
    t.whichAdd = "addType";
  } } }, [t._v("Add Type")])]), d("li", [d("button", { staticClass: "dropdown-item", attrs: { type: "button" }, on: { click: function(n) {
    t.whichAdd = "addAttribute";
  } } }, [t._v("Add Attribute")])])])]), t.whichAdd == "addLink" ? d("add-link", { attrs: { uri: t.uri, hideButton: "true" } }) : t._e(), t.whichAdd == "addType" ? d("add-type", { attrs: { uri: t.uri, hideButton: "true" } }) : t._e(), t.whichAdd == "addAttribute" ? d("add-attribute", { attrs: { uri: t.uri, hideButton: "true" } }) : t._e()], 1);
}, r = [], s = /* @__PURE__ */ i(
  a,
  o,
  r,
  !1,
  null,
  null
);
const l = s.exports;
export {
  l as default
};
