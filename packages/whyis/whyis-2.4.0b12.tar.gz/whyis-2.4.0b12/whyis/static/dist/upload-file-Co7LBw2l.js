import { V as l, n as s } from "./main-0dzOc6ov.js";
const i = l.component("upload-file", {
  props: ["active", "label"],
  data: function() {
    return {
      upload_type: "http://purl.org/net/provenance/ns#File"
    };
  },
  methods: {
    // Create dialog boxes
    showDialogBox() {
      this.$emit("update:active", !0);
    },
    resetDialogBox() {
      this.$emit("update:active", !1);
    },
    onCancel() {
      return this.resetDialogBox();
    },
    onSubmit() {
      return this.save().then(() => window.location.reload()), this.resetDialogBox();
    }
  }
});
var n = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, t.active ? e("div", { staticClass: "modal fade", class: { show: t.active }, style: { display: t.active ? "block" : "none" }, attrs: { tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog" }, [e("div", { staticClass: "modal-content" }, [e("div", { staticClass: "modal-header" }, [e("h5", { staticClass: "modal-title" }, [t._v("Upload File for " + t._s(t.label))]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.resetDialogBox } })]), e("div", { staticClass: "modal-body" }, [e("form", { staticStyle: { margin: "2em" }, attrs: { id: "upload_form", enctype: "multipart/form-data", novalidate: "", method: "post", action: "" } }, [e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "form-check" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.upload_type, expression: "upload_type" }], staticClass: "form-check-input", attrs: { type: "radio", name: "upload_type", id: "singleFile", value: "http://purl.org/net/provenance/ns#File", checked: "" }, domProps: { checked: t._q(t.upload_type, "http://purl.org/net/provenance/ns#File") }, on: { change: function(o) {
    t.upload_type = "http://purl.org/net/provenance/ns#File";
  } } }), e("label", { staticClass: "form-check-label", attrs: { for: "singleFile" } }, [t._v(" Single File ")])]), e("div", { staticClass: "form-check" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.upload_type, expression: "upload_type" }], staticClass: "form-check-input", attrs: { type: "radio", name: "upload_type", id: "collection", value: "http://purl.org/dc/dcmitype/Collection" }, domProps: { checked: t._q(t.upload_type, "http://purl.org/dc/dcmitype/Collection") }, on: { change: function(o) {
    t.upload_type = "http://purl.org/dc/dcmitype/Collection";
  } } }), e("label", { staticClass: "form-check-label", attrs: { for: "collection" } }, [t._v(" Collection ")])]), e("div", { staticClass: "form-check" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.upload_type, expression: "upload_type" }], staticClass: "form-check-input", attrs: { type: "radio", name: "upload_type", id: "dataset", value: "http://www.w3.org/ns/dcat#Dataset" }, domProps: { checked: t._q(t.upload_type, "http://www.w3.org/ns/dcat#Dataset") }, on: { change: function(o) {
    t.upload_type = "http://www.w3.org/ns/dcat#Dataset";
  } } }), e("label", { staticClass: "form-check-label", attrs: { for: "dataset" } }, [t._v(" Dataset ")])])]), t._m(0)])]), e("div", { staticClass: "modal-footer" }, [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(o) {
    return t.resetDialogBox();
  } } }, [t._v("Close")]), e("button", { staticClass: "btn btn-primary", attrs: { type: "submit", form: "upload_form" } }, [t._v("Upload")])])])])]) : t._e();
}, r = [function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("div", { staticClass: "mb-3" }, [t("label", { staticClass: "form-label", attrs: { for: "fileInput" } }, [a._v("File")]), t("input", { staticClass: "form-control", attrs: { type: "file", id: "fileInput", name: "file", multiple: "" } }), t("div", { staticClass: "form-text" }, [a._v("Add files here.")])]);
}], c = /* @__PURE__ */ s(
  i,
  n,
  r,
  !1,
  null,
  null
);
const d = c.exports;
export {
  d as default
};
