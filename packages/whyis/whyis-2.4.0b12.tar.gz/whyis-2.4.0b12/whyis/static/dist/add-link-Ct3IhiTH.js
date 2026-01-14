import { V as l, p as c, c as n, n as u } from "./main-0dzOc6ov.js";
const p = l.component("add-link", {
  props: ["uri", "hideButton"],
  data: function() {
    return {
      id: null,
      property: null,
      propertyName: null,
      useCustom: !1,
      customPropertyURI: null,
      entity: null,
      status: !1,
      active: !1
    };
  },
  methods: {
    useCustomURI() {
      this.useCustom = !0, this.property = "Custom attribute";
    },
    // Property and entity fetch methods for autocomplete
    async fetchPropertyData(r) {
      if (r && r.length > 2)
        try {
          return await this.getPropertyList(r);
        } catch (t) {
          return console.error("Error fetching properties:", t), [];
        }
      else
        return await this.getSuggestedProperties(this.uri);
    },
    async fetchEntityData(r) {
      if (r && r.length > 2)
        try {
          return await this.getEntityList(r);
        } catch (t) {
          return console.error("Error fetching entities:", t), [];
        }
      else
        return await this.getNeighborEntities(this.uri);
    },
    selectedPropertyChange(r) {
      this.property = r, r.preflabel ? this.propertyName = r.preflabel : this.propertyName = r.label;
    },
    selectedEntityChange(r) {
      this.entity = r;
    },
    // Create dialog boxes
    showDialogBox() {
      this.active = !0;
    },
    resetDialogBox() {
      this.active = !this.active, this.property = null, this.propertyName = null, this.useCustom = !1, this.customPropertyURI = null, this.entity = null;
    },
    onCancel() {
      return this.resetDialogBox();
    },
    onSubmit() {
      return this.saveLink().then(() => window.location.reload()), this.resetDialogBox();
    },
    async saveLink() {
      let r = Promise.resolve(), t = {
        "@id": this.uri
      }, e = this.entity.node;
      this.entity.uri && (e = this.entity.uri);
      let s = null;
      this.property.node ? s = this.property.node : this.property.property ? s = this.property.property : this.customPropertyURI && (s = this.customPropertyURI), t[s] = {
        "@id": e
      }, console.log(t), await r;
      try {
        return c(t);
      } catch (a) {
        return alert(a);
      }
    },
    // Formats the dropdown menu. Runs only while the menu is open
    processAutocompleteMenu(r) {
      if (document.getElementsByClassName("dropdown-menu").length >= 1)
        return status = !0;
    },
    async getSuggestedProperties(r) {
      return (await n.get(
        `${ROOT_URL}about?view=suggested_links&uri=${r}`
      )).data.outgoing;
    },
    async getPropertyList(r) {
      var t = [];
      const [e, s] = await n.all([
        n.get(
          `${ROOT_URL}about?term=*${r}*&view=resolve&type=http://www.w3.org/1999/02/22-rdf-syntax-ns%23Property`
        ),
        n.get(
          `${ROOT_URL}about?term=*${r}*&view=resolve&type=http://www.w3.org/2002/07/owl%23ObjectProperty`
        )
      ]).catch((o) => {
        throw o;
      });
      return t = s.data.concat(e.data).sort((o, i) => o.score < i.score ? 1 : -1), this.groupBy(t, "node");
    },
    async getNeighborEntities(r) {
      return (await n.get(
        `${ROOT_URL}about?view=neighbors&uri=${r}`
      )).data;
    },
    async getEntityList(r) {
      return (await n.get(
        `${ROOT_URL}about?term=*${r}*&view=resolve`
      )).data;
    },
    // Group entries by the value of a particular key
    groupBy(r, t) {
      let e = r.reduce(function(a, o) {
        return a[o[t]] = a[o[t]] || o, a;
      }, {});
      var s = Object.keys(e).map(function(a) {
        return e[a];
      });
      return s;
    }
  },
  created: function() {
    this.hideButton && (this.active = !0);
  }
});
var d = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", [t.hideButton ? t._e() : e("div", { on: { click: t.showDialogBox } }, [t._t("default", function() {
    return [t._m(0)];
  })], 2), e("div", [t.active ? e("div", { staticClass: "modal fade", class: { show: t.active }, style: { display: t.active ? "block" : "none" }, attrs: { id: "addLinkModal", tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog modal-lg" }, [e("div", { staticClass: "modal-content" }, [e("div", { staticClass: "modal-header utility-dialog-box_header" }, [e("h5", { staticClass: "modal-title" }, [t._v("New Link")]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.onCancel } })]), e("div", { staticClass: "modal-body", staticStyle: { margin: "20px" } }, [e("div", { staticClass: "mb-3" }, [e("autocomplete", { attrs: { "fetch-data": t.fetchPropertyData, "display-field": "preflabel", "key-field": "node", placeholder: "Link Type", "input-class": "form-control" }, on: { select: t.selectedPropertyChange }, scopedSlots: t._u([{ key: "option", fn: function({ item: s }) {
    return [e("div", [s.preflabel ? e("span", [t._v(t._s(s.preflabel))]) : e("span", [t._v(t._s(s.label))]), e("small", { staticClass: "text-muted d-block" }, [t._v(t._s(s.node || s.property))])])];
  } }, { key: "no-results", fn: function({ query: s }) {
    return [e("div", { staticClass: "alert alert-info mt-2" }, [s ? e("p", [t._v('No link types matching "' + t._s(s) + '" were found.')]) : e("p", [t._v("Type a property name.")]), e("button", { staticClass: "btn btn-link p-0", attrs: { type: "button" }, on: { click: t.useCustomURI } }, [t._v("Use a custom property URI")])])];
  } }], null, !1, 1495376442), model: { value: t.property, callback: function(s) {
    t.property = s;
  }, expression: "property" } })], 1), t.useCustom ? e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.customPropertyURI, expression: "customPropertyURI" }], staticClass: "form-control", attrs: { type: "text", id: "customPropertyURI", placeholder: "Full URI of property" }, domProps: { value: t.customPropertyURI }, on: { input: function(s) {
    s.target.composing || (t.customPropertyURI = s.target.value);
  } } }), e("label", { attrs: { for: "customPropertyURI" } }, [t._v("Full URI of property")])])]) : t._e(), t.property ? e("div", { staticClass: "mb-3" }, [e("autocomplete", { attrs: { "fetch-data": t.fetchEntityData, "display-field": "preflabel", "key-field": "node", placeholder: t.propertyName || "Linked entity", "input-class": "form-control" }, on: { select: t.selectedEntityChange }, scopedSlots: t._u([{ key: "option", fn: function({ item: s }) {
    return [e("div", [s.preflabel ? e("span", [t._v(t._s(s.preflabel) + " (" + t._s(s.class_label) + ")")]) : e("span", [t._v(t._s(s.label) + " (" + t._s(s.class_label) + ")")]), e("small", { staticClass: "text-muted d-block" }, [t._v(t._s(s.node || s.uri))])])];
  } }, { key: "no-results", fn: function({ query: s }) {
    return [e("div", { staticClass: "alert alert-info mt-2" }, [s ? e("p", [t._v('No entities matching "' + t._s(s) + '" were found.')]) : e("p", [t._v("Type an entity name.")])])];
  } }], null, !1, 629164403), model: { value: t.entity, callback: function(s) {
    t.entity = s;
  }, expression: "entity" } })], 1) : t._e(), e("div", { staticClass: "d-flex justify-content-end gap-2 mt-4" }, [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(s) {
    return s.preventDefault(), t.onCancel.apply(null, arguments);
  } } }, [t._v(" Cancel ")]), e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(s) {
    return s.preventDefault(), t.onSubmit.apply(null, arguments);
  } } }, [t._v(" Add Link ")])])])])])]) : t._e()])]);
}, y = [function() {
  var r = this, t = r._self._c;
  return r._self._setupProxy, t("button", { staticClass: "btn btn-outline-primary btn-sm", staticStyle: { border: "none", background: "transparent" } }, [t("i", { staticClass: "bi bi-plus" }), r._v(" Add Link "), t("span", { staticClass: "visually-hidden" }, [r._v("Add a link to another entity.")])]);
}], f = /* @__PURE__ */ u(
  p,
  d,
  y,
  !1,
  null,
  null
);
const m = f.exports;
export {
  m as default
};
