import { V as o, n as t } from "./main-0dzOc6ov.js";
const a = o.component("accordion", {
  props: {
    startOpen: {
      type: Boolean,
      default: () => !1
    },
    title: {
      type: String
    }
  },
  data() {
    return {
      open: this.startOpen
    };
  },
  methods: {
    toggleOpen() {
      this.open = !this.open;
    }
  }
});
var n = function() {
  var e = this, s = e._self._c;
  return e._self._setupProxy, s("div", { staticClass: "accordion" }, [s("div", { staticClass: "accordion-header bg-light border", on: { click: e.toggleOpen } }, [s("div", { staticClass: "accordion-toolbar-row p-3" }, [s("h3", { staticClass: "h5 mb-0" }, [e._v(e._s(e.title))]), s("div", { staticClass: "accordion-icons" }, [s("i", { directives: [{ name: "show", rawName: "v-show", value: !e.open, expression: "!open" }], staticClass: "bi bi-chevron-down" }), s("i", { directives: [{ name: "show", rawName: "v-show", value: e.open, expression: "open" }], staticClass: "bi bi-chevron-up" })])])]), e.open ? s("div", { staticClass: "accordion-content border border-top-0" }, [s("div", { staticClass: "p-3" }, [e._t("default")], 2)]) : e._e()]);
}, i = [], r = /* @__PURE__ */ t(
  a,
  n,
  i,
  !1,
  null,
  "ffe1ce81"
);
const p = r.exports;
export {
  p as default
};
