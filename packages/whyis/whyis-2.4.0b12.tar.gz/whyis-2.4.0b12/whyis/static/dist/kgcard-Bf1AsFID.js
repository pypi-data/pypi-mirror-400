import { V as l, b as a, S as c, n as o } from "./main-0dzOc6ov.js";
const d = l.component("kgcard", {
  name: "kgcard",
  props: {
    entity: {
      require: !0
    }
  },
  data() {
    return {};
  },
  methods: {
    getViewUrl(i, t) {
      return a(i, t);
    },
    navigate(i) {
      return window.location = a(i.identifier, "view");
    },
    reduceDescription(i) {
      if (i == null) return i;
      let t, e, r;
      return t = i.split(" "), t.splice(15), e = t.reduce((s, n) => `${s} ${n}`, ""), r = c(e), `${r}...`;
    }
  }
});
var _ = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", { staticClass: "card" }, [t.entity.thumbnail ? e("img", { staticClass: "card-img-top", staticStyle: { height: "10em", "object-fit": "contain" }, attrs: { src: t.getViewUrl(t.entity.thumbnail), alt: t.entity.label } }) : e("img", { staticClass: "card-img-top", staticStyle: { height: "10em", "object-fit": "contain" }, attrs: { src: t.$root.$data.root_url + "static/images/rdf_flyer.svg", alt: t.entity.label } }), e("div", { staticClass: "card-body" }, [e("h6", { staticClass: "card-title" }, [t._v(t._s(t.entity.label))]), e("p", { staticClass: "card-text flex-grow-1" }, [t._v(t._s(t.entity.description))]), e("a", { staticClass: "card-link", attrs: { href: t.getViewUrl(t.entity.identifier, "view") } }, [t._v("View")]), e("a", { staticClass: "card-link", attrs: { href: t.getViewUrl(t.entity.identifier, "explore") } }, [t._v("Explore")])])]);
}, u = [], f = /* @__PURE__ */ o(
  d,
  _,
  u,
  !1,
  null,
  null
);
const p = f.exports;
export {
  p as default
};
