import { n as l } from "./main-0dzOc6ov.js";
const a = {
  name: "AutocompleteSelect",
  props: {
    // Current selected value
    value: {
      type: [Object, String, Number],
      default: null
    },
    // Function to fetch data from server
    // Should return a Promise that resolves to an array
    fetchData: {
      type: Function,
      required: !0
    },
    // Minimum characters before triggering search
    minChars: {
      type: Number,
      default: 1
    },
    // Debounce delay in milliseconds
    debounce: {
      type: Number,
      default: 300
    },
    // Field to display from option object
    displayField: {
      type: String,
      default: "label"
    },
    // Field to use as unique identifier
    keyField: {
      type: String,
      default: "id"
    },
    // Placeholder text
    placeholder: {
      type: String,
      default: "Search..."
    },
    // Disabled state
    disabled: {
      type: Boolean,
      default: !1
    },
    // Additional CSS classes for input
    inputClass: {
      type: [String, Array, Object],
      default: ""
    },
    // Show "no results" message
    showNoResults: {
      type: Boolean,
      default: !0
    }
  },
  data() {
    return {
      searchQuery: "",
      filteredOptions: [],
      selectedItem: null,
      showDropdown: !1,
      loading: !1,
      highlightedIndex: -1,
      debounceTimer: null
    };
  },
  computed: {
    // For easier Vue 3 migration - computed properties work the same
  },
  watch: {
    value: {
      handler(t) {
        this.selectedItem = t, t ? (this.searchQuery = this.getDisplayValue(t), this.showDropdown = !1) : this.searchQuery = "";
      },
      immediate: !0
    }
  },
  mounted() {
    document.addEventListener("click", this.handleClickOutside);
  },
  beforeDestroy() {
    document.removeEventListener("click", this.handleClickOutside), this.debounceTimer && clearTimeout(this.debounceTimer);
  },
  methods: {
    onInput() {
      this.selectedItem && this.clearSelection(), this.debouncedSearch();
    },
    onFocus() {
      this.searchQuery.length >= this.minChars && !this.selectedItem && (this.showDropdown = !0);
    },
    onBlur() {
      setTimeout(() => {
        this.showDropdown = !1, this.highlightedIndex = -1;
      }, 150);
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
          t.preventDefault(), this.highlightedIndex >= 0 && this.selectOption(this.filteredOptions[this.highlightedIndex]);
          break;
        case "Escape":
          this.showDropdown = !1, this.highlightedIndex = -1, this.$refs.input.blur();
          break;
      }
    },
    debouncedSearch() {
      this.debounceTimer && clearTimeout(this.debounceTimer), this.debounceTimer = setTimeout(() => {
        this.performSearch();
      }, this.debounce);
    },
    async performSearch() {
      const t = this.searchQuery.trim();
      if (t.length < this.minChars) {
        this.filteredOptions = [], this.showDropdown = !1;
        return;
      }
      this.loading = !0;
      try {
        const e = await this.fetchData(t);
        this.filteredOptions = Array.isArray(e) ? e : [], this.showDropdown = !0, this.highlightedIndex = -1;
      } catch (e) {
        console.error("Error fetching autocomplete data:", e), this.filteredOptions = [], this.$emit("error", e);
      } finally {
        this.loading = !1;
      }
    },
    selectOption(t) {
      this.selectedItem = t, this.searchQuery = this.getDisplayValue(t), this.showDropdown = !1, this.highlightedIndex = -1, this.filteredOptions = [], this.$emit("input", t), this.$emit("select", t);
    },
    clearSelection() {
      this.selectedItem = null, this.searchQuery = "", this.filteredOptions = [], this.showDropdown = !1, this.$emit("input", null), this.$emit("clear"), this.$nextTick(() => {
        this.$refs.input.focus();
      });
    },
    navigateDown() {
      this.filteredOptions.length !== 0 && (this.highlightedIndex = Math.min(
        this.highlightedIndex + 1,
        this.filteredOptions.length - 1
      ));
    },
    navigateUp() {
      this.filteredOptions.length !== 0 && (this.highlightedIndex = Math.max(this.highlightedIndex - 1, -1));
    },
    getDisplayValue(t) {
      return t ? typeof t == "string" || typeof t == "number" ? String(t) : t[this.displayField] || t.preflabel || t.prefLabel || t.label || t.name || t.title || t.node || t.uri || t.id || "Unknown" : "";
    },
    getOptionKey(t, e) {
      return typeof t == "object" && t !== null ? t[this.keyField] || e : t || e;
    },
    handleClickOutside(t) {
      this.$refs.wrapper.contains(t.target) || (this.showDropdown = !1, this.highlightedIndex = -1);
    }
  }
};
var o = function() {
  var e = this, s = e._self._c;
  return s("div", { ref: "wrapper", staticClass: "autocomplete-wrapper" }, [e.selectedItem ? s("div", { staticClass: "selected-item-container mb-2" }, [s("div", { staticClass: "d-flex align-items-center justify-content-between bg-light border rounded p-2" }, [s("div", { staticClass: "flex-grow-1" }, [e._t("selected", function() {
    return [s("span", [e._v(e._s(e.getDisplayValue(e.selectedItem)))])];
  }, { item: e.selectedItem })], 2), s("button", { staticClass: "btn btn-sm btn-outline-danger ms-2", attrs: { type: "button", disabled: e.disabled }, on: { click: e.clearSelection } }, [s("i", { staticClass: "bi bi-x" }), e._v(" Remove ")])])]) : e._e(), s("div", { staticClass: "position-relative" }, [s("input", { directives: [{ name: "model", rawName: "v-model", value: e.searchQuery, expression: "searchQuery" }], ref: "input", staticClass: "form-control", class: e.inputClass, attrs: { type: "text", placeholder: e.placeholder, disabled: e.disabled, autocomplete: "off" }, domProps: { value: e.searchQuery }, on: { input: [function(i) {
    i.target.composing || (e.searchQuery = i.target.value);
  }, e.onInput], focus: e.onFocus, blur: e.onBlur, keydown: e.onKeydown } }), e.loading ? s("div", { staticClass: "position-absolute top-50 end-0 translate-middle-y pe-3" }, [e._m(0)]) : e._e()]), s("div", { directives: [{ name: "show", rawName: "v-show", value: e.showDropdown && (e.filteredOptions.length > 0 || e.showNoResults), expression: "showDropdown && (filteredOptions.length > 0 || showNoResults)" }], staticClass: "dropdown-menu show position-absolute w-100 mt-1", staticStyle: { "max-height": "200px", "overflow-y": "auto", "z-index": "1050" } }, [e.filteredOptions.length > 0 ? e._l(e.filteredOptions, function(i, r) {
    return s("button", { key: e.getOptionKey(i, r), staticClass: "dropdown-item d-flex align-items-center", class: { active: r === e.highlightedIndex }, attrs: { type: "button" }, on: { click: function(n) {
      return e.selectOption(i);
    }, mouseenter: function(n) {
      e.highlightedIndex = r;
    } } }, [e._t("option", function() {
      return [s("span", [e._v(e._s(e.getDisplayValue(i)))])];
    }, { item: i, index: r })], 2);
  }) : e.showNoResults ? s("div", { staticClass: "dropdown-item-text text-muted" }, [e._t("no-results", function() {
    return [e._v(' No results found for "' + e._s(e.searchQuery) + '" ')];
  }, { query: e.searchQuery })], 2) : e._e()], 2)]);
}, h = [function() {
  var t = this, e = t._self._c;
  return e("div", { staticClass: "spinner-border spinner-border-sm", attrs: { role: "status" } }, [e("span", { staticClass: "visually-hidden" }, [t._v("Loading...")])]);
}], d = /* @__PURE__ */ l(
  a,
  o,
  h,
  !1,
  null,
  "c86d0831"
);
const c = d.exports;
export {
  c as default
};
