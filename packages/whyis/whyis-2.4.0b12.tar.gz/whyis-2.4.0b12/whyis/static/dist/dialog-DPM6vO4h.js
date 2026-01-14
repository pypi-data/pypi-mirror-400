import { V as n, E as a, n as o } from "./main-0dzOc6ov.js";
import { l as r } from "./orcid-lookup-BqprP7gj.js";
let l;
const c = () => (l = setInterval(() => {
  const s = document.getElementsByClassName("md-menu-content-bottom-start");
  if (s.length >= 1)
    return s[0].setAttribute("style", "z-index:1000 !important; width: 410px; max-width: 410px; position: absolute; top: 579px; left:50%; transform:translateX(-50%); will-change: top, left;"), status = !0;
}, 40), l), u = () => {
  if (l)
    return clearInterval(l);
}, d = n.component("dialogBox", {
  data() {
    return {
      active: !1,
      required: null,
      hasMessages: !1,
      loginRequestSent: !1,
      filterby: "title",
      selectedText: null,
      password: null,
      introTipScreen: 1,
      textarea: null,
      chartResults: {
        title: [],
        description: [],
        query: [],
        tableview: []
      },
      dialog: {
        status: !1
      },
      makeNew: {
        status: !1
      },
      agent: "",
      organization: {
        type: "Organization",
        name: ""
      },
      author: {
        type: "Person",
        name: "",
        "@id": null
      }
    };
  },
  computed: {
    messageClass() {
      return {
        "is-invalid": this.hasMessages
      };
    }
  },
  watch: {
    dialog(s, t) {
      s && s.share && this.copyText();
    }
  },
  components: {},
  destroy() {
    return u();
  },
  methods: {
    copyText() {
      setTimeout(() => {
        const s = document.getElementById("sharedlinktext");
        if (s)
          return s.select(), s.setSelectionRange(0, 99999), document.execCommand("copy"), a.$emit("snacks", { status: !0, message: "Chart link copied!", tip: "Paste Anywhere" });
      }, 800);
    },
    onConfirm() {
      return this.active = !this.active, this.loginRequestSent = !1, a.$emit("close-filter-box", this.active), a.filterChart(this.filterby, this.selectedText);
    },
    onSubmitNew() {
      if (this.active = !this.active, this.loginRequestSent = !1, this.agent === "author") {
        const s = r(this.author["@id"], "author");
        console.log(s);
      } else if (this.agent === "organization")
        return;
      a.$emit("close-filter-box", this.active);
    },
    onCancel() {
      this.active = !this.active, a.$emit("close-filter-box", this.active);
    },
    cancelDel() {
      this.active = !this.active, this.dialog = { status: !1 }, a.$emit("close-filter-box", this.active);
    },
    dialogAction() {
      return this.active = !this.active, this.dialog.delete ? a.deleteAChart(this.dialog.chart) : this.dialog.reset && a.resetChart(), this.dialog = { status: !1 }, a.$emit("close-filter-box", this.active);
    },
    nextScreen() {
      return this.introTipScreen += 1;
    },
    previousScreen() {
      if (this.introTipScreen >= 2)
        return this.introTipScreen -= 1;
    }
  },
  created() {
    a.$on("open-filter-box", (s) => {
      if (s.type == "filter")
        return this.active = s.open, c();
      this.active = s.open, this.loginRequestSent = !0;
    }).$on("appstate", (s) => {
      s.length >= 1 && (this.chartResults.title = s.map((t) => t.backup.title), this.chartResults.description = s.map((t) => t.backup.description), this.chartResults.query = s.map((t) => t.backup.query));
    }).$on("dialoguebox", (s) => {
      s && s.intro ? (this.active = s.status, this.dialog = s, this.introTipScreen = 1) : (this.active = s.status, this.dialog = s);
    }).$on("open-new-instance", (s) => {
      this.active = s.status, this.agent = s.type, this.makeNew = s;
    });
  }
});
var h = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", [t.active ? e("div", { staticClass: "modal fade", class: { show: t.active }, style: { display: t.active ? "block" : "none" }, attrs: { tabindex: "-1" } }, [e("div", { staticClass: "modal-dialog modal-lg" }, [e("div", { staticClass: "modal-content" }, [t.dialog.intro ? e("div", { staticClass: "viz-intro" }, [e("div", { staticClass: "modal-header" }, [e("h5", { staticClass: "modal-title" }, [t._v("Tips")]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.cancelDel } })]), e("div", { staticClass: "modal-body" }, [e("intros", { attrs: { screen: t.introTipScreen } })], 1), e("div", { staticClass: "modal-footer justify-content-between" }, [t.introTipScreen == 1 ? e("button", { staticClass: "btn btn-outline-secondary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.cancelDel.apply(null, arguments);
  } } }, [t._v("Skip")]) : e("button", { staticClass: "btn btn-outline-secondary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.previousScreen.apply(null, arguments);
  } } }, [t._v("Previous")]), e("div", [t.introTipScreen <= 3 ? e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.nextScreen.apply(null, arguments);
  } } }, [t._v("Next")]) : e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.cancelDel.apply(null, arguments);
  } } }, [t._v("Close")])])])]) : e("div", [e("div", { staticClass: "modal-header utility-dialog-box_header" }, [t.dialog.status ? e("h5", { staticClass: "modal-title" }, [t._v(t._s(t.dialog.title))]) : t.makeNew.status ? e("h5", { staticClass: "modal-title" }, [t._v(t._s(t.loginRequestSent ? "Login" : t.makeNew.title))]) : e("h5", { staticClass: "modal-title" }, [t._v(t._s(t.loginRequestSent ? "Login" : "Filter Chart"))]), e("button", { staticClass: "btn-close", attrs: { type: "button", "aria-label": "Close" }, on: { click: t.cancelDel } })]), e("div", { staticClass: "modal-body utility-dialog-box_login" }, [t.dialog.share ? e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "form-floating" }, [e("textarea", { directives: [{ name: "model", rawName: "v-model", value: t.dialog.chart, expression: "dialog.chart" }], staticClass: "form-control", staticStyle: { height: "100px" }, attrs: { id: "sharedlinktext", maxlength: "150" }, domProps: { value: t.dialog.chart }, on: { input: function(i) {
    i.target.composing || t.$set(t.dialog, "chart", i.target.value);
  } } }, [t._v(t._s(t.dialog.chart))]), e("label", { attrs: { for: "sharedlinktext" } }, [t._v("Chart Link")])]), e("small", { staticClass: "text-muted" }, [t._v(t._s(t.dialog.message))])]) : t.dialog.tableview ? e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "viz-intro-query", staticStyle: { "min-height": "40rem !important" } }, [e("yasr", { attrs: { results: t.dialog.tableview } })], 1)]) : t.dialog.query ? e("div", { staticClass: "mb-3" }, [e("div", { staticClass: "viz-intro-query" }, [e("yasqe", { attrs: { showBtns: !0 }, model: { value: t.dialog.query, callback: function(i) {
    t.$set(t.dialog, "query", i);
  }, expression: "dialog.query" } })], 1), e("small", { staticClass: "text-muted" }, [t._v(t._s(t.dialog.message))])]) : e("div", { staticClass: "mb-3" }, [e("p", [t._v(t._s(t.dialog.message))])])]), t.dialog.share || t.dialog.delete || t.dialog.query || t.dialog.diag || t.dialog.tableview ? e("div", { staticClass: "modal-footer" }, [t.dialog.share || t.dialog.query || t.dialog.tableview ? e("div", [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.cancelDel.apply(null, arguments);
  } } }, [t._v("Close")])]) : t.dialog.delete || t.dialog.diag ? e("div", [e("button", { staticClass: "btn btn-secondary", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.cancelDel.apply(null, arguments);
  } } }, [t._v("Close")]), t.dialog.btn ? t._e() : e("button", { staticClass: "btn btn-primary ms-2", attrs: { type: "button" }, on: { click: function(i) {
    return i.preventDefault(), t.dialogAction.apply(null, arguments);
  } } }, [t._v(t._s(t.dialog.title))])]) : t._e()]) : t._e()])])])]) : t._e()]);
}, p = [], m = /* @__PURE__ */ o(
  d,
  h,
  p,
  !1,
  null,
  null
);
const b = m.exports;
export {
  b as default
};
