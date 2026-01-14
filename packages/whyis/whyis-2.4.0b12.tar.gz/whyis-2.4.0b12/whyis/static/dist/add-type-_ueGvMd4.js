import { V as r, p as c, c as l, n as u } from "./main-0dzOc6ov.js";
const p = r.component("add-type", {
  props: ["uri", "hideButton"],
  data: function() {
    return {
      id: null,
      useCustom: !1,
      customTypeURI: null,
      selectedTypeModel: null,
      typeChips: [],
      status: !1,
      active: !1
    };
  },
  methods: {
    async fetchTypeData(s) {
      if (s && s.length > 2)
        try {
          return await this.getTypeList(s);
        } catch (t) {
          return console.error("Error fetching types:", t), [];
        }
      else
        return await this.getSuggestedTypes(this.uri);
    },
    useCustomURI() {
      this.useCustom = !0;
    },
    submitCustomURI() {
      var s = {
        label: this.customTypeURI,
        node: this.customTypeURI
      };
      this.typeChips.push(s), this.customTypeURI = "", this.useCustom = !1;
    },
    selectedTypeChange(s) {
      this.typeChips.push(s), this.selectedTypeModel = null;
    },
    // Create dialog boxes
    showDialogBox() {
      this.active = !0;
    },
    removeChip(s) {
      this.typeChips.splice(s, 1);
    },
    resetDialogBox() {
      this.active = !this.active, this.typeChips = [], this.customTypeURI = "", this.useCustom = !1, this.selectedTypeModel = null;
    },
    onCancel() {
      return this.resetDialogBox();
    },
    onSubmit() {
      return this.saveNewTypes().then(() => window.location.reload()), this.resetDialogBox();
    },
    async saveNewTypes() {
      let s = Promise.resolve();
      const t = this.processTypeChips(), e = {
        "@id": this.uri,
        "@type": t
      };
      await s;
      try {
        return c(e);
      } catch (a) {
        return alert(a);
      }
    },
    processTypeChips() {
      var s = this.typeChips;
      return Object.keys(s).map(function(t, e) {
        s[t].node && (s[t] = s[t].node);
      }), s;
    },
    // Formats the dropdown menu. Runs only while the menu is open
    processAutocompleteMenu(s) {
      if (document.getElementsByClassName("dropdown-menu").length >= 1)
        return status = !0;
    },
    async getSuggestedTypes(s) {
      return (await l.get(
        `${ROOT_URL}about?view=suggested_types&uri=${s}`
      )).data;
    },
    async getTypeList(s) {
      var t = [];
      const [e, a] = await l.all([
        l.get(
          `${ROOT_URL}about?term=${s}*&view=resolve&type=http://www.w3.org/2000/01/rdf-schema%23Class`
        ),
        l.get(
          `${ROOT_URL}about?term=${s}*&view=resolve&type=http://www.w3.org/2002/07/owl%23Class`
        )
      ]).catch((n) => {
        throw n;
      });
      return t = a.data.concat(e.data).sort((n, i) => n.score < i.score ? 1 : -1), this.groupBy(t, "node");
    },
    // Group entries by the value of a particular key
    groupBy(s, t) {
      let e = s.reduce(function(o, n) {
        return o[n[t]] = o[n[t]] || n, o;
      }, {});
      var a = Object.keys(e).map(function(o) {
        return e[o];
      });
      return a;
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
  })], 2), e("div", [t.active ? e("div", { staticClass: "modal fade", class: { show: t.active }, style: { display: t.active ? "block" : "none" }, attrs: { id: "addTypeModal", tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog modal-lg" }, [e("div", { staticClass: "modal-content" }, [e("div", { staticClass: "modal-header utility-dialog-box_header" }, [e("h5", { staticClass: "modal-title" }, [t._v("Specify additional types/classes")]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.onCancel } })]), e("div", { staticClass: "modal-body", staticStyle: { margin: "20px" } }, [e("div", { staticClass: "mb-3" }, [e("autocomplete", { attrs: { "fetch-data": t.fetchTypeData, "display-field": "preflabel", "key-field": "node", placeholder: "Search for types", "input-class": "form-control" }, on: { select: t.selectedTypeChange }, scopedSlots: t._u([{ key: "option", fn: function({ item: a }) {
    return [e("div", [a.preflabel ? e("span", [t._v(t._s(a.preflabel))]) : e("span", [t._v(t._s(a.label))]), e("small", { staticClass: "text-muted d-block" }, [t._v(t._s(a.node || a.property))])])];
  } }, { key: "no-results", fn: function({ query: a }) {
    return [e("div", { staticClass: "alert alert-info mt-2" }, [a ? e("p", [t._v('No types or classes matching "' + t._s(a) + '" were found.')]) : e("p", [t._v("Enter a type name.")]), e("button", { staticClass: "btn btn-link p-0", attrs: { type: "button" }, on: { click: t.useCustomURI } }, [t._v("Use a custom type URI")])])];
  } }], null, !1, 2138873359), model: { value: t.selectedTypeModel, callback: function(a) {
    t.selectedTypeModel = a;
  }, expression: "selectedTypeModel" } })], 1), t.useCustom ? e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "row g-3" }, [e("div", { staticClass: "col" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.customTypeURI, expression: "customTypeURI" }], staticClass: "form-control", attrs: { type: "text", id: "customTypeURI", placeholder: "Full URI of type" }, domProps: { value: t.customTypeURI }, on: { input: function(a) {
    a.target.composing || (t.customTypeURI = a.target.value);
  } } }), e("label", { attrs: { for: "customTypeURI" } }, [t._v("Full URI of type")])])]), e("div", { staticClass: "col-auto" }, [e("button", { staticClass: "btn btn-primary h-100", attrs: { type: "button" }, on: { click: t.submitCustomURI } }, [t._v(" Confirm URI ")])])])]) : t._e(), e("div", { staticClass: "mb-3" }, t._l(t.typeChips, function(a, o) {
    return e("div", { key: o + "chips", staticClass: "d-inline-block me-2 mb-2" }, [e("span", { staticClass: "badge bg-secondary d-flex align-items-center" }, [a.preflabel ? e("span", [t._v(t._s(a.preflabel))]) : a.label ? e("span", [t._v(t._s(a.label))]) : e("span", [t._v(t._s(a.node || a))]), e("button", { staticClass: "btn-close btn-close-white ms-2", attrs: { type: "button", "aria-label": "Remove" }, on: { click: function(n) {
      return t.removeChip(o);
    } } })])]);
  }), 0), e("div", { staticClass: "d-flex justify-content-end gap-2" }, [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(a) {
    return a.preventDefault(), t.onCancel.apply(null, arguments);
  } } }, [t._v(" Cancel ")]), e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(a) {
    return a.preventDefault(), t.onSubmit.apply(null, arguments);
  } } }, [t._v(" Submit ")])])])])])]) : t._e()])]);
}, y = [function() {
  var s = this, t = s._self._c;
  return s._self._setupProxy, t("button", { staticClass: "btn btn-outline-primary btn-sm", staticStyle: { border: "none", background: "transparent" } }, [t("i", { staticClass: "bi bi-plus" }), s._v(" Add type(s) "), t("span", { staticClass: "visually-hidden" }, [s._v("Specify additional type, subclass, or superclass.")])]);
}], m = /* @__PURE__ */ u(
  p,
  d,
  y,
  !1,
  null,
  null
);
const h = m.exports;
export {
  h as default
};
