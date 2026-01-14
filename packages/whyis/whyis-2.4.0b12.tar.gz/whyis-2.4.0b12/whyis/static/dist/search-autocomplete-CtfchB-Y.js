import { V as o, c as a, n as h } from "./main-0dzOc6ov.js";
const l = o.component("search-autocomplete", {
  data: () => ({
    searchQuery: "",
    filteredOptions: [],
    showDropdown: !1,
    loading: !1,
    highlightedIndex: -1,
    debounceTimer: null
  }),
  methods: {
    async resolveEntity(t) {
      if (t && t.length > 2)
        try {
          return (await a.get("/", {
            params: { view: "resolve", term: t + "*" },
            responseType: "json"
          })).data || [];
        } catch (e) {
          return console.error("Error resolving entities:", e), [];
        }
      else
        return [];
    },
    onInput() {
      this.debouncedSearch();
    },
    onFocus() {
      this.searchQuery.length >= 3 && (this.showDropdown = !0);
    },
    onBlur() {
      setTimeout(() => {
        this.showDropdown = !1, this.highlightedIndex = -1;
      }, 200);
    },
    onKeydown(t) {
      switch (t.key) {
        case "ArrowDown":
          t.preventDefault(), this.navigateDown();
          break;
        case "ArrowUp":
          t.preventDefault(), this.navigateUp();
          break;
        case "Enter":
          t.preventDefault(), this.highlightedIndex === -1 && this.searchQuery.length >= 3 ? this.searchFor() : this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredOptions.length && this.selectOption(this.filteredOptions[this.highlightedIndex]);
          break;
        case "Escape":
          this.showDropdown = !1, this.highlightedIndex = -1, this.$refs.input.blur();
          break;
      }
    },
    debouncedSearch() {
      this.debounceTimer && clearTimeout(this.debounceTimer), this.debounceTimer = setTimeout(() => {
        this.performSearch();
      }, 300);
    },
    async performSearch() {
      const t = this.searchQuery.trim();
      if (t.length < 3) {
        this.filteredOptions = [], this.showDropdown = !1;
        return;
      }
      this.loading = !0;
      try {
        const e = await this.resolveEntity(t);
        this.filteredOptions = Array.isArray(e) ? e : [], this.showDropdown = !0, this.highlightedIndex = -1;
      } catch (e) {
        console.error("Error fetching autocomplete data:", e), this.filteredOptions = [];
      } finally {
        this.loading = !1;
      }
    },
    selectOption(t) {
      t && t.node && (window.location.href = "/about?view=view&uri=" + encodeURIComponent(t.node));
    },
    searchFor() {
      const t = encodeURIComponent(this.searchQuery);
      window.location.href = "/about?view=search&query=" + t;
    },
    navigateDown() {
      this.highlightedIndex < this.filteredOptions.length - 1 && this.highlightedIndex++;
    },
    navigateUp() {
      this.highlightedIndex > -1 && this.highlightedIndex--;
    },
    handleClickOutside(t) {
      this.$refs.wrapper.contains(t.target) || (this.showDropdown = !1, this.highlightedIndex = -1);
    }
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },
  beforeDestroy() {
    document.removeEventListener("click", this.handleClickOutside), this.debounceTimer && clearTimeout(this.debounceTimer);
  }
});
var d = function() {
  var e = this, s = e._self._c;
  return e._self._setupProxy, s("div", { staticClass: "position-relative" }, [s("div", { ref: "wrapper", staticClass: "autocomplete-wrapper" }, [s("div", { staticClass: "position-relative" }, [s("input", { directives: [{ name: "model", rawName: "v-model", value: e.searchQuery, expression: "searchQuery" }], ref: "input", staticClass: "form-control form-control-lg", attrs: { type: "text", placeholder: "Search knowledge base...", autocomplete: "off" }, domProps: { value: e.searchQuery }, on: { input: [function(i) {
    i.target.composing || (e.searchQuery = i.target.value);
  }, e.onInput], focus: e.onFocus, blur: e.onBlur, keydown: e.onKeydown } }), e.loading ? s("div", { staticClass: "position-absolute top-50 end-0 translate-middle-y pe-3" }, [e._m(0)]) : e._e()]), s("div", { directives: [{ name: "show", rawName: "v-show", value: e.showDropdown && (e.filteredOptions.length > 0 || e.searchQuery.length >= 3), expression: "showDropdown && (filteredOptions.length > 0 || searchQuery.length >= 3)" }], staticClass: "dropdown-menu show position-absolute w-100 mt-1", staticStyle: { "max-height": "300px", "overflow-y": "auto", "z-index": "1050" } }, [e.searchQuery.length >= 3 ? s("button", { staticClass: "dropdown-item d-flex align-items-center fw-bold", class: { active: e.highlightedIndex === -1 }, attrs: { type: "button" }, on: { click: e.searchFor, mouseenter: function(i) {
    e.highlightedIndex = -1;
  } } }, [s("i", { staticClass: "bi bi-search me-2" }), s("span", [e._v('Search for "' + e._s(e.searchQuery) + '"')])]) : e._e(), e.filteredOptions.length > 0 ? s("div", { staticClass: "dropdown-divider" }) : e._e(), e.filteredOptions.length > 0 ? e._l(e.filteredOptions, function(i, r) {
    return s("button", { key: i.node || r, staticClass: "dropdown-item d-flex align-items-center", class: { active: r === e.highlightedIndex }, attrs: { type: "button" }, on: { click: function(n) {
      return e.selectOption(i);
    }, mouseenter: function(n) {
      e.highlightedIndex = r;
    } } }, [s("div", [s("span", [e._v(e._s(i.prefLabel || i.label))]), i.label && i.label !== i.prefLabel ? s("span", { staticClass: "text-muted ms-1" }, [e._v("(" + e._s(i.label) + ")")]) : e._e()])]);
  }) : e._e()], 2)])]);
}, c = [function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", { staticClass: "spinner-border spinner-border-sm", attrs: { role: "status" } }, [e("span", { staticClass: "visually-hidden" }, [t._v("Loading...")])]);
}], u = /* @__PURE__ */ h(
  l,
  d,
  c,
  !1,
  null,
  "e9d9dba0"
);
const f = u.exports;
export {
  f as default
};
