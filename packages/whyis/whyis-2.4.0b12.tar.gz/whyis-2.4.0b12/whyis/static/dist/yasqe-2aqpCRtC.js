import { V as a, n as r } from "./main-0dzOc6ov.js";
const n = a.component("yasqe", {
  props: {
    value: {
      type: String,
      default: () => ""
    },
    endpoint: {
      type: String,
      default: () => "/sparql"
    },
    showBtns: {
      type: Boolean,
      default: !1
    },
    readOnly: {
      type: Boolean,
      default: !1
    }
  },
  data() {
    return {
      editorValue: this.value
    };
  },
  mounted() {
    const e = this;
    this.yasqe = window.YASQE(this.$el, {
      persistent: null,
      sparql: {
        showQueryButton: !this.showBtns,
        endpoint: this.endpoint,
        requestMethod: "POST",
        callbacks: {
          error() {
            console.error("YASQE query error", arguments), e.$emit("query-error", error);
          },
          success(t) {
            e.$emit("query-success", t);
          }
        }
      },
      readOnly: this.readOnly
    }), this.yasqe.setValue(this.value), this.yasqe.on("changes", () => {
      this.editorValue = e.yasqe.getValue(), e.$emit("input", this.editorValue);
    }), this.yasqe.setSize("100%", "100%");
  },
  watch: {
    value(e) {
      e !== this.editorValue && this.yasqe.setValue(e);
    }
  }
});
var o = function() {
  var t = this, s = t._self._c;
  return t._self._setupProxy, s("div", { staticClass: "yasqe" });
}, i = [], l = /* @__PURE__ */ r(
  n,
  o,
  i,
  !1,
  null,
  null
);
const d = l.exports;
export {
  d as default
};
