import { V as t, n as i } from "./main-0dzOc6ov.js";
const a = t.component("Spinner", {
  props: {
    /**
     * Controls spinner visibility
     * @type {Boolean}
     * @default true
     */
    loading: {
      type: Boolean,
      default: !0
    },
    /**
     * Color of the spinning dots
     * @type {String}
     * @default "#08233c"
     */
    color: {
      type: String,
      default: "#08233c"
    },
    /**
     * Size of each spinning dot
     * @type {String}
     * @default "15px"
     */
    size: {
      type: String,
      default: "15px"
    },
    /**
     * Margin between spinning dots
     * @type {String}
     * @default "2px"
     */
    margin: {
      type: String,
      default: "2px"
    },
    /**
     * Border radius of the dots (100% for circles)
     * @type {String}
     * @default "100%"
     */
    radius: {
      type: String,
      default: "100%"
    },
    /**
     * Optional text to display above the spinner
     * @type {String}
     * @default null
     */
    text: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      spinnerStyle: {
        backgroundColor: this.color,
        height: this.size,
        width: this.size,
        borderRadius: this.radius,
        margin: this.margin,
        display: "inline-block",
        animationName: "spinerAnimation",
        animationDuration: "1.25s",
        animationIterationCount: "infinite",
        animationTimingFunction: "ease-in-out",
        animationFillMode: "both"
      },
      spinnerDelay1: {
        animationDelay: "0.07s"
      },
      spinnerDelay2: {
        animationDelay: "0.14s"
      },
      spinnerDelay3: {
        animationDelay: "0.21s"
      }
    };
  }
});
var s = function() {
  var n = this, e = n._self._c;
  return n._self._setupProxy, e("div", { directives: [{ name: "show", rawName: "v-show", value: n.loading, expression: "loading" }], staticClass: "spinner" }, [n.text ? e("div", { staticStyle: { "font-size": "1.5rem", "font-weight": "200", flex: "0 0 auto", "margin-bottom": "2rem" } }, [n._v(n._s(n.text) + " "), e("br")]) : n._e(), e("div", { staticStyle: { flex: "0 0 auto" } }, [e("span", { staticClass: "sync", style: [n.spinnerStyle, n.spinnerDelay1] }), e("span", { staticClass: "sync", style: [n.spinnerStyle, n.spinnerDelay2] }), e("span", { staticClass: "sync", style: [n.spinnerStyle, n.spinnerDelay3] })])]);
}, r = [], o = /* @__PURE__ */ i(
  a,
  s,
  r,
  !1,
  null,
  null
);
const y = o.exports;
export {
  y as default
};
