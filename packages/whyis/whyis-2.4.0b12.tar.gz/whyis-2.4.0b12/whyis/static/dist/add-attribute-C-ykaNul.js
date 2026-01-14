import { V as u, p as d, c as n, n as c } from "./main-0dzOc6ov.js";
const w = u.component("add-attribute", {
  props: ["uri", "hideButton"],
  data: function() {
    return {
      id: null,
      datatypeProperty: null,
      datatypePropertyName: null,
      useCustom: !1,
      customDatatypePropertyURI: null,
      query: null,
      awaitingResolve: !1,
      propertyList: [],
      value: null,
      datatype: null,
      language: null,
      status: !1,
      active: !1,
      datatypes: {
        null: {
          uri: null,
          label: "None",
          widget: "textarea"
        },
        "http://www.w3.org/2001/XMLSchema#string": {
          uri: "http://www.w3.org/2001/XMLSchema#string",
          label: "String",
          widget: "textarea"
        },
        "http://www.w3.org/2001/XMLSchema#date": {
          uri: "http://www.w3.org/2001/XMLSchema#date",
          label: "Date",
          widget: "date"
        },
        "http://www.w3.org/2001/XMLSchema#dateTime": {
          uri: "http://www.w3.org/2001/XMLSchema#dateTime",
          label: "DateTime",
          widget: "date"
        },
        "http://www.w3.org/2001/XMLSchema#integer": {
          uri: "http://www.w3.org/2001/XMLSchema#integer",
          label: "Integer",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#decimal": {
          uri: "http://www.w3.org/2001/XMLSchema#decimal",
          label: "Decimal",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#time": {
          uri: "http://www.w3.org/2001/XMLSchema#time",
          label: "Time",
          widget: "time"
        },
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML": {
          uri: "http://www.w3.org/1999/02/22-rdf-syntax-ns#HTML",
          label: "HTML",
          widget: "textarea"
        },
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral": {
          uri: "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
          label: "XML",
          widget: "textarea"
        },
        "http://www.w3.org/2001/XMLSchema#boolean": {
          uri: "http://www.w3.org/2001/XMLSchema#boolean",
          label: "Boolean",
          widget: "select",
          options: ["true", "false"]
        },
        "http://www.w3.org/2001/XMLSchema#byte": {
          uri: "http://www.w3.org/2001/XMLSchema#byte",
          label: "Byte",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#double": {
          uri: "http://www.w3.org/2001/XMLSchema#double",
          label: "Double",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#float": {
          uri: "http://www.w3.org/2001/XMLSchema#float",
          label: "Float",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#int": {
          uri: "http://www.w3.org/2001/XMLSchema#int",
          label: "Int",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#negativeInteger": {
          uri: "http://www.w3.org/2001/XMLSchema#negativeInteger",
          label: "Integer",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#positiveInteger": {
          uri: "http://www.w3.org/2001/XMLSchema#positiveInteger",
          label: "Integer",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#nonNegativeInteger": {
          uri: "http://www.w3.org/2001/XMLSchema#nonNegativeInteger",
          label: "Integer",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#nonPositiveInteger": {
          uri: "http://www.w3.org/2001/XMLSchema#nonPositiveInteger",
          label: "Integer",
          widget: "number"
        },
        "http://www.w3.org/2001/XMLSchema#short": {
          uri: "http://www.w3.org/2001/XMLSchema#short",
          label: "Short Integer",
          widget: "number"
        },
        "http://www.opengis.net/ont/geosparql#wktLiteral": {
          uri: "http://www.opengis.net/ont/geosparql#wktLiteral",
          label: "WKT Geometry",
          widget: "textarea"
        },
        "http://www.opengis.net/ont/geosparql#gmlLiteral": {
          uri: "http://www.opengis.net/ont/geosparql#gmlLiteral",
          label: "GML Geometry",
          widget: "textarea"
        }
      }
    };
  },
  methods: {
    async fetchDatatypePropertyData(r) {
      if (r && r.length > 2)
        try {
          return await this.getDatatypePropertyList(r);
        } catch (t) {
          return console.error("Error fetching datatype properties:", t), [];
        }
      else
        return await this.getSuggestedDatatypeProperties(this.uri);
    },
    useCustomURI() {
      this.useCustom = !0, this.datatypeProperty = "Custom datatype property";
    },
    selectedDatatypePropertyChange(r) {
      this.datatypeProperty = r, r.preflabel ? this.datatypePropertyName = r.preflabel : this.datatypePropertyName = r.label, r.range && this.datatypes[r.range] && (this.datatype = r.range);
    },
    selectedDatatypeChange(r) {
      console.log(this);
    },
    // Create dialog boxes
    showDialogBox() {
      this.active = !0;
    },
    resetDialogBox() {
      this.active = !this.active, this.datatypeProperty = null, this.datatypePropertyName = null, this.useCustom = !1, this.customDatatypePropertyURI = null, this.value = null, this.language = null, this.datatype = null;
    },
    onCancel() {
      return this.resetDialogBox();
    },
    onSubmit() {
      return this.saveAttribute().then(() => window.location.reload()), this.resetDialogBox();
    },
    async saveAttribute() {
      let r = Promise.resolve(), t = {
        "@id": this.uri
      };
      this.datatype && (this.language = null);
      let e = null;
      this.datatypeProperty && this.datatypeProperty.node ? e = this.datatypeProperty.node : this.customDatatypePropertyURI && (e = this.customDatatypePropertyURI), e && (t[e] = {
        "@value": this.value,
        "@lang": this.language,
        "@type": this.datatype
      }), console.log(t), await r;
      try {
        return d(t);
      } catch (a) {
        return alert(a);
      }
    },
    // Formats the dropdown menu. Runs only while the menu is open
    processAutocompleteMenu(r) {
      if (document.getElementsByClassName("dropdown-menu").length >= 1)
        return status = !0;
    },
    async getSuggestedDatatypeProperties(r) {
      return (await n.get(
        `${ROOT_URL}about?view=suggested_attributes&uri=${r}`
      )).data;
    },
    async getDatatypePropertyList(r) {
      var t = [];
      const [e, a] = await n.all([
        n.get(
          `${ROOT_URL}about?term=*${r}*&view=resolve&type=http://www.w3.org/1999/02/22-rdf-syntax-ns%23Property`
        ),
        n.get(
          `${ROOT_URL}about?term=*${r}*&view=resolve&type=http://www.w3.org/2002/07/owl%23DatatypeProperty`
        )
      ]).catch((l) => {
        throw l;
      });
      return t = a.data.concat(e.data).sort((l, s) => l.score < s.score ? 1 : -1), this.groupBy(t, "node");
    },
    // Group entries by the value of a particular key
    groupBy(r, t) {
      let e = r.reduce(function(o, l) {
        return o[l[t]] = o[l[t]] || l, o;
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
var y = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", [t.hideButton ? t._e() : e("div", { on: { click: t.showDialogBox } }, [t._t("default", function() {
    return [t._m(0)];
  })], 2), e("div", [t.active ? e("div", { staticClass: "modal fade", class: { show: t.active }, style: { display: t.active ? "block" : "none" }, attrs: { id: "addAttributeModal", tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog modal-lg" }, [e("div", { staticClass: "modal-content" }, [e("div", { staticClass: "modal-header utility-dialog-box_header" }, [e("h5", { staticClass: "modal-title" }, [t._v("New Attribute")]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.onCancel } })]), e("div", { staticClass: "modal-body", staticStyle: { margin: "20px" } }, [e("div", { staticClass: "row g-3" }, [e("div", { staticClass: "col-md-6" }, [e("autocomplete", { attrs: { "fetch-data": t.fetchDatatypePropertyData, "display-field": "preflabel", "key-field": "node", placeholder: "Search for datatype property", "input-class": "form-control" }, on: { select: t.selectedDatatypePropertyChange }, scopedSlots: t._u([{ key: "option", fn: function({ item: a }) {
    return [e("div", [a.preflabel ? e("span", [t._v(t._s(a.preflabel))]) : e("span", [t._v(t._s(a.label))]), e("small", { staticClass: "text-muted d-block" }, [t._v(t._s(a.node || a.property))])])];
  } }, { key: "no-results", fn: function({ query: a }) {
    return [e("div", { staticClass: "alert alert-info mt-2" }, [a ? e("p", [t._v('No datatype properties matching "' + t._s(a) + '" were found.')]) : e("p", [t._v("Enter a datatype property name.")]), e("button", { staticClass: "btn btn-link p-0", attrs: { type: "button" }, on: { click: t.useCustomURI } }, [t._v("Use a custom property URI")])])];
  } }], null, !1, 3559394240), model: { value: t.datatypeProperty, callback: function(a) {
    t.datatypeProperty = a;
  }, expression: "datatypeProperty" } })], 1), e("div", { staticClass: "col-md-6" }, [e("div", { staticClass: "form-floating" }, [e("select", { directives: [{ name: "model", rawName: "v-model", value: t.datatype, expression: "datatype" }], staticClass: "form-select", attrs: { id: "datatype" }, on: { change: [function(a) {
    var o = Array.prototype.filter.call(a.target.options, function(l) {
      return l.selected;
    }).map(function(l) {
      var s = "_value" in l ? l._value : l.value;
      return s;
    });
    t.datatype = a.target.multiple ? o : o[0];
  }, t.selectedDatatypeChange] } }, [e("option", { attrs: { value: "" } }, [t._v("Select data type...")]), t._l(Object.values(t.datatypes), function(a) {
    return e("option", { key: a.uri, domProps: { value: a.uri } }, [t._v(" " + t._s(a.label) + " ")]);
  })], 2), e("label", { attrs: { for: "datatype" } }, [t._v("Data type")])])]), t.datatype ? t._e() : e("div", { staticClass: "col-md-6" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.language, expression: "language" }], staticClass: "form-control", attrs: { type: "text", id: "language", placeholder: "Language" }, domProps: { value: t.language }, on: { input: function(a) {
    a.target.composing || (t.language = a.target.value);
  } } }), e("label", { attrs: { for: "language" } }, [t._v("Language")])])])]), t.useCustom ? e("div", { staticClass: "row g-3 mt-3" }, [e("div", { staticClass: "col" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.customDatatypePropertyURI, expression: "customDatatypePropertyURI" }], staticClass: "form-control", attrs: { type: "text", id: "customDatatypePropertyURI", placeholder: "Full URI of datatype property" }, domProps: { value: t.customDatatypePropertyURI }, on: { input: function(a) {
    a.target.composing || (t.customDatatypePropertyURI = a.target.value);
  } } }), e("label", { attrs: { for: "customDatatypePropertyURI" } }, [t._v("Full URI of datatype property")])])])]) : t._e(), t.datatypeProperty ? e("div", { staticClass: "row g-3 mt-3" }, [e("div", { staticClass: "col" }, [t.datatype == null || t.datatypes[t.datatype] && t.datatypes[t.datatype].widget == "textarea" ? e("div", { staticClass: "form-floating" }, [e("textarea", { directives: [{ name: "model", rawName: "v-model", value: t.value, expression: "value" }], staticClass: "form-control", staticStyle: { height: "100px" }, attrs: { id: "valueTextarea", placeholder: t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value" }, domProps: { value: t.value }, on: { input: function(a) {
    a.target.composing || (t.value = a.target.value);
  } } }), e("label", { attrs: { for: "valueTextarea" } }, [t._v(t._s(t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value"))])]) : e("div", { staticClass: "form-floating" }, [(t.datatypes[t.datatype] ? t.datatypes[t.datatype].widget : "text") === "checkbox" ? e("input", { directives: [{ name: "model", rawName: "v-model", value: t.value, expression: "value" }], staticClass: "form-control", attrs: { id: "valueInput", placeholder: t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value", type: "checkbox" }, domProps: { checked: Array.isArray(t.value) ? t._i(t.value, null) > -1 : t.value }, on: { change: function(a) {
    var o = t.value, l = a.target, s = !!l.checked;
    if (Array.isArray(o)) {
      var p = null, i = t._i(o, p);
      l.checked ? i < 0 && (t.value = o.concat([p])) : i > -1 && (t.value = o.slice(0, i).concat(o.slice(i + 1)));
    } else
      t.value = s;
  } } }) : (t.datatypes[t.datatype] ? t.datatypes[t.datatype].widget : "text") === "radio" ? e("input", { directives: [{ name: "model", rawName: "v-model", value: t.value, expression: "value" }], staticClass: "form-control", attrs: { id: "valueInput", placeholder: t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value", type: "radio" }, domProps: { checked: t._q(t.value, null) }, on: { change: function(a) {
    t.value = null;
  } } }) : e("input", { directives: [{ name: "model", rawName: "v-model", value: t.value, expression: "value" }], staticClass: "form-control", attrs: { id: "valueInput", placeholder: t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value", type: t.datatypes[t.datatype] ? t.datatypes[t.datatype].widget : "text" }, domProps: { value: t.value }, on: { input: function(a) {
    a.target.composing || (t.value = a.target.value);
  } } }), e("label", { attrs: { for: "valueInput" } }, [t._v(t._s(t.datatypeProperty.preflabel || t.datatypeProperty.label || "Value"))])])])]) : t._e(), e("div", { staticClass: "d-flex justify-content-end gap-2 mt-4" }, [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(a) {
    return a.preventDefault(), t.onCancel.apply(null, arguments);
  } } }, [t._v(" Cancel ")]), e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(a) {
    return a.preventDefault(), t.onSubmit.apply(null, arguments);
  } } }, [t._v(" Add Attribute ")])])])])])]) : t._e()])]);
}, g = [function() {
  var r = this, t = r._self._c;
  return r._self._setupProxy, t("button", { staticClass: "btn btn-outline-primary btn-sm", staticStyle: { border: "none", background: "transparent" } }, [t("i", { staticClass: "bi bi-plus" }), r._v(" Add attribute "), t("span", { staticClass: "visually-hidden" }, [r._v("Add data about this entity.")])]);
}], m = /* @__PURE__ */ c(
  w,
  y,
  g,
  !1,
  null,
  null
);
const v = m.exports;
export {
  v as default
};
