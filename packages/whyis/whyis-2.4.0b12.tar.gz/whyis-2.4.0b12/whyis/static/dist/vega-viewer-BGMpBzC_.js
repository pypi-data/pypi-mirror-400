import { n as d, V as p, E as i, l as v, q as o, f as b, k as m, S as u } from "./main-0dzOc6ov.js";
import { V as _ } from "./v-jsoneditor.min-Bvw701If.js";
const f = {};
var y = function() {
  var t = this, e = t._self._c;
  return e("div", [t._v(" ▬▬▬▬▬ ▬▬▬▬ ▬▬▬ ▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬ ▬▬▬▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬ ▬▬ ▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬ ▬▬▬▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬ ▬ ▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬ ▬▬ ▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬ ▬▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬▬ ▬▬▬▬ ▬▬▬ ▬▬▬▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ▬▬▬▬▬▬▬ ▬▬▬▬▬ ▬▬▬▬▬▬ ▬▬ ▬▬▬▬ ▬▬▬▬ ")]);
}, C = [], g = /* @__PURE__ */ d(
  f,
  y,
  C,
  !1,
  null,
  null
);
const w = g.exports, V = p.component("vega-viewer", {
  data() {
    return {
      error: { status: !1, message: null },
      filter: !1,
      loading: !0,
      spec: null,
      chart: null,
      chartTags: [],
      args: null,
      authenticated: i.authUser,
      allowEdit: !1,
      vizOfTheDay: !1,
      specViewer: {
        show: !1,
        includeData: !1,
        jsonEditorOpts: {
          mode: "code",
          mainMenuBar: !1,
          onEditable: () => !1
        }
      }
    };
  },
  components: {
    tempFiller: w,
    VJsoneditor: _
  },
  computed: {
    specViewerSpec() {
      return this.specViewer.includeData ? this.spec : this.chart && this.chart.baseSpec;
    }
  },
  methods: {
    async loadVisualization() {
      if (this.chart = await v(this.pageUri), i.checkIfEditable(this.chart.uri), this.chart.query) {
        const s = await o(this.chart.query);
        this.spec = b(this.chart.baseSpec, s);
      } else
        this.spec = this.chart.baseSpec;
      this.chart.dataset && (this.spec = this.chart.baseSpec, this.spec.data = { url: `/about?uri=${this.chart.dataset}` }), this.loading = !1;
    },
    navBack(s) {
      return s && i.toggleVizOfTheDay(s), i.navTo("view", !0);
    },
    shareChart() {
      return i.$emit("dialoguebox", {
        status: !0,
        share: !0,
        title: "Share Chart",
        message: "Copy the chart link above to share this chart",
        chart: this.chart.uri
      });
    },
    editChart() {
      return m(this.chart.uri, "edit");
    },
    chartQuery() {
      if (this.chart.query)
        return i.$emit("dialoguebox", {
          status: !0,
          query: !0,
          title: "Chart Query",
          message: "Copy and rerun query on a sparql endpoint",
          chart: this.chart.query
        });
    },
    slugify(s) {
      return u(s);
    },
    tableView() {
      this.chart.query && o(this.chart.query).then((s) => (console.log(s), i.$emit("dialoguebox", {
        status: !0,
        tableview: s,
        title: "Table View of Chart Data",
        chart: this.chart.query
      })));
    },
    slugify(s) {
      return u(s);
    }
  },
  beforeMount() {
    return this.loadVisualization();
  },
  destroyed() {
    this.error = { status: !1, message: null };
  },
  created() {
    this.loading = !0, i.$on("isauthenticated", (s) => this.authenticated = s).$on("allowChartEdit", (s) => this.allowEdit = s);
  }
});
var k = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", [e("div", { staticClass: "utility-content__result" }, [t.loading ? t._e() : e("div", { staticClass: "utility-gridicon-single" }, [t.vizOfTheDay ? t._e() : e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "Go Back" }, on: { click: function(a) {
    return a.preventDefault(), t.navBack.apply(null, arguments);
  } } }, [e("i", { staticClass: "bi bi-arrow-left" })])]), e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "Share Chart" }, on: { click: function(a) {
    return a.preventDefault(), t.shareChart.apply(null, arguments);
  } } }, [e("i", { staticClass: "bi bi-share" })])]), t.chart.query ? e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "Preview Chart Query" }, on: { click: function(a) {
    return a.preventDefault(), t.chartQuery.apply(null, arguments);
  } } }, [e("i", { staticClass: "bi bi-eye" })])]) : t._e(), e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "View Data as Table" }, on: { click: function(a) {
    return a.preventDefault(), t.tableView.apply(null, arguments);
  } } }, [e("i", { staticClass: "bi bi-table" })])]), e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "Preview Chart Spec" }, on: { click: function(a) {
    a.preventDefault(), t.specViewer.show = !0;
  } } }, [e("i", { staticClass: "bi bi-code-slash" })])]), t.allowEdit ? e("div", [e("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button", title: "Edit Chart" }, on: { click: function(a) {
    return a.preventDefault(), t.editChart.apply(null, arguments);
  } } }, [e("i", { staticClass: "bi bi-pencil" })])]) : t._e()])]), e("div", { staticClass: "viz-3-col viz-u-mgup-sm" }, [e("div", { staticClass: "loading-dialog__justify" }, [e("div", { staticClass: "viz-sample" }, [t.vizOfTheDay ? e("div", { staticClass: "viz-sample__header viz-u-mgbottom" }, [e("i", { staticClass: "bi bi-bar-chart", staticStyle: { "font-size": "2rem !important", color: "gray !important" } }), t._v(" Viz of the day ")]) : e("div", { staticClass: "viz-u-mgbottom-big viz-u-display__desktop" }), t.vizOfTheDay ? t._e() : e("div", { staticClass: "viz-sample__header viz-u-mgbottom" }, [t._v(" Chart Information ")]), e("div", { staticClass: "viz-sample__content" }, [t.loading ? e("temp-filler", { staticClass: "viz-sample__loading viz-sample__loading_anim" }) : e("div", {}, [e("h3", { staticClass: "h4 viz-u-mgup-sm btn--animated" }, [t._v(t._s(t.chart.title))]), e("div", { staticClass: "btn--animated" }, [t._v(" " + t._s(t.slugify(t.chart.description)) + " ")]), e("div", { staticClass: "viz-sample__list btn--animated" }, [e("ul", t._l(t.chartTags, function(a, r) {
    return e("li", { key: r, staticClass: "viz-u-postion__rel" }, [e("div", { staticClass: "viz-sample__content__card viz-u-display__hide viz-u-postion__abs" }, [t._v(" " + t._s(a.description) + " "), e("div", [e("a", { staticClass: "btn-text btn-text--simple", attrs: { target: "_blank", href: a.uri } }, [t._v("More")])])]), t._v(" " + t._s(a.title) + " ")]);
  }), 0)]), t.vizOfTheDay ? e("a", { staticClass: "btn btn_medium btn--primary viz-u-display__desktop btn--animated", on: { click: function(a) {
    return a.preventDefault(), t.navBack(!0);
  } } }, [t._v("View Gallery")]) : t._e()])], 1)])]), t.loading ? e("div", { staticClass: "loading-dialog", staticStyle: { margin: "auto" } }, [e("spinner", { attrs: { loading: t.loading } })], 1) : e("div", { staticClass: "loading-dialog", staticStyle: { margin: "auto" } }, [e("div", { staticClass: "viz-u-display__desktop", staticStyle: { "margin-bottom": "2rem" } }), e("vega-lite", { staticClass: "btn--animated", attrs: { spec: t.spec } }), t.vizOfTheDay ? e("a", { staticClass: "btn btn_small btn--primary utility-margin-big viz-u-display__ph", on: { click: function(a) {
    return a.preventDefault(), t.navBack(!0);
  } } }, [t._v("View Gallery")]) : t._e()], 1), t.specViewer.show ? e("div", { staticClass: "modal fade", class: { show: t.specViewer.show }, style: { display: t.specViewer.show ? "block" : "none" }, attrs: { tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog modal-xl" }, [e("div", { staticClass: "modal-content" }, [e("div", { staticClass: "modal-header" }, [e("h5", { staticClass: "modal-title" }, [t._v("Chart Vega Spec")]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: function(a) {
    t.specViewer.show = !1;
  } } })]), e("div", { staticClass: "modal-body" }, [e("div", { staticClass: "vega-spec-container" }, [e("v-jsoneditor", { attrs: { options: t.specViewer.jsonEditorOpts }, model: { value: t.specViewerSpec, callback: function(a) {
    t.specViewerSpec = a;
  }, expression: "specViewerSpec" } })], 1)]), e("div", { staticClass: "modal-footer d-flex justify-content-between" }, [e("div", { staticClass: "form-check" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.specViewer.includeData, expression: "specViewer.includeData" }], staticClass: "form-check-input", attrs: { type: "checkbox", id: "includeDataCheck" }, domProps: { checked: Array.isArray(t.specViewer.includeData) ? t._i(t.specViewer.includeData, null) > -1 : t.specViewer.includeData }, on: { change: function(a) {
    var r = t.specViewer.includeData, n = a.target, h = !!n.checked;
    if (Array.isArray(r)) {
      var c = null, l = t._i(r, c);
      n.checked ? l < 0 && t.$set(t.specViewer, "includeData", r.concat([c])) : l > -1 && t.$set(t.specViewer, "includeData", r.slice(0, l).concat(r.slice(l + 1)));
    } else
      t.$set(t.specViewer, "includeData", h);
  } } }), e("label", { staticClass: "form-check-label", attrs: { for: "includeDataCheck" } }, [t._v(" Include data in spec ")])]), e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(a) {
    t.specViewer.show = !1;
  } } }, [t._v("Close")])])])])]) : t._e()])]);
}, z = [], D = /* @__PURE__ */ d(
  V,
  k,
  z,
  !1,
  null,
  "600df06f"
);
const x = D.exports;
export {
  x as default
};
