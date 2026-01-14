import { V as a, E as t, n as r } from "./main-0dzOc6ov.js";
const s = a.component("vega-sparql", {
  data() {
    return {
      loading: !1
    };
  },
  mounted() {
    YASGUI(document.getElementById("yasgui"), {
      yasqe: {
        sparql: {
          endpoint: "{{endpoint}}",
          requestMethod: "POST"
        }
      },
      yasr: {
        table: {
          fetchTitlesFromPrefLabel: !1
        }
      }
    });
  },
  created() {
    if (t.authUser == null)
      return t.navTo("view", !0);
  }
});
var o = function() {
  var e = this, n = e._self._c;
  return e._self._setupProxy, n("div", { attrs: { id: "yasgui" } });
}, l = [], i = /* @__PURE__ */ r(
  s,
  o,
  l,
  !1,
  null,
  null
);
const c = i.exports;
export {
  c as default
};
