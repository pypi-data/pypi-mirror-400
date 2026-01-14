import { V as n, E as a, v as r, n as l } from "./main-0dzOc6ov.js";
const o = n.component("vega-gallery", {
  data() {
    return {
      filter: !1,
      bottomPosition: "bottom-0 end-0",
      speedDials: a.speedDials,
      authenticated: a.authUser,
      existingBkmk: {
        status: !1
      }
    };
  },
  components: {
    vizGrid: r
  },
  mounted() {
    return this.showIntro();
  },
  methods: {
    showIntro(i) {
      return a.tipController(i);
    },
    showFilterBox() {
      return a.$emit("open-filter-box", { open: !0, type: "filter" }), this.filter = !0;
    },
    newChart() {
      return a.navTo("new", !0);
    },
    cancelFilter() {
      return a.cancelChartFilter();
    }
  },
  created() {
    a.$on("close-filter-box", (i) => this.filter = i).$on("isauthenticated", (i) => this.authenticated = i).$on("gotexistingbookmarks", (i) => this.existingBkmk = i);
  }
});
var c = function() {
  var e = this, t = e._self._c;
  return e._self._setupProxy, t("div", [e.existingBkmk.status ? t("div", [t("spinner", { attrs: { loading: e.existingBkmk.status, text: e.existingBkmk.text } })], 1) : t("div", [t("viz-grid", { attrs: { authenticated: e.authenticated, instancetype: "http://semanticscience.org/resource/Chart" } }), e.speedDials ? t("div", { staticClass: "position-fixed bottom-0 end-0 p-3" }, [t("div", { staticClass: "dropdown dropup" }, [e._m(0), t("ul", { staticClass: "dropdown-menu dropdown-menu-end" }, [t("li", [t("a", { staticClass: "dropdown-item d-flex align-items-center", attrs: { href: "#", "data-bs-toggle": "tooltip", "data-bs-placement": "left", title: "Cancel Filter" }, on: { click: function(s) {
    return s.preventDefault(), e.cancelFilter.apply(null, arguments);
  } } }, [t("i", { staticClass: "bi bi-search-heart utility-color me-2" }), t("span", [e._v("Cancel Filter")])])]), t("li", [t("a", { staticClass: "dropdown-item d-flex align-items-center", attrs: { href: "#", "data-bs-toggle": "tooltip", "data-bs-placement": "left", title: "Filter" }, on: { click: e.showFilterBox } }, [t("i", { staticClass: "bi bi-search utility-color me-2" }), t("span", [e._v("Filter")])])]), t("li", [t("a", { staticClass: "dropdown-item d-flex align-items-center", attrs: { href: "#", "data-bs-toggle": "tooltip", "data-bs-placement": "left", title: "Replay Tips" }, on: { click: function(s) {
    return s.preventDefault(), e.showIntro(!0);
  } } }, [t("i", { staticClass: "bi bi-info-circle utility-color me-2" }), t("span", [e._v("Replay Tips")])])]), e.authenticated !== void 0 ? t("li", [t("a", { staticClass: "dropdown-item d-flex align-items-center", attrs: { href: "#", "data-bs-toggle": "tooltip", "data-bs-placement": "left", title: "Create New Chart" }, on: { click: function(s) {
    return s.preventDefault(), e.newChart.apply(null, arguments);
  } } }, [t("i", { staticClass: "bi bi-plus-circle utility-color me-2" }), t("span", [e._v("Create New Chart")])])]) : e._e()])])]) : e._e()], 1)]);
}, d = [function() {
  var i = this, e = i._self._c;
  return i._self._setupProxy, e("button", { staticClass: "btn btn-primary rounded-circle p-3 utility-float-icon", staticStyle: { width: "56px", height: "56px" }, attrs: { type: "button", "data-bs-toggle": "dropdown", "aria-expanded": "false" } }, [e("i", { staticClass: "bi bi-list" })]);
}], p = /* @__PURE__ */ l(
  o,
  c,
  d,
  !1,
  null,
  null
);
const m = p.exports;
export {
  m as default
};
