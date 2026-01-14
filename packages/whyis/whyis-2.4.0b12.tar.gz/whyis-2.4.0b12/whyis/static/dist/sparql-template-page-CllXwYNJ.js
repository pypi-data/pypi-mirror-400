import { q as T, x as E, y as v, i as I, k as S, D as q, o as C, n as w } from "./main-0dzOc6ov.js";
import { d as x } from "./debounce-BezZ7Sd5.js";
const R = "http://www.w3.org/1999/02/22-rdf-syntax-ns#", O = "http://www.w3.org/2000/01/rdf-schema#", u = "http://schema.org/";
loadSparqlTemplatesQuery = `
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX sp: <http://spinrdf.org/sp>
PREFIX spin: <http://spinrdf.org/spin#>
PREFIX spl: <http://spinrdf.org/spin#>
PREFIX whyis: <http://vocab.rpi.edu/whyis/>
PREFIX nanomine_templates: <http://nanomine.org/query/>

CONSTRUCT {
    ?template a whyis:SparqlTemplate  ;
        spin:labelTemplate ?labelTemplate ;
        sp:text ?query ;
        spin:constraint ?constraint .
    ?constraint sp:varName ?varName ;
        schema:option ?option .
    ?option rdfs:label ?optLabel ;
        schema:value ?optValue ;
        schema:identifier ?optId ;
        schema:position ?optPosition .
}
WHERE {
    ?template a whyis:SparqlTemplate  ;
        spin:labelTemplate ?labelTemplate ;
        sp:text ?query ;
        spin:constraint ?constraint .
    ?constraint sp:varName ?varName ;
        schema:option ?option .
    ?option rdfs:label ?optLabel ;
        schema:position ?optPosition .
    OPTIONAL { ?option schema:value ?optValue } .
    OPTIONAL { ?option schema:identifier ?optId } .
}
`;
const y = "http://spinrdf.org/sp", f = `${y}in#`, N = "http://vocab.rpi.edu/whyis/SparqlTemplate", j = R + "type";
async function P() {
  const s = await T(loadSparqlTemplatesQuery), e = {}, t = [];
  s.results.bindings.forEach((a) => {
    const r = a.subject.value, o = a.predicate.value;
    let p = a.object.value;
    a.object.type === "literal" && a.object.datatype && (p = E.fromRdf(v.literal(p, v.namedNode(a.object.datatype)))), o === j && p === N && t.push(r);
    let c = e[r];
    c || (c = {}, e[r] = c);
    let d = c[o];
    d || (d = /* @__PURE__ */ new Set(), c[o] = d), d.add(p);
  });
  const i = t.map((a) => l(a)).map(V);
  return i.sort((a, r) => a.id > r.id ? 1 : -1), i;
  function l(a, r) {
    if (r = r || /* @__PURE__ */ new Set(), r.has(a) || !e.hasOwnProperty(a))
      return a;
    r.add(a);
    const o = e[a], p = { uri: a };
    return Object.entries(o).forEach(([c, d]) => {
      const _ = [...d].map((g) => l(g, r));
      p[c] = _;
    }), p;
  }
}
const h = Object.freeze({
  VAR: "var",
  TEXT: "text"
}), m = Object.freeze({
  ANY: "any",
  LITERAL: "literal",
  IDENTIFIER: "identifier"
});
function V(s) {
  const e = s[`${f}labelTemplate`][0];
  return {
    id: s.uri,
    display: e,
    displaySegments: F(e),
    SPARQL: s[`${y}text`][0],
    options: $(s[`${f}constraint`])
  };
}
function $(s) {
  return Object.fromEntries(
    s.map((e) => [
      e[`${y}varName`][0],
      L(e[`${u}option`])
    ])
  );
}
function L(s) {
  return Object.fromEntries(
    s.map((e) => [
      e[`${O}label`][0],
      A(e),
      e[`${u}position`][0]
    ]).sort((e, t) => e[2] > t[2] ? 1 : -1)
  );
}
function A(s) {
  let e = {
    type: m.ANY
  };
  return s[`${u}value`] ? (s[`${u}value`], e = {
    type: m.LITERAL,
    value: s[`${u}value`][0]
  }) : s[`${u}identifier`] && (e = {
    type: m.IDENTIFIER,
    value: s[`${u}identifier`][0]
  }), e;
}
const b = /{\?([^}]+)}/g, Q = new RegExp(`${b.source}|[^{]+`, "g");
function F(s) {
  return s.match(Q).map((e) => {
    let t;
    const n = b.exec(e);
    return n ? t = {
      type: h.VAR,
      varName: n[1]
    } : t = {
      type: h.TEXT,
      text: e
    }, t;
  });
}
const k = {
  data() {
    return {
      loadingTemplates: !0,
      queryTemplates: {},
      TextSegmentType: h,
      selTemplateId: null,
      query: "",
      varSelections: {},
      results: null,
      execQueryDebounced: x(this.execQuery, 300)
    };
  },
  computed: {
    templateIds() {
      return Object.keys(this.queryTemplates);
    },
    selectedTemplate() {
      return this.queryTemplates[this.selTemplateId];
    },
    currentIndex() {
      return this.templateIds.indexOf(this.selTemplateId);
    },
    totalTemplateCount() {
      return this.templateIds.length;
    }
  },
  methods: {
    ...I("vizEditor", ["setQuery"]),
    selectQueryForVizEditor() {
      this.setQuery(this.query), this.toVizEditor();
    },
    toVizEditor() {
      S(C.CHART_EDITOR, q.NEW);
    },
    async loadSparqlTemplates() {
      this.loadingTemplates = !0;
      try {
        const s = await P();
        this.queryTemplates = {}, s.forEach((e) => this.queryTemplates[e.id] = e), console.log("qtemps", this.queryTemplates), this.selTemplateId = s.length > 0 ? s[0].id : null;
      } finally {
        this.loadingTemplates = !1;
      }
    },
    shiftTemplate(s) {
      let e = this.currentIndex + s;
      for (; e >= this.totalTemplateCount; )
        e -= this.totalTemplateCount;
      for (; e < 0; )
        e += this.totalTemplateCount;
      this.selTemplateId = this.templateIds[e], console.log("shifted", e, this.selTemplateId, this.templateIds);
    },
    populateSelections() {
      this.selectedTemplate && (this.varSelections = Object.fromEntries(
        Object.entries(
          this.selectedTemplate.options
        ).map(([s, e]) => [s, Object.keys(e)[0]])
      ));
    },
    getOptVal(s, e) {
      return this.selectedTemplate.options[s][e];
    },
    buildQuery() {
      if (!this.selectedTemplate)
        return;
      this.query = this.selectedTemplate.SPARQL, this.selectedTemplate.options;
      const s = Object.fromEntries(
        Object.entries(this.varSelections).filter((e) => this.getOptVal(...e).type !== m.ANY)
      );
      if (Object.keys(s).length > 0) {
        const e = Object.keys(s).map((n) => `?${n}`).join(" "), t = Object.entries(s).map((n) => {
          const i = this.getOptVal(...n);
          let l;
          if (i.type === m.LITERAL)
            l = i.value, typeof l != "number" && (l = `"${l}"`);
          else if (i.type === m.IDENTIFIER)
            l = `<${i.value}>`;
          else
            throw `Unknown option value type: ${i.type}`;
          return l;
        }).join(" ");
        this.query += `
VALUES (${e}) {
  (${t})
}
`;
      }
    },
    async execQuery() {
      console.log("querying...."), this.results = null, this.results = await T(this.query), console.log("done", this.results);
    }
  },
  created() {
    this.loadSparqlTemplates();
  },
  watch: {
    // The following reactive watchers are used due to limitations of not being
    // able to deep watch dependencies of computed methods.
    selectedTemplate: {
      handler: "populateSelections"
    },
    varSelections: {
      handler: "buildQuery",
      deep: !0
    },
    query: {
      handler: "execQueryDebounced"
    }
  }
};
var D = function() {
  var e = this, t = e._self._c;
  return t("div", { staticClass: "sparql-template-page" }, [e.loadingTemplates ? t("div", [e._m(0)]) : e.totalTemplateCount === 0 ? t("div", [t("p", [e._v("No templates were loaded")])]) : t("div", [t("div", { staticClass: "button-row" }, [t("div", { staticClass: "d-flex gap-2" }, [t("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button" }, on: { click: function(n) {
    return n.preventDefault(), e.selectQueryForVizEditor();
  } } }, [t("i", { staticClass: "bi bi-check" }), t("span", { staticClass: "visually-hidden" }, [e._v("Select current query and return to Viz Editor")])]), t("button", { staticClass: "btn btn-outline-secondary btn-sm", attrs: { type: "button" }, on: { click: function(n) {
    return n.preventDefault(), e.toVizEditor();
  } } }, [t("i", { staticClass: "bi bi-arrow-left" }), t("span", { staticClass: "visually-hidden" }, [e._v("Return to viz editor")])])])]), e._m(1), t("div", { staticClass: "display" }, [t("button", { staticClass: "btn btn-outline-secondary template-back", attrs: { type: "button" }, on: { click: function(n) {
    return e.shiftTemplate(-1);
  } } }, [t("i", { staticClass: "bi bi-chevron-left" })]), t("button", { staticClass: "btn btn-outline-secondary template-next", attrs: { type: "button" }, on: { click: function(n) {
    return e.shiftTemplate(1);
  } } }, [t("i", { staticClass: "bi bi-chevron-right" })]), t("p", { staticClass: "display-text" }, e._l(e.selectedTemplate.displaySegments, function(n, i) {
    return t("span", { key: i }, [n.type == e.TextSegmentType.TEXT ? t("span", { domProps: { innerHTML: e._s(n.text) } }) : t("span", [t("select", { directives: [{ name: "model", rawName: "v-model", value: e.varSelections[n.varName], expression: "varSelections[segment.varName]" }], attrs: { id: n.varName, name: n.varName }, on: { change: function(l) {
      var a = Array.prototype.filter.call(l.target.options, function(r) {
        return r.selected;
      }).map(function(r) {
        var o = "_value" in r ? r._value : r.value;
        return o;
      });
      e.$set(e.varSelections, n.varName, l.target.multiple ? a : a[0]);
    } } }, e._l(e.selectedTemplate.options[n.varName], function(l, a) {
      return t("option", { key: a, domProps: { value: a } }, [e._v(" " + e._s(a) + " ")]);
    }), 0)])]);
  }), 0)]), t("div", { staticClass: "display-count-indicator" }, [t("p", [e._v("Query template " + e._s(e.currentIndex + 1) + " of " + e._s(e.totalTemplateCount))])]), e.query ? t("div", { staticClass: "query" }, [t("accordion", { attrs: { startOpen: !1, title: "SPARQL Query" } }, [t("yasqe", { attrs: { value: e.query, readonly: "true" } })], 1)], 1) : e._e(), t("div", { staticClass: "results" }, [t("accordion", { attrs: { startOpen: !0, title: "SPARQL Results" } }, [e.results ? t("div", [t("yasr", { attrs: { results: e.results } })], 1) : t("div", { staticClass: "text-center" }, [t("div", { staticClass: "spinner-border", attrs: { role: "status" } }, [t("span", { staticClass: "visually-hidden" }, [e._v("Loading...")])])])])], 1)])]);
}, z = [function() {
  var s = this, e = s._self._c;
  return e("div", { staticClass: "text-center" }, [e("div", { staticClass: "spinner-border", attrs: { role: "status" } }, [e("span", { staticClass: "visually-hidden" }, [s._v("Loading...")])])]);
}, function() {
  var s = this, e = s._self._c;
  return e("div", { staticClass: "bg-primary text-white p-3 mb-3" }, [e("h3", { staticClass: "h5 mb-0" }, [s._v("Query Template")])]);
}], X = /* @__PURE__ */ w(
  k,
  D,
  z,
  !1,
  null,
  "b72e9ec9"
);
const H = X.exports;
export {
  H as default
};
