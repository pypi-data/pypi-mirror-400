import { V as r, n as l } from "./main-0dzOc6ov.js";
const n = r.component("yasr", {
  props: {
    id: {
      type: String,
      default: () => "YASR"
    },
    results: {
      type: Object,
      default: () => null
    }
  },
  methods: {
    setResults(s) {
      s && this.yasr.setResponse(s);
    }
  },
  mounted() {
    this.yasr = window.YASR(this.$el, {
      outputPlugins: ["table"],
      useGoogleCharts: !1,
      persistency: {
        results: {
          key: () => !1
        }
      }
    }), this.setResults(this.results);
  },
  watch: {
    results(s, e) {
      this.setResults(s);
    }
  }
});
var a = function() {
  var e = this, t = e._self._c;
  return e._self._setupProxy, t("div", { attrs: { id: e.id } });
}, o = [], i = /* @__PURE__ */ l(
  n,
  a,
  o,
  !1,
  null,
  null
);
const _ = i.exports;
export {
  _ as default
};
