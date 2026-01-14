import { V as n, c as r, n as i } from "./main-0dzOc6ov.js";
const l = n.component("album", {
  name: "album",
  props: {
    instancetype: {
      type: String,
      require: !0
    }
  },
  data() {
    return {
      results: [],
      loading: !1,
      loadError: !1,
      otherArgs: null,
      pageSize: 24
    };
  },
  watch: {},
  components: {},
  methods: {
    async loadPage() {
      if (this.results.length % this.pageSize > 0)
        return;
      const e = await r.get(
        `${ROOT_URL}about`,
        {
          params: {
            view: "instances",
            uri: this.instancetype,
            limit: this.pageSize,
            offset: this.results.length
          }
        }
      );
      this.results.push(...e.data);
    },
    async scrollBottom() {
      Math.ceil(window.innerHeight + window.scrollY) >= document.body.offsetHeight && await this.loadPage();
    }
  },
  async mounted() {
    window.addEventListener("scroll", this.scrollBottom), this.loading = !0, await this.loadPage(), this.loading = !1;
  },
  async unmounted() {
    window.removeEventListener("scroll", this.scrollBottom);
  },
  created() {
  }
});
var c = function() {
  var t = this, s = t._self._c;
  return t._self._setupProxy, s("div", {}, [t.loading ? s("spinner", { attrs: { loading: t.loading, text: "Loading..." } }) : s("div", { staticClass: "container" }, [s("div", { staticClass: "row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-6 row-cols-xxl-8 g-2 gx-2" }, t._l(t.results, function(o, a) {
    return s("kgcard", { key: a, staticClass: "col", attrs: { entity: o } });
  }), 1)])], 1);
}, d = [], u = /* @__PURE__ */ i(
  l,
  c,
  d,
  !1,
  null,
  "f0b7678e"
);
const g = u.exports;
export {
  g as default
};
