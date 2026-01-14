import { d as G, g as J, V as K, E as b, m as Z, e as H, f as W, h as X, i as ee, q as te, l as re, s as ie, j as ne, k as P, o as R, n as se } from "./main-0dzOc6ov.js";
import { V as ae } from "./v-jsoneditor.min-Bvw701If.js";
var q = { exports: {} };
(function(e, t) {
  (function(r, n) {
    e.exports = n();
  })(G, function() {
    return function(r) {
      function n(s) {
        if (i[s]) return i[s].exports;
        var a = i[s] = { i: s, l: !1, exports: {} };
        return r[s].call(a.exports, a, a.exports, n), a.l = !0, a.exports;
      }
      var i = {};
      return n.m = r, n.c = i, n.i = function(s) {
        return s;
      }, n.d = function(s, a, o) {
        n.o(s, a) || Object.defineProperty(s, a, { configurable: !1, enumerable: !0, get: o });
      }, n.n = function(s) {
        var a = s && s.__esModule ? function() {
          return s.default;
        } : function() {
          return s;
        };
        return n.d(a, "a", a), a;
      }, n.o = function(s, a) {
        return Object.prototype.hasOwnProperty.call(s, a);
      }, n.p = "/dist/", n(n.s = 7);
    }([function(r, n) {
      r.exports = function() {
        var i = [];
        return i.toString = function() {
          for (var s = [], a = 0; a < this.length; a++) {
            var o = this[a];
            o[2] ? s.push("@media " + o[2] + "{" + o[1] + "}") : s.push(o[1]);
          }
          return s.join("");
        }, i.i = function(s, a) {
          typeof s == "string" && (s = [[null, s, ""]]);
          for (var o = {}, p = 0; p < this.length; p++) {
            var f = this[p][0];
            typeof f == "number" && (o[f] = !0);
          }
          for (p = 0; p < s.length; p++) {
            var l = s[p];
            typeof l[0] == "number" && o[l[0]] || (a && !l[2] ? l[2] = a : a && (l[2] = "(" + l[2] + ") and (" + a + ")"), i.push(l));
          }
        }, i;
      };
    }, function(r, n) {
      r.exports = function(i, s, a, o) {
        var p, f = i = i || {}, l = typeof i.default;
        l !== "object" && l !== "function" || (p = i, f = i.default);
        var g = typeof f == "function" ? f.options : f;
        if (s && (g.render = s.render, g.staticRenderFns = s.staticRenderFns), a && (g._scopeId = a), o) {
          var v = Object.create(g.computed || null);
          Object.keys(o).forEach(function(E) {
            var _ = o[E];
            v[E] = function() {
              return _;
            };
          }), g.computed = v;
        }
        return { esModule: p, exports: f, options: g };
      };
    }, function(r, n, i) {
      function s(c) {
        for (var m = 0; m < c.length; m++) {
          var d = c[m], u = v[d.id];
          if (u) {
            u.refs++;
            for (var h = 0; h < u.parts.length; h++) u.parts[h](d.parts[h]);
            for (; h < d.parts.length; h++) u.parts.push(o(d.parts[h]));
            u.parts.length > d.parts.length && (u.parts.length = d.parts.length);
          } else {
            for (var x = [], h = 0; h < d.parts.length; h++) x.push(o(d.parts[h]));
            v[d.id] = { id: d.id, refs: 1, parts: x };
          }
        }
      }
      function a() {
        var c = document.createElement("style");
        return c.type = "text/css", E.appendChild(c), c;
      }
      function o(c) {
        var m, d, u = document.querySelector('style[data-vue-ssr-id~="' + c.id + '"]');
        if (u) {
          if (I) return U;
          u.parentNode.removeChild(u);
        }
        if (V) {
          var h = k++;
          u = _ || (_ = a()), m = p.bind(null, u, h, !1), d = p.bind(null, u, h, !0);
        } else u = a(), m = f.bind(null, u), d = function() {
          u.parentNode.removeChild(u);
        };
        return m(c), function(x) {
          if (x) {
            if (x.css === c.css && x.media === c.media && x.sourceMap === c.sourceMap) return;
            m(c = x);
          } else d();
        };
      }
      function p(c, m, d, u) {
        var h = d ? "" : u.css;
        if (c.styleSheet) c.styleSheet.cssText = $(m, h);
        else {
          var x = document.createTextNode(h), w = c.childNodes;
          w[m] && c.removeChild(w[m]), w.length ? c.insertBefore(x, w[m]) : c.appendChild(x);
        }
      }
      function f(c, m) {
        var d = m.css, u = m.media, h = m.sourceMap;
        if (u && c.setAttribute("media", u), h && (d += `
/*# sourceURL=` + h.sources[0] + " */", d += `
/*# sourceMappingURL=data:application/json;base64,` + btoa(unescape(encodeURIComponent(JSON.stringify(h)))) + " */"), c.styleSheet) c.styleSheet.cssText = d;
        else {
          for (; c.firstChild; ) c.removeChild(c.firstChild);
          c.appendChild(document.createTextNode(d));
        }
      }
      var l = typeof document < "u";
      if (typeof DEBUG < "u" && DEBUG && !l) throw new Error("vue-style-loader cannot be used in a non-browser environment. Use { target: 'node' } in your Webpack config to indicate a server-rendering environment.");
      var g = i(19), v = {}, E = l && (document.head || document.getElementsByTagName("head")[0]), _ = null, k = 0, I = !1, U = function() {
      }, V = typeof navigator < "u" && /msie [6-9]\b/.test(navigator.userAgent.toLowerCase());
      r.exports = function(c, m, d) {
        I = d;
        var u = g(c, m);
        return s(u), function(h) {
          for (var x = [], w = 0; w < u.length; w++) {
            var Q = u[w], S = v[Q.id];
            S.refs--, x.push(S);
          }
          h ? (u = g(c, h), s(u)) : u = [];
          for (var w = 0; w < x.length; w++) {
            var S = x[w];
            if (S.refs === 0) {
              for (var A = 0; A < S.parts.length; A++) S.parts[A]();
              delete v[S.id];
            }
          }
        };
      };
      var $ = /* @__PURE__ */ function() {
        var c = [];
        return function(m, d) {
          return c[m] = d, c.filter(Boolean).join(`
`);
        };
      }();
    }, function(r, n, i) {
      i(17);
      var s = i(1)(i(4), i(14), "data-v-566a42b8", null);
      r.exports = s.exports;
    }, function(r, n, i) {
      function s(l) {
        return l && l.__esModule ? l : { default: l };
      }
      Object.defineProperty(n, "__esModule", { value: !0 });
      var a = i(12), o = s(a), p = i(11), f = s(p);
      n.default = { name: "splitPane", components: { Resizer: o.default, Pane: f.default }, props: { minPercent: { type: Number, default: 10 }, defaultPercent: { type: Number, default: 50 }, split: { validator: function(l) {
        return ["vertical", "horizontal"].indexOf(l) >= 0;
      }, required: !0 }, className: String }, computed: { userSelect: function() {
        return this.active ? "none" : "";
      }, cursor: function() {
        return this.active ? this.split === "vertical" ? "col-resize" : "row-resize" : "";
      } }, watch: { defaultPercent: function(l, g) {
        this.percent = l;
      } }, data: function() {
        return { active: !1, hasMoved: !1, height: null, percent: this.defaultPercent, type: this.split === "vertical" ? "width" : "height", resizeType: this.split === "vertical" ? "left" : "top" };
      }, methods: { onClick: function() {
        this.hasMoved || (this.percent = 50, this.$emit("resize", this.percent));
      }, onMouseDown: function() {
        this.active = !0, this.hasMoved = !1;
      }, onMouseUp: function() {
        this.active = !1;
      }, onMouseMove: function(l) {
        if (l.buttons !== 0 && l.which !== 0 || (this.active = !1), this.active) {
          var g = 0, v = l.currentTarget;
          if (this.split === "vertical") for (; v; ) g += v.offsetLeft, v = v.offsetParent;
          else for (; v; ) g += v.offsetTop, v = v.offsetParent;
          var E = this.split === "vertical" ? l.pageX : l.pageY, _ = this.split === "vertical" ? l.currentTarget.offsetWidth : l.currentTarget.offsetHeight, k = Math.floor((E - g) / _ * 1e4) / 100;
          k > this.minPercent && k < 100 - this.minPercent && (this.percent = k), this.$emit("resize", this.percent), this.hasMoved = !0;
        }
      } } };
    }, function(r, n, i) {
      Object.defineProperty(n, "__esModule", { value: !0 }), n.default = { name: "Pane", props: { className: String }, data: function() {
        return { classes: [this.$parent.split, this.className].join(" "), percent: 50 };
      } };
    }, function(r, n, i) {
      Object.defineProperty(n, "__esModule", { value: !0 }), n.default = { props: { split: { validator: function(s) {
        return ["vertical", "horizontal"].indexOf(s) >= 0;
      }, required: !0 }, className: String }, computed: { classes: function() {
        return ["splitter-pane-resizer", this.split, this.className].join(" ");
      } } };
    }, function(r, n, i) {
      Object.defineProperty(n, "__esModule", { value: !0 });
      var s = i(3), a = function(o) {
        return o && o.__esModule ? o : { default: o };
      }(s);
      n.default = a.default, typeof window < "u" && window.Vue && window.Vue.component("split-pane", a.default);
    }, function(r, n, i) {
      n = r.exports = i(0)(), n.push([r.i, ".splitter-pane-resizer[data-v-212fa2a4]{box-sizing:border-box;background:#000;position:absolute;opacity:.2;z-index:1;background-clip:padding-box}.splitter-pane-resizer.horizontal[data-v-212fa2a4]{height:11px;margin:-5px 0;border-top:5px solid hsla(0,0%,100%,0);border-bottom:5px solid hsla(0,0%,100%,0);cursor:row-resize;width:100%}.splitter-pane-resizer.vertical[data-v-212fa2a4]{width:11px;height:100%;margin-left:-5px;border-left:5px solid hsla(0,0%,100%,0);border-right:5px solid hsla(0,0%,100%,0);cursor:col-resize}", ""]);
    }, function(r, n, i) {
      n = r.exports = i(0)(), n.push([r.i, '.clearfix[data-v-566a42b8]:after{visibility:hidden;display:block;font-size:0;content:" ";clear:both;height:0}.vue-splitter-container[data-v-566a42b8]{height:100%;position:relative}.vue-splitter-container-mask[data-v-566a42b8]{z-index:9999;width:100%;height:100%;position:absolute;top:0;left:0}', ""]);
    }, function(r, n, i) {
      n = r.exports = i(0)(), n.push([r.i, ".splitter-pane.vertical.splitter-paneL[data-v-815c801c]{position:absolute;left:0;height:100%;padding-right:3px}.splitter-pane.vertical.splitter-paneR[data-v-815c801c]{position:absolute;right:0;height:100%;padding-left:3px}.splitter-pane.horizontal.splitter-paneL[data-v-815c801c]{position:absolute;top:0;width:100%}.splitter-pane.horizontal.splitter-paneR[data-v-815c801c]{position:absolute;bottom:0;width:100%;padding-top:3px}", ""]);
    }, function(r, n, i) {
      i(18);
      var s = i(1)(i(5), i(15), "data-v-815c801c", null);
      r.exports = s.exports;
    }, function(r, n, i) {
      i(16);
      var s = i(1)(i(6), i(13), "data-v-212fa2a4", null);
      r.exports = s.exports;
    }, function(r, n) {
      r.exports = { render: function() {
        var i = this, s = i.$createElement;
        return (i._self._c || s)("div", { class: i.classes });
      }, staticRenderFns: [] };
    }, function(r, n) {
      r.exports = { render: function() {
        var i, s, a, o = this, p = o.$createElement, f = o._self._c || p;
        return f("div", { staticClass: "vue-splitter-container clearfix", style: { cursor: o.cursor, userSelect: o.userSelect }, on: { mouseup: o.onMouseUp, mousemove: o.onMouseMove } }, [f("pane", { staticClass: "splitter-pane splitter-paneL", style: (i = {}, i[o.type] = o.percent + "%", i), attrs: { split: o.split } }, [o._t("paneL")], 2), o._v(" "), f("resizer", { style: (s = {}, s[o.resizeType] = o.percent + "%", s), attrs: { className: o.className, split: o.split }, nativeOn: { mousedown: function(l) {
          return o.onMouseDown(l);
        }, click: function(l) {
          return o.onClick(l);
        } } }), o._v(" "), f("pane", { staticClass: "splitter-pane splitter-paneR", style: (a = {}, a[o.type] = 100 - o.percent + "%", a), attrs: { split: o.split } }, [o._t("paneR")], 2), o._v(" "), o.active ? f("div", { staticClass: "vue-splitter-container-mask" }) : o._e()], 1);
      }, staticRenderFns: [] };
    }, function(r, n) {
      r.exports = { render: function() {
        var i = this, s = i.$createElement;
        return (i._self._c || s)("div", { class: i.classes }, [i._t("default")], 2);
      }, staticRenderFns: [] };
    }, function(r, n, i) {
      var s = i(8);
      typeof s == "string" && (s = [[r.i, s, ""]]), s.locals && (r.exports = s.locals), i(2)("a82a4610", s, !0);
    }, function(r, n, i) {
      var s = i(9);
      typeof s == "string" && (s = [[r.i, s, ""]]), s.locals && (r.exports = s.locals), i(2)("033d59ad", s, !0);
    }, function(r, n, i) {
      var s = i(10);
      typeof s == "string" && (s = [[r.i, s, ""]]), s.locals && (r.exports = s.locals), i(2)("6816c93c", s, !0);
    }, function(r, n) {
      r.exports = function(i, s) {
        for (var a = [], o = {}, p = 0; p < s.length; p++) {
          var f = s[p], l = f[0], g = f[1], v = f[2], E = f[3], _ = { id: i + ":" + p, css: g, media: v, sourceMap: E };
          o[l] ? o[l].parts.push(_) : a.push(o[l] = { id: l, parts: [_] });
        }
        return a;
      };
    }]);
  });
})(q);
var oe = q.exports;
const le = /* @__PURE__ */ J(oe);
/*! js-yaml 4.1.0 https://github.com/nodeca/js-yaml @license MIT */
function B(e) {
  return typeof e > "u" || e === null;
}
function ce(e) {
  return typeof e == "object" && e !== null;
}
function ue(e) {
  return Array.isArray(e) ? e : B(e) ? [] : [e];
}
function pe(e, t) {
  var r, n, i, s;
  if (t)
    for (s = Object.keys(t), r = 0, n = s.length; r < n; r += 1)
      i = s[r], e[i] = t[i];
  return e;
}
function fe(e, t) {
  var r = "", n;
  for (n = 0; n < t; n += 1)
    r += e;
  return r;
}
function de(e) {
  return e === 0 && Number.NEGATIVE_INFINITY === 1 / e;
}
var he = B, ve = ce, me = ue, ge = fe, ye = de, xe = pe, z = {
  isNothing: he,
  isObject: ve,
  toArray: me,
  repeat: ge,
  isNegativeZero: ye,
  extend: xe
};
function Y(e, t) {
  var r = "", n = e.reason || "(unknown reason)";
  return e.mark ? (e.mark.name && (r += 'in "' + e.mark.name + '" '), r += "(" + (e.mark.line + 1) + ":" + (e.mark.column + 1) + ")", !t && e.mark.snippet && (r += `

` + e.mark.snippet), n + " " + r) : n;
}
function N(e, t) {
  Error.call(this), this.name = "YAMLException", this.reason = e, this.mark = t, this.message = Y(this, !1), Error.captureStackTrace ? Error.captureStackTrace(this, this.constructor) : this.stack = new Error().stack || "";
}
N.prototype = Object.create(Error.prototype);
N.prototype.constructor = N;
N.prototype.toString = function(t) {
  return this.name + ": " + Y(this, t);
};
var T = N, be = [
  "kind",
  "multi",
  "resolve",
  "construct",
  "instanceOf",
  "predicate",
  "represent",
  "representName",
  "defaultStyle",
  "styleAliases"
], we = [
  "scalar",
  "sequence",
  "mapping"
];
function _e(e) {
  var t = {};
  return e !== null && Object.keys(e).forEach(function(r) {
    e[r].forEach(function(n) {
      t[String(n)] = r;
    });
  }), t;
}
function Ee(e, t) {
  if (t = t || {}, Object.keys(t).forEach(function(r) {
    if (be.indexOf(r) === -1)
      throw new T('Unknown option "' + r + '" is met in definition of "' + e + '" YAML type.');
  }), this.options = t, this.tag = e, this.kind = t.kind || null, this.resolve = t.resolve || function() {
    return !0;
  }, this.construct = t.construct || function(r) {
    return r;
  }, this.instanceOf = t.instanceOf || null, this.predicate = t.predicate || null, this.represent = t.represent || null, this.representName = t.representName || null, this.defaultStyle = t.defaultStyle || null, this.multi = t.multi || !1, this.styleAliases = _e(t.styleAliases || null), we.indexOf(this.kind) === -1)
    throw new T('Unknown kind "' + this.kind + '" is specified for "' + e + '" YAML type.');
}
var y = Ee;
function M(e, t) {
  var r = [];
  return e[t].forEach(function(n) {
    var i = r.length;
    r.forEach(function(s, a) {
      s.tag === n.tag && s.kind === n.kind && s.multi === n.multi && (i = a);
    }), r[i] = n;
  }), r;
}
function Se() {
  var e = {
    scalar: {},
    sequence: {},
    mapping: {},
    fallback: {},
    multi: {
      scalar: [],
      sequence: [],
      mapping: [],
      fallback: []
    }
  }, t, r;
  function n(i) {
    i.multi ? (e.multi[i.kind].push(i), e.multi.fallback.push(i)) : e[i.kind][i.tag] = e.fallback[i.tag] = i;
  }
  for (t = 0, r = arguments.length; t < r; t += 1)
    arguments[t].forEach(n);
  return e;
}
function O(e) {
  return this.extend(e);
}
O.prototype.extend = function(t) {
  var r = [], n = [];
  if (t instanceof y)
    n.push(t);
  else if (Array.isArray(t))
    n = n.concat(t);
  else if (t && (Array.isArray(t.implicit) || Array.isArray(t.explicit)))
    t.implicit && (r = r.concat(t.implicit)), t.explicit && (n = n.concat(t.explicit));
  else
    throw new T("Schema.extend argument should be a Type, [ Type ], or a schema definition ({ implicit: [...], explicit: [...] })");
  r.forEach(function(s) {
    if (!(s instanceof y))
      throw new T("Specified list of YAML types (or a single Type object) contains a non-Type object.");
    if (s.loadKind && s.loadKind !== "scalar")
      throw new T("There is a non-scalar type in the implicit list of a schema. Implicit resolving of such types is not supported.");
    if (s.multi)
      throw new T("There is a multi type in the implicit list of a schema. Multi tags can only be listed as explicit.");
  }), n.forEach(function(s) {
    if (!(s instanceof y))
      throw new T("Specified list of YAML types (or a single Type object) contains a non-Type object.");
  });
  var i = Object.create(O.prototype);
  return i.implicit = (this.implicit || []).concat(r), i.explicit = (this.explicit || []).concat(n), i.compiledImplicit = M(i, "implicit"), i.compiledExplicit = M(i, "explicit"), i.compiledTypeMap = Se(i.compiledImplicit, i.compiledExplicit), i;
};
var Te = O, Ce = new y("tag:yaml.org,2002:str", {
  kind: "scalar",
  construct: function(e) {
    return e !== null ? e : "";
  }
}), ke = new y("tag:yaml.org,2002:seq", {
  kind: "sequence",
  construct: function(e) {
    return e !== null ? e : [];
  }
}), Ne = new y("tag:yaml.org,2002:map", {
  kind: "mapping",
  construct: function(e) {
    return e !== null ? e : {};
  }
}), Ae = new Te({
  explicit: [
    Ce,
    ke,
    Ne
  ]
});
function Oe(e) {
  if (e === null) return !0;
  var t = e.length;
  return t === 1 && e === "~" || t === 4 && (e === "null" || e === "Null" || e === "NULL");
}
function ze() {
  return null;
}
function Fe(e) {
  return e === null;
}
var Ie = new y("tag:yaml.org,2002:null", {
  kind: "scalar",
  resolve: Oe,
  construct: ze,
  predicate: Fe,
  represent: {
    canonical: function() {
      return "~";
    },
    lowercase: function() {
      return "null";
    },
    uppercase: function() {
      return "NULL";
    },
    camelcase: function() {
      return "Null";
    },
    empty: function() {
      return "";
    }
  },
  defaultStyle: "lowercase"
});
function Pe(e) {
  if (e === null) return !1;
  var t = e.length;
  return t === 4 && (e === "true" || e === "True" || e === "TRUE") || t === 5 && (e === "false" || e === "False" || e === "FALSE");
}
function Re(e) {
  return e === "true" || e === "True" || e === "TRUE";
}
function Me(e) {
  return Object.prototype.toString.call(e) === "[object Boolean]";
}
var Le = new y("tag:yaml.org,2002:bool", {
  kind: "scalar",
  resolve: Pe,
  construct: Re,
  predicate: Me,
  represent: {
    lowercase: function(e) {
      return e ? "true" : "false";
    },
    uppercase: function(e) {
      return e ? "TRUE" : "FALSE";
    },
    camelcase: function(e) {
      return e ? "True" : "False";
    }
  },
  defaultStyle: "lowercase"
});
function qe(e) {
  return 48 <= e && e <= 57 || 65 <= e && e <= 70 || 97 <= e && e <= 102;
}
function Be(e) {
  return 48 <= e && e <= 55;
}
function Ye(e) {
  return 48 <= e && e <= 57;
}
function je(e) {
  if (e === null) return !1;
  var t = e.length, r = 0, n = !1, i;
  if (!t) return !1;
  if (i = e[r], (i === "-" || i === "+") && (i = e[++r]), i === "0") {
    if (r + 1 === t) return !0;
    if (i = e[++r], i === "b") {
      for (r++; r < t; r++)
        if (i = e[r], i !== "_") {
          if (i !== "0" && i !== "1") return !1;
          n = !0;
        }
      return n && i !== "_";
    }
    if (i === "x") {
      for (r++; r < t; r++)
        if (i = e[r], i !== "_") {
          if (!qe(e.charCodeAt(r))) return !1;
          n = !0;
        }
      return n && i !== "_";
    }
    if (i === "o") {
      for (r++; r < t; r++)
        if (i = e[r], i !== "_") {
          if (!Be(e.charCodeAt(r))) return !1;
          n = !0;
        }
      return n && i !== "_";
    }
  }
  if (i === "_") return !1;
  for (; r < t; r++)
    if (i = e[r], i !== "_") {
      if (!Ye(e.charCodeAt(r)))
        return !1;
      n = !0;
    }
  return !(!n || i === "_");
}
function De(e) {
  var t = e, r = 1, n;
  if (t.indexOf("_") !== -1 && (t = t.replace(/_/g, "")), n = t[0], (n === "-" || n === "+") && (n === "-" && (r = -1), t = t.slice(1), n = t[0]), t === "0") return 0;
  if (n === "0") {
    if (t[1] === "b") return r * parseInt(t.slice(2), 2);
    if (t[1] === "x") return r * parseInt(t.slice(2), 16);
    if (t[1] === "o") return r * parseInt(t.slice(2), 8);
  }
  return r * parseInt(t, 10);
}
function Ue(e) {
  return Object.prototype.toString.call(e) === "[object Number]" && e % 1 === 0 && !z.isNegativeZero(e);
}
var Ve = new y("tag:yaml.org,2002:int", {
  kind: "scalar",
  resolve: je,
  construct: De,
  predicate: Ue,
  represent: {
    binary: function(e) {
      return e >= 0 ? "0b" + e.toString(2) : "-0b" + e.toString(2).slice(1);
    },
    octal: function(e) {
      return e >= 0 ? "0o" + e.toString(8) : "-0o" + e.toString(8).slice(1);
    },
    decimal: function(e) {
      return e.toString(10);
    },
    /* eslint-disable max-len */
    hexadecimal: function(e) {
      return e >= 0 ? "0x" + e.toString(16).toUpperCase() : "-0x" + e.toString(16).toUpperCase().slice(1);
    }
  },
  defaultStyle: "decimal",
  styleAliases: {
    binary: [2, "bin"],
    octal: [8, "oct"],
    decimal: [10, "dec"],
    hexadecimal: [16, "hex"]
  }
}), $e = new RegExp(
  // 2.5e4, 2.5 and integers
  "^(?:[-+]?(?:[0-9][0-9_]*)(?:\\.[0-9_]*)?(?:[eE][-+]?[0-9]+)?|\\.[0-9_]+(?:[eE][-+]?[0-9]+)?|[-+]?\\.(?:inf|Inf|INF)|\\.(?:nan|NaN|NAN))$"
);
function Qe(e) {
  return !(e === null || !$e.test(e) || // Quick hack to not allow integers end with `_`
  // Probably should update regexp & check speed
  e[e.length - 1] === "_");
}
function Ge(e) {
  var t, r;
  return t = e.replace(/_/g, "").toLowerCase(), r = t[0] === "-" ? -1 : 1, "+-".indexOf(t[0]) >= 0 && (t = t.slice(1)), t === ".inf" ? r === 1 ? Number.POSITIVE_INFINITY : Number.NEGATIVE_INFINITY : t === ".nan" ? NaN : r * parseFloat(t, 10);
}
var Je = /^[-+]?[0-9]+e/;
function Ke(e, t) {
  var r;
  if (isNaN(e))
    switch (t) {
      case "lowercase":
        return ".nan";
      case "uppercase":
        return ".NAN";
      case "camelcase":
        return ".NaN";
    }
  else if (Number.POSITIVE_INFINITY === e)
    switch (t) {
      case "lowercase":
        return ".inf";
      case "uppercase":
        return ".INF";
      case "camelcase":
        return ".Inf";
    }
  else if (Number.NEGATIVE_INFINITY === e)
    switch (t) {
      case "lowercase":
        return "-.inf";
      case "uppercase":
        return "-.INF";
      case "camelcase":
        return "-.Inf";
    }
  else if (z.isNegativeZero(e))
    return "-0.0";
  return r = e.toString(10), Je.test(r) ? r.replace("e", ".e") : r;
}
function Ze(e) {
  return Object.prototype.toString.call(e) === "[object Number]" && (e % 1 !== 0 || z.isNegativeZero(e));
}
var He = new y("tag:yaml.org,2002:float", {
  kind: "scalar",
  resolve: Qe,
  construct: Ge,
  predicate: Ze,
  represent: Ke,
  defaultStyle: "lowercase"
}), We = Ae.extend({
  implicit: [
    Ie,
    Le,
    Ve,
    He
  ]
}), Xe = We, j = new RegExp(
  "^([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])$"
), D = new RegExp(
  "^([0-9][0-9][0-9][0-9])-([0-9][0-9]?)-([0-9][0-9]?)(?:[Tt]|[ \\t]+)([0-9][0-9]?):([0-9][0-9]):([0-9][0-9])(?:\\.([0-9]*))?(?:[ \\t]*(Z|([-+])([0-9][0-9]?)(?::([0-9][0-9]))?))?$"
);
function et(e) {
  return e === null ? !1 : j.exec(e) !== null || D.exec(e) !== null;
}
function tt(e) {
  var t, r, n, i, s, a, o, p = 0, f = null, l, g, v;
  if (t = j.exec(e), t === null && (t = D.exec(e)), t === null) throw new Error("Date resolve error");
  if (r = +t[1], n = +t[2] - 1, i = +t[3], !t[4])
    return new Date(Date.UTC(r, n, i));
  if (s = +t[4], a = +t[5], o = +t[6], t[7]) {
    for (p = t[7].slice(0, 3); p.length < 3; )
      p += "0";
    p = +p;
  }
  return t[9] && (l = +t[10], g = +(t[11] || 0), f = (l * 60 + g) * 6e4, t[9] === "-" && (f = -f)), v = new Date(Date.UTC(r, n, i, s, a, o, p)), f && v.setTime(v.getTime() - f), v;
}
function rt(e) {
  return e.toISOString();
}
var it = new y("tag:yaml.org,2002:timestamp", {
  kind: "scalar",
  resolve: et,
  construct: tt,
  instanceOf: Date,
  represent: rt
});
function nt(e) {
  return e === "<<" || e === null;
}
var st = new y("tag:yaml.org,2002:merge", {
  kind: "scalar",
  resolve: nt
}), F = `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=
\r`;
function at(e) {
  if (e === null) return !1;
  var t, r, n = 0, i = e.length, s = F;
  for (r = 0; r < i; r++)
    if (t = s.indexOf(e.charAt(r)), !(t > 64)) {
      if (t < 0) return !1;
      n += 6;
    }
  return n % 8 === 0;
}
function ot(e) {
  var t, r, n = e.replace(/[\r\n=]/g, ""), i = n.length, s = F, a = 0, o = [];
  for (t = 0; t < i; t++)
    t % 4 === 0 && t && (o.push(a >> 16 & 255), o.push(a >> 8 & 255), o.push(a & 255)), a = a << 6 | s.indexOf(n.charAt(t));
  return r = i % 4 * 6, r === 0 ? (o.push(a >> 16 & 255), o.push(a >> 8 & 255), o.push(a & 255)) : r === 18 ? (o.push(a >> 10 & 255), o.push(a >> 2 & 255)) : r === 12 && o.push(a >> 4 & 255), new Uint8Array(o);
}
function lt(e) {
  var t = "", r = 0, n, i, s = e.length, a = F;
  for (n = 0; n < s; n++)
    n % 3 === 0 && n && (t += a[r >> 18 & 63], t += a[r >> 12 & 63], t += a[r >> 6 & 63], t += a[r & 63]), r = (r << 8) + e[n];
  return i = s % 3, i === 0 ? (t += a[r >> 18 & 63], t += a[r >> 12 & 63], t += a[r >> 6 & 63], t += a[r & 63]) : i === 2 ? (t += a[r >> 10 & 63], t += a[r >> 4 & 63], t += a[r << 2 & 63], t += a[64]) : i === 1 && (t += a[r >> 2 & 63], t += a[r << 4 & 63], t += a[64], t += a[64]), t;
}
function ct(e) {
  return Object.prototype.toString.call(e) === "[object Uint8Array]";
}
var ut = new y("tag:yaml.org,2002:binary", {
  kind: "scalar",
  resolve: at,
  construct: ot,
  predicate: ct,
  represent: lt
}), pt = Object.prototype.hasOwnProperty, ft = Object.prototype.toString;
function dt(e) {
  if (e === null) return !0;
  var t = [], r, n, i, s, a, o = e;
  for (r = 0, n = o.length; r < n; r += 1) {
    if (i = o[r], a = !1, ft.call(i) !== "[object Object]") return !1;
    for (s in i)
      if (pt.call(i, s))
        if (!a) a = !0;
        else return !1;
    if (!a) return !1;
    if (t.indexOf(s) === -1) t.push(s);
    else return !1;
  }
  return !0;
}
function ht(e) {
  return e !== null ? e : [];
}
var vt = new y("tag:yaml.org,2002:omap", {
  kind: "sequence",
  resolve: dt,
  construct: ht
}), mt = Object.prototype.toString;
function gt(e) {
  if (e === null) return !0;
  var t, r, n, i, s, a = e;
  for (s = new Array(a.length), t = 0, r = a.length; t < r; t += 1) {
    if (n = a[t], mt.call(n) !== "[object Object]" || (i = Object.keys(n), i.length !== 1)) return !1;
    s[t] = [i[0], n[i[0]]];
  }
  return !0;
}
function yt(e) {
  if (e === null) return [];
  var t, r, n, i, s, a = e;
  for (s = new Array(a.length), t = 0, r = a.length; t < r; t += 1)
    n = a[t], i = Object.keys(n), s[t] = [i[0], n[i[0]]];
  return s;
}
var xt = new y("tag:yaml.org,2002:pairs", {
  kind: "sequence",
  resolve: gt,
  construct: yt
}), bt = Object.prototype.hasOwnProperty;
function wt(e) {
  if (e === null) return !0;
  var t, r = e;
  for (t in r)
    if (bt.call(r, t) && r[t] !== null)
      return !1;
  return !0;
}
function _t(e) {
  return e !== null ? e : {};
}
var Et = new y("tag:yaml.org,2002:set", {
  kind: "mapping",
  resolve: wt,
  construct: _t
});
Xe.extend({
  implicit: [
    it,
    st
  ],
  explicit: [
    ut,
    vt,
    xt,
    Et
  ]
});
function L(e) {
  return e === 48 ? "\0" : e === 97 ? "\x07" : e === 98 ? "\b" : e === 116 || e === 9 ? "	" : e === 110 ? `
` : e === 118 ? "\v" : e === 102 ? "\f" : e === 114 ? "\r" : e === 101 ? "\x1B" : e === 32 ? " " : e === 34 ? '"' : e === 47 ? "/" : e === 92 ? "\\" : e === 78 ? "" : e === 95 ? " " : e === 76 ? "\u2028" : e === 80 ? "\u2029" : "";
}
var St = new Array(256), Tt = new Array(256);
for (var C = 0; C < 256; C++)
  St[C] = L(C) ? 1 : 0, Tt[C] = L(C);
