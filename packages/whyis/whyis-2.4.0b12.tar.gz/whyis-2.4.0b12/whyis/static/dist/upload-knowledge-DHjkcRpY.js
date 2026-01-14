import { V as d, c as m, n as c } from "./main-0dzOc6ov.js";
var n = [
  { mimetype: "application/rdf+xml", name: "RDF/XML", extensions: ["rdf"] },
  { mimetype: "application/ld+json", name: "JSON-LD", extensions: ["json", "jsonld"] },
  { mimetype: "text/turtle", name: "Turtle", extensions: ["ttl"] },
  { mimetype: "application/trig", name: "TRiG", extensions: ["trig"] },
  { mimetype: "application/n-quads", name: "n-Quads", extensions: ["nq", "nquads"] },
  { mimetype: "application/n-triples", name: "N-Triples", extensions: ["nt", "ntriples"] }
], i = {};
n.forEach(function(a) {
  i[a.name] = a;
});
const f = d.component("upload-knowledge", {
  data: function() {
    return {
      formats: n,
      file: { name: "" },
      format_map: i,
      format: null,
      fileobj: "",
      status: !1,
      showRDFUpload: !1,
      modalInstance: null
    };
  },
  methods: {
    onSubmitRDF() {
      this.save().then(() => {
        window.location.reload();
      }).catch((a) => {
        console.error("Upload failed:", a);
      });
    },
    handleFileUpload(a) {
      console.log(a), this.fileobj = a.target.files[0], this.file.name = a.target.files[0] ? a.target.files[0].name : "";
    },
    async save() {
      let a = this.format;
      if (a == null) {
        let t = this.formats.filter((e) => e.extensions.filter((s) => this.fileobj.name.endsWith(s)));
        t.length > 0 && (console.log("setting format", t[0]), a = t[0]);
      } else
        a = this.format_map[this.format];
      console.log(this.format);
      try {
        const t = {
          method: "post",
          url: `${ROOT_URL}pub`,
          data: this.fileobj,
          headers: { "Content-Type": a.mimetype }
        };
        return console.log(t), m(t);
      } catch (t) {
        return alert(t);
      }
    }
  }
});
var p = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", { staticClass: "modal fade", attrs: { id: "uploadKnowledgeModal", tabindex: "-1", "aria-labelledby": "uploadKnowledgeModalLabel", "aria-hidden": "true" } }, [e("div", { staticClass: "modal-dialog" }, [e("div", { staticClass: "modal-content" }, [t._m(0), e("div", { staticClass: "modal-body" }, [e("h6", [t._v("Upload RDF Knowledge")]), e("div", { staticClass: "mb-3" }, [e("label", { staticClass: "form-label", attrs: { for: "rdfFile" } }, [t._v("RDF File")]), e("input", { staticClass: "form-control", attrs: { type: "file", id: "rdfFile", accept: ".rdf,.json,.jsonld,.ttl,.trig,.nq,.nquads,.nt,.ntriples" }, on: { change: function(s) {
    return t.handleFileUpload(s);
  } } }), e("div", { staticClass: "form-text" }, [t._v("Upload Knowledge in RDF")])]), e("div", { staticClass: "mb-3" }, [e("label", { staticClass: "form-label", attrs: { for: "format" } }, [t._v("Format")]), e("select", { directives: [{ name: "model", rawName: "v-model", value: t.format, expression: "format" }], staticClass: "form-select", attrs: { id: "format", required: "" }, on: { change: function(s) {
    var o = Array.prototype.filter.call(s.target.options, function(l) {
      return l.selected;
    }).map(function(l) {
      var r = "_value" in l ? l._value : l.value;
      return r;
    });
    t.format = s.target.multiple ? o : o[0];
  } } }, [e("option", { attrs: { value: "" } }, [t._v("Format")]), t._l(t.formats, function(s) {
    return e("option", { key: s.name, domProps: { value: s.name } }, [t._v(t._s(s.name))]);
  })], 2)])]), t.showRDFUpload ? t._e() : e("div", { staticClass: "modal-footer" }, [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button", "data-bs-dismiss": "modal" } }, [t._v(" Cancel ")]), e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: t.onSubmitRDF } }, [t._v(" Upload ")])])])])]);
}, u = [function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("div", { staticClass: "modal-header" }, [t("h5", { staticClass: "modal-title", attrs: { id: "uploadKnowledgeModalLabel" } }, [a._v("Upload Knowledge")]), t("button", { staticClass: "btn-close", attrs: { type: "button", "data-bs-dismiss": "modal", "aria-label": "Close" } })]);
}], _ = /* @__PURE__ */ c(
  f,
  p,
  u,
  !1,
  null,
  null
);
const b = _.exports;
export {
  b as default
};