const Ct = K.component("vega-editor", {
  props: ["instances"],
  data() {
    return {
      loading: !1,
      sparqlError: !1,
      showAllTabBtn: !1,
      showAllTabs: { display: "none" },
      paneResize: 18,
      bottomPosition: "position-fixed bottom-0 end-0 m-4",
      previewPane: !0,
      authenticated: b.authUser,
      restoredChartId: null,
      results: null,
      chartPub: null,
      specJsonEditorOpts: {
        mode: "code",
        mainMenuBar: !1
      },
      actionType: "Save Chart",
      queryEditorReadOnly: !1
    };
  },
  computed: {
    ...Z("vizEditor", ["uri", "baseSpec", "query", "title", "description", "depiction"]),
    ...H("vizEditor", ["chart"]),
    spec() {
      return W(this.baseSpec, this.results);
    }
  },
  components: {
    splitPane: le,
    VJsoneditor: ae
  },
  methods: {
    ...X("vizEditor", ["loadChart"]),
    ...ee("vizEditor", ["setBaseSpec", "setQuery", "setTitle", "setDescription", "setDepiction", "setChart"]),
    navBack() {
      return b.navTo("view", !0);
    },
    resize(e) {
      e <= 26 ? this.showAllTabBtn = !0 : this.showAllTabBtn = !1;
    },
    showTabNavigation() {
      return this.paneResize = 50, this.showAllTabBtn = !1, this.paneResize = 18;
    },
    async tabNavigation(e) {
      const t = document.getElementById("sparqlc"), r = document.getElementById("vegac"), n = document.getElementById("savec"), i = await document.querySelectorAll(".viz-editor-tabs-item");
      i.length && i.forEach((s) => s.classList.remove("tabselected")), e.srcElement.classList.add("tabselected"), e.srcElement.id == "vegaE" ? (t.classList.remove("viz-editor-show"), n.classList.remove("viz-editor-show"), r.classList.add("viz-editor-show")) : e.srcElement.id == "saveE" ? (t.classList.remove("viz-editor-show"), r.classList.remove("viz-editor-show"), n.classList.add("viz-editor-show")) : (n.classList.remove("viz-editor-show"), r.classList.remove("viz-editor-show"), t.classList.add("viz-editor-show"));
    },
    async getSparqlData() {
      try {
        const e = await te(this.query);
        this.onQuerySuccess(e);
      } catch (e) {
        this.onQueryError(e);
      }
    },
    onQuerySuccess(e) {
      this.sparqlError = !1, this.results = e;
    },
    onQueryError(e) {
      this.sparqlError = !0, console.warn(`SPARQL QUERY ERROR
`, e);
    },
    isSparqlError() {
      return this.sparqlError;
    },
    onSpecJsonError() {
      console.log("bad", arguments);
    },
    async onNewVegaView(e) {
      const t = await e.toImageURL("png").then((n) => fetch(n)).then((n) => n.blob()), r = new FileReader();
      r.addEventListener("load", () => {
        this.setDepiction(r.result);
      }), r.readAsDataURL(t);
    },
    async initializeChart() {
      if (this.loading = !0, this.pageView === "edit")
        await re(this.pageUri);
      else if (this.pageView === "restore")
        return await this.postChartBk(), this.getSparqlData();
      await this.getSparqlData(), this.loading = !1;
    },
    async reloadRestored(e) {
      const t = b.tempChart;
      t && t.chart && await ec.appState.filter((n) => {
        n._id == t.chart._id && (n.restored = !0);
      });
      const r = e == "Editing" ? "Edited" : "Restored";
      return b.$emit("snacks", { status: !0, message: `Chart ${r} Successfully` }), b.$emit("reloadrestored", !0), b.navTo("view", !0);
    },
    async saveChart() {
      const e = this;
      try {
        ie(this.chart).then(async () => e.actionType == "Restore" || e.actionType == "Editing" ? (await b.createBackUp(e.chart, e.restoredChartId, !0, this.selectedTags)).mssg ? e.reloadRestored(e.actionType) : void 0 : (await b.createBackUp(this.chart, null, !0, this.selectedTags), b.$emit("snacks", { status: !0, message: "Chart Saved Successfully" }), b.navTo("view", !0)));
      } catch (t) {
        return alert(t);
      }
    },
    async postChartBk() {
      if (typeof Storage < "u") {
        let e = await JSON.parse(sessionStorage.getItem("chart"));
        if (e)
          this.setChart(e.backup), this.restoredChartId = e.name;
        else
          return;
      } else
        b.$emit("snacks", { status: !0, message: "No Browser Support!!!" });
    },
    defineAction() {
      const e = ne();
      e == "restore" ? (this.actionType = "Restore", this.queryEditorReadOnly = !0) : e == "edit" ? (this.actionType = "Editing", this.queryEditorReadOnly = !1) : this.actionType = "Save Chart";
    },
    goToSparqlTemplates() {
      P(R.SPARQL_TEMPLATES);
    },
    goToDataVoyager() {
      P(R.CHART_EDITOR, "voyager");
    }
  },
  async created() {
    if (b.authUser == null)
      return b.navTo("view", !0);
    this.defineAction(), this.initializeChart();
  }
});
var kt = function() {
  var t = this, r = t._self._c;
  return t._self._setupProxy, r("div", [t.loading ? r("div", { staticClass: "viz-dark-loading" }, [r("spinner", { attrs: { loading: t.loading } })], 1) : t._e(), r("split-pane", { attrs: { "min-percent": t.paneResize, "default-percent": 50, split: "vertical" }, on: { resize: t.resize } }, [r("template", { slot: "paneL" }, [r("div", {}, [r("div", { staticClass: "viz-editor-tabs", on: { click: t.showTabNavigation } }, [r("div", { staticClass: "viz-editor-tabs-item", style: t.showAllTabBtn ? !1 : t.showAllTabs, attrs: { id: "showtabs" } }, [r("span", { staticClass: "material-icons" }, [t._v(" double_arrow ")])]), r("div", { staticClass: "viz-editor-tabs-item tabselected", style: t.showAllTabBtn ? t.showAllTabs : !1, attrs: { id: "sparql" }, on: { click: t.tabNavigation } }, [t._v(" Sparql "), r("span", { staticClass: "visually-hidden" }, [t._v("Enter Query")])]), r("div", { staticClass: "viz-editor-tabs-item", style: t.showAllTabBtn ? t.showAllTabs : !1, attrs: { id: "vegaE" }, on: { click: t.tabNavigation } }, [t._v(" Vega "), r("span", { staticClass: "visually-hidden" }, [t._v("Enter Vega Specs")])]), r("div", { staticClass: "viz-editor-tabs-item", style: t.showAllTabBtn ? t.showAllTabs : !1, attrs: { id: "saveE" }, on: { click: t.tabNavigation } }, [t._v(" " + t._s(t.actionType) + " "), r("span", { staticClass: "visually-hidden" }, [t._v(t._s(t.actionType))])])]), r("div", { staticClass: "viz-editor viz-editor-show", attrs: { id: "sparqlc" } }, [r("button", { staticClass: "btn btn-outline-primary mb-3", attrs: { type: "button" }, on: { click: function(n) {
    return t.goToSparqlTemplates();
  } } }, [t._v(" Build query from template ")]), t.query ? r("yasqe", { attrs: { value: t.query, readOnly: t.queryEditorReadOnly }, on: { input: t.setQuery, "query-success": t.onQuerySuccess, "query-error": t.onQueryError } }) : t._e()], 1), r("div", { staticClass: "viz-editor", attrs: { id: "vegac" } }, [r("div", { staticStyle: { height: "100%" }, attrs: { id: "vega-spec-editor" } }, [r("button", { staticClass: "btn btn-outline-primary mb-3", attrs: { type: "button", disabled: t.sparqlError }, on: { click: function(n) {
    return t.goToDataVoyager();
  } } }, [t._v(" Browse Data Voyager ")]), t.baseSpec ? r("v-jsoneditor", { staticStyle: { height: "98%" }, attrs: { value: t.baseSpec, options: t.specJsonEditorOpts, error: t.onSpecJsonError }, on: { input: t.setBaseSpec } }) : t._e()], 1)]), r("div", { staticClass: "viz-editor", attrs: { id: "savec" } }, [r("form", { staticClass: "title-form", on: { submit: function(n) {
    return n.preventDefault(), t.saveChart.apply(null, arguments);
  } } }, [r("div", { staticStyle: { display: "block", flex: "1" } }, [r("div", { staticClass: "form-floating mb-3" }, [r("input", { staticClass: "form-control", attrs: { type: "text", name: "chart-title", id: "chart-title", placeholder: "Title" }, domProps: { value: t.title }, on: { input: t.setTitle } }), r("label", { attrs: { for: "chart-title" } }, [t._v("Title")])])]), r("div", { staticStyle: { display: "block" } }, [r("div", { staticClass: "form-floating mb-3" }, [r("textarea", { staticClass: "form-control", staticStyle: { height: "100px" }, attrs: { name: "chart-description", id: "chart-description", placeholder: "Description" }, domProps: { value: t.description }, on: { input: t.setDescription } }), r("label", { attrs: { for: "chart-description" } }, [t._v("Description")])])]), r("div", { staticStyle: { display: "block" } }, [r("button", { staticClass: "btn btn-primary", attrs: { type: "submit" } }, [t._v(t._s(t.actionType) + " "), r("i", { staticClass: "bi bi-check text-success" })])])])])])]), r("template", { slot: "paneR" }, [t.sparqlError ? r("div", [r("div", { staticClass: "alert alert-danger" }, [t._v(" The SPARQL query failed to execute. Please ensure syntax is valid and try again. ")])]) : r("div", [r("div", { staticStyle: { "text-align": "right" } }, [r("a", { staticClass: "viz-editor-tabs-item", class: { tabselected: t.previewPane }, on: { click: function(n) {
    n.preventDefault(), t.previewPane = !0;
  } } }, [t._v(" Chart "), r("span", { staticClass: "visually-hidden" }, [t._v("Chart Preview")])]), r("a", { staticClass: "viz-editor-tabs-item", class: { tabselected: t.previewPane == !1 }, on: { click: function(n) {
    n.preventDefault(), t.previewPane = !1;
  } } }, [t._v(" Table "), r("span", { staticClass: "visually-hidden" }, [t._v("Table Preview")])])]), t.previewPane ? r("div", { staticClass: "vega-container" }, [r("keep-alive", [r("vega-lite", { staticStyle: { height: "98%" }, attrs: { spec: t.spec }, on: { "new-vega-view": t.onNewVegaView } })], 1)], 1) : r("div", { staticStyle: { overflow: "scroll" } }, [r("keep-alive", [r("yasr", { attrs: { results: t.results } })], 1)], 1)])])], 2), r("div", { staticClass: "position-fixed bottom-0 end-0 m-4" }, [r("button", { staticClass: "btn btn-primary rounded-circle p-3", attrs: { type: "button" }, on: { click: function(n) {
    return n.preventDefault(), t.navBack.apply(null, arguments);
  } } }, [r("i", { staticClass: "bi bi-arrow-left" }), r("span", { staticClass: "visually-hidden" }, [t._v("Go Back")])])])], 1);
}, Nt = [], At = /* @__PURE__ */ se(
  Ct,
  kt,
  Nt,
  !1,
  null,
  null
);
const Ft = At.exports;
export {
  Ft as default
};
