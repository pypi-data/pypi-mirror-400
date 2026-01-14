import { r as w, p as D, t as I, u as f, c, w as S, V as A, E as d, k as $, n as k } from "./main-0dzOc6ov.js";
import { l as F } from "./orcid-lookup-BqprP7gj.js";
function P() {
  var a = (/* @__PURE__ */ new Date()).getTime(), t = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(e) {
    var i = (a + Math.random() * 16) % 16 | 0;
    return a = Math.floor(a / 16), (e == "x" ? i : i & 3 | 8).toString(16);
  });
  return t;
}
const h = {
  title: "",
  description: "",
  contactpoint: {
    "@type": "individual",
    "@id": null,
    name: "",
    cpfirstname: "",
    cplastname: "",
    cpemail: ""
  },
  contributor: [],
  author: [],
  datepub: {
    "@type": "date",
    "@value": ""
  },
  datemod: {
    "@type": "date",
    "@value": ""
  },
  refby: [],
  distribution: {
    accessURL: null
  },
  depiction: {
    name: "",
    accessURL: null
  }
}, y = "http://w3.org/ns/dcat#", l = "http://purl.org/dc/terms/", p = "http://www.w3.org/2006/vcard/ns#", u = "http://xmlns.com/foaf/0.1/", r = {
  baseSpec: "http://semanticscience.org/resource/hasValue",
  title: `${l}title`,
  description: `${l}description`,
  contactpoint: `${y}contactpoint`,
  cpemail: `${p}email`,
  cpfirstname: `${p}given-name`,
  cplastname: `${p}family-name`,
  individual: `${p}individual`,
  author: `${l}creator`,
  name: `${u}name`,
  contributor: `${l}contributor`,
  organization: `${u}Organization`,
  person: `${u}Person`,
  onbehalfof: "http://www.w3.org/ns/prov#actedOnBehalfOf",
  specializationOf: "http://www.w3.org/ns/prov#specializationOf",
  datepub: `${l}issued`,
  datemod: `${l}modified`,
  date: "https://www.w3.org/2001/XMLSchema#date",
  refby: `${l}isReferencedBy`,
  // distribution: `${dcat}distribution`,
  depiction: `${u}depiction`,
  hasContent: "http://vocab.rpi.edu/whyis/hasContent",
  accessURL: `${y}accessURL`
}, O = "dataset";
function _(a) {
  var t;
  return arguments.length === 0 ? t = P() : t = a, `${f()}/${O}/${t}`;
}
function U(a) {
  a = Object.assign({}, a), a.context = JSON.stringify(a.context);
  const t = {
    "@id": a.uri,
    "@type": []
  };
  return a["@type"] != null && t["@type"].push(a["@type"]), Object.entries(a).filter(([e, i]) => r[e]).forEach(([e, i]) => {
    var s = {};
    console.log(e), g(i) || (s = b([e, i]), t[r[e]] = [s]);
  }), t;
}
function g(a) {
  if (a === "" || a === null || a === [] || a === "undefined")
    return !0;
  if (Array.isArray(a)) {
    let i = a.length === 0;
    for (var t in a)
      i = i || g(a[t]);
    return i;
  } else if (typeof a == "object") {
    let i = !1;
    for (var e in a)
      i = i || g(a[e]);
    return i;
  }
  return !1;
}
function b([a, t]) {
  if (Array.isArray(t)) {
    var e = [];
    for (var i in t)
      e.push(b([a, t[i]]));
    return e;
  } else {
    var s = {};
    for (var i in t)
      i === "@type" || i === "@value" || i === "@id" ? (s[i] = t[i], r.hasOwnProperty(t[i]) && (s[i] = r[t[i]])) : r.hasOwnProperty(i) ? s[r[i]] = b([r[i], t[i]]) : s["@value"] = t;
    return s;
  }
}
function E() {
  return Object.assign({}, h);
}
function N(a, t) {
  return S(a).then((e) => {
    const i = `${a}_assertion`;
    for (let s of e)
      if (s["@id"] === i) {
        for (let n of s["@graph"])
          if (n["@id"] === t)
            return T(n);
      }
  });
}
function L(a) {
  return w(a).then((t) => {
    if (t.length > 0) {
      const e = t[0].np;
      return N(e, a);
    }
  });
}
function T(a) {
  const t = Object.assign({}, h);
  return Object.entries(h).forEach(([e]) => {
    let i = r[e];
    var s = a[i];
    console.log(s), i in a && typeof s < "u" && (console.log(s[0]), typeof s[0]["@value"] < "u" && (t[e] = a[i][0]["@value"]));
  }), t;
}
async function z(a, t) {
  let e = Promise.resolve();
  a.uri ? e = R(a.uri) : arguments.length === 1 ? a.uri = _() : a.uri = _(t);
  const i = U(a);
  await e;
  try {
    return D(i);
  } catch (s) {
    return alert(s);
  }
}
function R(a) {
  return w(a).then(
    (t) => {
      console.log("in delete"), console.log(t.np), Promise.all(t.map((e) => I(e.np)));
    }
  );
}
async function q(a, t) {
  let e = new FormData(), i = Array(a.length);
  e.append("upload_type", "http://www.w3.org/ns/dcat#Dataset"), Array.from(Array(a.length).keys()).map((o) => {
    e.append(a[o].label, a[o]), i[o] = {
      "@id": `${f()}/dataset/${t}/${a[o].name.replace(/ /g, "_")}`,
      "http://www.w3.org/2000/01/rdf-schema#label": a[o].label
    };
  });
  const s = `${f()}/dataset/${t}`, n = `${window.location.origin}/about?uri=${s}`;
  c.post(
    n,
    e,
    {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    }
  ), Array.from(Array(a.length).keys()).map((o) => {
    i[o]["http://www.w3.org/2000/01/rdf-schema#label"] != "" && D(i[o]);
  });
}
async function M(a, t) {
  const e = `${f()}/dataset/${t}/depiction`, i = `${window.location.origin}/about?uri=${e}`;
  let s = new FormData();
  s.append("upload_type", "http://purl.org/net/provenance/ns#File"), s.append("depiction", a);
  var n = {
    "@id": e,
    file: s
  };
  return await fetch(i, {
    method: "POST",
    body: n,
    headers: {
      Accept: "application/json",
      "Content-Type": "multipart/form-data"
    }
  }), [e, i];
}
async function j(a) {
  return await c.get(`/doi/${a}?view=describe`, {
    headers: {
      Accept: "application/json"
    }
  });
}
async function B(a) {
  const t = await c.get(`/about?uri=${a}&view=describe`, {
    headers: {
      Accept: "application/json"
    }
  });
  var e = t.data;
  if ("@graph" in t.data)
    for (var i in t.data["@graph"])
      t.data["@graph"][i]["@id"] === a && (e = t.data["@graph"][i]);
  return e;
}
function V(a) {
  const t = document.getElementsByClassName("md-menu-content-bottom-start");
  if (t.length >= 1)
    return t[0].style["z-index"] = 12, t[0].style.width = "75%", t[0].style["max-width"] = "75%", status = !0;
}
async function Y(a) {
  const [t, e] = await c.all([
    c.get(
      `/?term=${a}*&view=resolve&type=http://xmlns.com/foaf/0.1/Person`
    ),
    c.get(
      `/?term=${a}*&view=resolve&type=http://schema.org/Person`
    )
  ]).catch((s) => {
    throw s;
  });
  var i = t.data.concat(e.data).sort((s, n) => s.score < n.score ? 1 : -1);
  return i;
}
async function W(a) {
  return (await c.get(
    `/?term=${a}*&view=resolve&type=http://schema.org/Organization`
  )).data;
}
function Z() {
  var a = (/* @__PURE__ */ new Date()).getTime(), t = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(e) {
    var i = (a + Math.random() * 16) % 16 | 0;
    return a = Math.floor(a / 16), (e == "x" ? i : i & 3 | 8).toString(16);
  });
  return t;
}
const m = 0, C = 1, x = 2, v = 3, G = Z(), J = A.component("dataset-uploader", {
  props: [
    "datasetType"
  ],
  data() {
    return {
      dataset: {
        "@type": this.datasetType,
        title: "",
        description: "",
        contactpoint: {
          "@type": "individual",
          "@id": null,
          name: "",
          cpfirstname: "",
          cplastname: "",
          cpemail: ""
        },
        contributor: [],
        author: [],
        datepub: {
          "@type": "date",
          "@value": ""
        },
        datemod: {
          "@type": "date",
          "@value": ""
        },
        refby: [],
        depiction: {
          name: "",
          accessURL: null,
          "@id": null,
          hasContent: null
        }
      },
      generatedUUID: G,
      doi: "",
      doiLoading: !1,
      cpID: "",
      cpIDError: !1,
      contributors: [],
      distr_upload: [],
      rep_image: [],
      // Stepper data
      active: "first",
      first: !1,
      second: !1,
      third: !1,
      //handle uploads
      uploadedFiles: [],
      uploadedImg: [],
      uploadError: null,
      distrStatus: m,
      depictStatus: m,
      isInvalidUpload: !1,
      isInvalidForm: !1,
      authenticated: d.authUser,
      loading: !1,
      loadingText: "Loading Existing Datasets",
      /// search
      query: null,
      selectedAuthorModel: null,
      // TODO: deal with empty orgs
      editableOrgs: !0
    };
  },
  methods: {
    load() {
      let a;
      this.pageView === "new" ? a = Promise.resolve(E()) : a = L(this.pageUri), a.then((t) => {
        this.dataset = t, this.dataset["@type"] = this.datasetType, this.loading = !1;
      });
    },
    dateFormat(a, t) {
      return moment(a).format("YYYY-MM-DD");
    },
    removeElement: function(a) {
      this.contributors.splice(a, 1);
    },
    editDois: function() {
      this.doi !== "" && (this.dataset.refby = "https://dx.doi.org/" + this.doi);
    },
    /* 
      Contributor and author handling: User facing 
    */
    handleContrAuth: function() {
      for (var a in this.contributors) {
        let t = this.contributors[a], e = {
          "@id": t["@id"],
          "@type": "person",
          name: t.name
        };
        t.onbehalfof.name !== null && t.onbehalfof.name !== void 0 && (e.onbehalfof = {
          "@id": t.onbehalfof["@id"],
          "@type": "organization",
          name: t.onbehalfof.name
        }), "specializationOf" in t && (e.specializationOf = {
          "@id": t.specializationOf["@id"]
        }), this.dataset.author.push(e);
      }
    },
    /*
      Distribution and representation handling: server
    */
    handleDistrUpload(a) {
      let t = a;
      for (var e = 0; e < t.length; e++) {
        var i = t[e];
        this.uploadedFiles.some((s) => s.name === i.name) ? alert(`${i.name} has already been uploaded`) : (this.isInvalidUpload = !1, i.label = this.createDefaultLabel(i.name), this.uploadedFiles.push(i));
      }
    },
    /* 
      Helper to generate a default rdfs:label for distributions
    */
    createDefaultLabel(a) {
      var t = a.split(".");
      t.pop();
      var e = t.join("."), i = e.replace(/_/g, " ");
      return i.replace(/[^a-zA-Z0-9]+/g, " ").trim();
    },
    handleImgUpload(a) {
      this.uploadedImg = a;
    },
    removeFile(a) {
      this.uploadedFiles.splice(a, 1);
      const t = document.querySelector("#distrFiles");
      this.distr_upload = [], t.value = "";
    },
    async saveDistribution() {
      let a = this.uploadedFiles;
      if (this.distrStatus = C, !a.length)
        return this.distrStatus = m;
      await q(a, this.generatedUUID).then((t) => {
        this.distrStatus = x;
      }).catch((t) => {
        this.uploadError = t.response, this.distrStatus = v;
      });
    },
    async saveRepImg() {
      const a = this.uploadedImg;
      if (this.depictStatus = C, !a.length)
        return this.depictStatus = m;
      await M(a[0], this.generatedUUID).then((t) => {
        this.dataset.depiction.accessURL = t[1], this.dataset.depiction["@id"] = t[0], this.dataset.depiction.name = a[0].name, this.depictStatus = x;
      }).catch((t) => {
        this.uploadError = t.response, this.depictStatus = v;
      });
    },
    removeImage() {
      document.querySelector("#repImgUploader").value = "", document.querySelector("#depictImg").src = "", this.rep_image = [], this.uploadedImg = [], document.querySelector("#depictWrapper").style.visibility = "hidden";
    },
    // Load a thumbnail of the representative image
    previewFile() {
      const a = document.querySelector("#depictImg"), t = document.querySelector("#depictWrapper"), e = document.querySelector("#repImgUploader").files[0], i = new FileReader(), s = this.dataset;
      i.addEventListener("load", function() {
        t.style.visibility = "visible", a.src = i.result, s.depiction.hasContent = i.result;
      }, !1), e && i.readAsDataURL(e);
    },
    async checkFirstPage() {
      this.doiLoading = !0, this.uploadedFiles.length ? (this.saveRepImg(), this.saveDistribution(), this.doi === "" ? (this.doiLoading = !1, this.setDone("first", "second")) : await this.getDOI()) : (this.isInvalidUpload = !0, this.doiLoading = !1);
    },
    checkSecondPage() {
      const a = this.dataset.title === "", t = this.cpID === null || this.cpID === "", e = this.dataset.contactpoint.cpfirstname === "", i = this.dataset.contactpoint.cplastname === "", s = this.dataset.contactpoint.cpemail === "", n = this.dataset.description === "";
      a || t || e || i || s || n ? this.isInvalidForm = !0 : this.validEmail(this.dataset.contactpoint.cpemail) ? (this.isInvalidForm = !1, this.dataset.contactpoint["@id"] = `http://orcid.org/${this.cpID}`, this.dataset.contactpoint.name = this.dataset.contactpoint.cpfirstname.concat(" ", this.dataset.contactpoint.cplastname), this.setDone("second", "third"), this.handleContrAuth(), this.editDois()) : (this.dataset.contactpoint.cpemail = "", this.isInvalidForm = !0);
    },
    // Handle steppers
    setDone(a, t) {
      this[a] = !0, t && (this.active = t);
    },
    // Use regex for valid email format
    validEmail(a) {
      var t = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      return t.test(a);
    },
    // Submit and post as nanopublication
    submitForm: function() {
      try {
        z(this.dataset, this.generatedUUID).then(() => $(this.dataset.uri, "view"));
      } catch (a) {
        this.uploadError = a.response, this.distrStatus = v;
      }
    },
    async resolveEntityAuthor(a) {
      if (a && a.length > 2)
        try {
          return await Y(a);
        } catch (t) {
          return console.error("Error fetching authors:", t), [];
        }
      return [];
    },
    async resolveEntityInstitution(a) {
      if (a && a.length > 2)
        try {
          return await W(a);
        } catch (t) {
          return console.error("Error fetching organizations:", t), [];
        }
      return [];
    },
    selectedAuthorChange(a) {
      var t;
      a.label ? t = a.label : t = a.name, this.contributors.push({
        "@id": a.node,
        name: t,
        onbehalfof: {
          name: null
        }
      }), this.selectedAuthorModel = null;
    },
    selectedOrgChange(a, t) {
      var e = this.contributors[a].onbehalfof;
      return e.name = t.label, e["@id"] = t.node, t.label;
    },
    //TODO: decide how to deal with not having organizations available
    addAuthor(a) {
      document.createElement("tr"), this.contributors.push({
        "@id": a["@id"],
        name: a.name,
        onbehalfof: {
          name: null
        }
      });
    },
    async getDOI() {
      if (this.doi === "")
        return;
      const a = await j(this.doi);
      await this.useDescribedDoi(a, this.doi).then((t) => {
        this.doiLoading = !1, this.setDone("first", "second");
      }).catch((t) => {
        throw this.doiLoading = !1, this.setDone("first", "second"), t;
      });
    },
    // Fill the form with available data from doi
    async useDescribedDoi(a, t) {
      const e = a.data["@graph"];
      for (var i in e) {
        let n = e[i];
        if (n["@id"] == `http://dx.doi.org/${t}` && ("dc:title" in n && (this.dataset.title = n["dc:title"]), "dc:date" in n && (this.dataset.datemod["@value"] = n["dc:date"]["@value"], this.dataset.datepub["@value"] = n["dc:date"]["@value"]), "dc:creator" in n))
          for (var s in n["dc:creator"])
            await this.getAuthorDescribed(n["dc:creator"][s]["@id"]);
      }
    },
    async getAuthorDescribed(a) {
      const t = await B(a);
      var e = {
        "@id": t["@id"],
        name: t["foaf:name"],
        onbehalfof: {
          name: null
        }
      };
      return "owl:sameAs" in t && (e.specializationOf = {}, e.specializationOf["@id"] = t["owl:sameAs"]["@id"]), "prov:specializationOf" in t && (e.specializationOf = {}, e.specializationOf["@id"] = t["prov:specializationOf"]["@id"]), this.contributors.push(e), e;
    },
    async lookupOrcid() {
      this.cpIDError = !1, await F(this.cpID, "contactPoint").then((a) => {
        let t = a;
        if (t === "Invalid")
          return this.resetContactPoint();
        "schema:familyName" in t && (this.dataset.contactpoint.cplastname = t["schema:familyName"]), "schema:givenName" in t && (this.dataset.contactpoint.cpfirstname = t["schema:givenName"]);
      }).catch((a) => {
        throw a;
      });
    },
    // Clear contact point values
    resetContactPoint() {
      this.cpIDError = !0, this.dataset.contactpoint.cplastname = "", this.dataset.contactpoint.cpfirstname = "";
    },
    // Create dialog boxes
    showNewInstitution() {
      d.$emit("open-new-instance", { status: !0, title: "Add new institution", type: "organization" });
    },
    showNewAuthor() {
      d.$emit("open-new-instance", { status: !0, title: "Add new author", type: "author" }).$on("authorSelected", (a) => this.addAuthor(a));
    },
    // Modify styling of menu to override bad width
    setListStyle(a) {
      return V();
    }
  },
  created() {
    if (this.loading = !0, d.authUser == null)
      return this.loading = !1;
    this.load(), d.$on("isauthenticated", (a) => this.authenticated = a);
  }
});
var X = function() {
  var t = this, e = t._self._c;
  return t._self._setupProxy, e("div", [[e("div", [t.loading ? e("div", [e("spinner", { attrs: { loading: t.loading, text: t.loadingText } })], 1) : t.authenticated ? e("div", [e("div", {}), e("div", { staticClass: "card", staticStyle: { margin: "10px" } }, [e("form", { staticClass: "modal-content", attrs: { action: "", method: "post", enctype: "multipart/form-data", upload_type: "http://www.w3.org/ns/dcat#Dataset" } }, [e("div", { staticClass: "card-body" }, [e("ul", { staticClass: "nav nav-tabs", attrs: { role: "tablist" } }, [e("li", { staticClass: "nav-item", attrs: { role: "presentation" } }, [e("button", { staticClass: "nav-link", class: { active: t.active === "first" }, attrs: { type: "button", role: "tab", disabled: !t.first } }, [t._v("Upload files")])]), e("li", { staticClass: "nav-item", attrs: { role: "presentation" } }, [e("button", { staticClass: "nav-link", class: { active: t.active === "second" }, attrs: { type: "button", role: "tab", disabled: !t.second } }, [t._v("Provide additional info")])]), e("li", { staticClass: "nav-item", attrs: { role: "presentation" } }, [e("button", { staticClass: "nav-link", class: { active: t.active === "third" }, attrs: { type: "button", role: "tab", disabled: !t.third } }, [t._v("Confirm and Submit")])])]), e("div", { staticClass: "tab-content" }, [e("div", { staticClass: "tab-pane fade", class: { show: t.active === "first", active: t.active === "first" }, attrs: { id: "first", role: "tabpanel" } }, [e("div", { staticStyle: { margin: "20px" } }, [e("div", { staticClass: "form-floating mb-3" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.doi, expression: "doi" }], staticClass: "form-control", attrs: { type: "text", id: "doi", placeholder: "DOI of related publication" }, domProps: { value: t.doi }, on: { input: function(i) {
    i.target.composing || (t.doi = i.target.value);
  } } }), e("label", { attrs: { for: "doi" } }, [t._v("DOI of related publication (e.g., 10.1000/000)")])]), e("div", { staticClass: "mb-3", class: { "is-invalid": t.isInvalidUpload } }, [e("label", { staticClass: "form-label", attrs: { for: "distrFiles" } }, [t._v("Select files to upload for this dataset")]), e("input", { staticClass: "form-control", attrs: { type: "file", id: "distrFiles", multiple: "", required: "" }, on: { change: function(i) {
    return t.handleDistrUpload(i.target.files);
  } } }), t.distrStatus === 3 ? e("div", { staticClass: "invalid-feedback d-block" }, [t._v("Error in upload. Please try again")]) : t._e(), t.isInvalidUpload ? e("div", { staticClass: "invalid-feedback" }, [t._v("At least one distribution is required")]) : t._e()]), e("div", { staticClass: "large-12 medium-12 small-12 cell", staticStyle: { margin: "20px" } }, t._l(t.uploadedFiles, function(i, s) {
    return e("div", { key: s + "listing", staticClass: "file-listing" }, [e("div", { staticClass: "row align-items-center", staticStyle: { "margin-left": "10px" } }, [e("div", { staticClass: "col" }, [t._v(t._s(i.name) + " ")]), e("div", { staticClass: "col" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: i.label, expression: "file.label" }], staticClass: "form-control", attrs: { type: "text", id: "label-{{key}}" }, domProps: { value: i.label }, on: { input: function(n) {
      n.target.composing || t.$set(i, "label", n.target.value);
    } } }), e("label", { attrs: { for: "label-{{key}}" } }, [t._v("Label")]), e("div", { staticClass: "form-text" }, [t._v("Provide a human-readable label or leave as the default")])])]), e("div", { staticClass: "col-auto" }, [e("button", { staticClass: "btn btn-outline-danger", attrs: { type: "button" }, on: { click: function(n) {
      return t.removeFile(s);
    } } }, [t._v("Remove file")])])])]);
  }), 0), e("div", { staticClass: "mb-3" }, [e("label", { staticClass: "form-label", attrs: { for: "repImgUploader" } }, [t._v("Select a representative image to use as thumbnail")]), e("input", { staticClass: "form-control", attrs: { type: "file", id: "repImgUploader", accept: "image/*" }, on: { change: function(i) {
    t.handleImgUpload(i.target.files), t.previewFile();
  } } }), t.depictStatus === 3 ? e("div", { staticClass: "text-danger" }, [t._v("Error in upload. Please try again")]) : t._e()]), e("div", { staticStyle: { "margin-left": "40px", visibility: "hidden" }, attrs: { id: "depictWrapper" } }, [e("figure", [e("img", { staticStyle: { height: "200px" }, attrs: { id: "depictImg", src: require(""), alt: "Image preview..." } }), e("figcaption", [t._v(t._s(t.dataset.depiction.name))])]), e("button", { staticClass: "btn btn-outline-secondary ms-2", attrs: { type: "button" }, on: { click: function(i) {
    return t.removeImage();
  } } }, [t._v("Remove image")])])]), e("div", { staticClass: "row align-items-center" }, [e("div", { staticClass: "col-auto" }, [e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: function(i) {
    return t.checkFirstPage();
  } } }, [t._v(" Upload and continue ")])]), t.doiLoading ? e("div", { staticClass: "col-auto" }, [t._m(0)]) : t._e(), e("div", { staticClass: "col" }), e("div", { staticClass: "col" })])]), e("div", { staticClass: "tab-pane fade", class: { show: t.active === "second", active: t.active === "second" }, attrs: { id: "second", role: "tabpanel" } }, [e("div", { staticClass: "row" }, [e("div", { staticClass: "col-12", staticStyle: { margin: "20px" } }, [e("h3", { staticClass: "h4 mt-2" }, [t._v(" General Information ")]), e("div", { staticClass: "form-floating mb-3", class: { "is-invalid": t.isInvalidForm && t.dataset.title === "" } }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.title, expression: "dataset.title" }], staticClass: "form-control", attrs: { type: "text", id: "title", required: "", placeholder: "Title" }, domProps: { value: t.dataset.title }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset, "title", i.target.value);
  } } }), e("label", { attrs: { for: "title" } }, [t._v("Title")]), t.isInvalidForm && t.dataset.title === "" ? e("div", { staticClass: "invalid-feedback" }, [t._v("Title required")]) : t._e()]), e("h5", { staticClass: "mt-4" }, [t._v("Contact Point")]), e("div", { staticClass: "row g-3 align-items-center" }, [e("div", { staticClass: "col-md-3" }, [e("div", { staticClass: "form-floating", class: { "is-invalid": t.isInvalidForm && (t.cpID === null || t.cpID === "") } }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.cpID, expression: "cpID" }], staticClass: "form-control", attrs: { type: "text", id: "cpID", required: "", placeholder: "ORCID Identifier" }, domProps: { value: t.cpID }, on: { change: function(i) {
    return t.lookupOrcid();
  }, input: function(i) {
    i.target.composing || (t.cpID = i.target.value);
  } } }), e("label", { attrs: { for: "cpID" } }, [t._v("ORCID Identifier (e.g., 0000-0001-2345-6789)")]), t.isInvalidForm && (t.cpID === null || t.cpID === "") ? e("div", { staticClass: "invalid-feedback" }, [t._v("ORCID iD required")]) : t._e()])]), e("div", { staticClass: "col-md-2" }, [e("div", { staticClass: "form-floating", class: { "is-invalid": t.isInvalidForm && t.dataset.contactpoint.cpfirstname === "" } }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.contactpoint.cpfirstname, expression: "dataset.contactpoint.cpfirstname" }], staticClass: "form-control", attrs: { type: "text", id: "cpfirstname", required: "", placeholder: "First name" }, domProps: { value: t.dataset.contactpoint.cpfirstname }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset.contactpoint, "cpfirstname", i.target.value);
  } } }), e("label", { attrs: { for: "cpfirstname" } }, [t._v("First name")]), t.isInvalidForm && t.dataset.contactpoint.cpfirstname === "" ? e("div", { staticClass: "invalid-feedback" }, [t._v("Contact point required")]) : t._e()])]), e("div", { staticClass: "col-md-2" }, [e("div", { staticClass: "form-floating", class: { "is-invalid": t.isInvalidForm && t.dataset.contactpoint.cplastname === "" } }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.contactpoint.cplastname, expression: "dataset.contactpoint.cplastname" }], staticClass: "form-control", attrs: { type: "text", id: "cplastname", required: "", placeholder: "Last name" }, domProps: { value: t.dataset.contactpoint.cplastname }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset.contactpoint, "cplastname", i.target.value);
  } } }), e("label", { attrs: { for: "cplastname" } }, [t._v("Last name")]), t.isInvalidForm && t.dataset.contactpoint.cplastname === "" ? e("div", { staticClass: "invalid-feedback" }, [t._v("Contact point required")]) : t._e()])]), e("div", { staticClass: "col-md-3" }, [e("div", { staticClass: "form-floating", class: { "is-invalid": t.isInvalidForm && t.dataset.contactpoint.cpemail === "" } }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.contactpoint.cpemail, expression: "dataset.contactpoint.cpemail" }], staticClass: "form-control", attrs: { type: "email", id: "cpemail", required: "", placeholder: "Email" }, domProps: { value: t.dataset.contactpoint.cpemail }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset.contactpoint, "cpemail", i.target.value);
  } } }), e("label", { attrs: { for: "cpemail" } }, [t._v("Email")]), t.isInvalidForm && t.dataset.contactpoint.cpemail === "" ? e("div", { staticClass: "invalid-feedback" }, [t._v("Valid email required")]) : t._e()])])]), t.cpIDError ? e("div", { staticClass: "alert alert-danger text-center", staticStyle: { "margin-bottom": "20px" } }, [t._v(" No results found for " + t._s(t.cpID) + " ")]) : t._e(), t._m(1), e("div", { staticClass: "form-floating mb-3", class: { "is-invalid": t.isInvalidForm && t.dataset.description === "" } }, [e("textarea", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.description, expression: "dataset.description" }], staticClass: "form-control", staticStyle: { height: "120px" }, attrs: { id: "description", required: "", placeholder: "Text Description" }, domProps: { value: t.dataset.description }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset, "description", i.target.value);
  } } }), e("label", { attrs: { for: "description" } }, [t._v("Text Description")]), t.isInvalidForm && t.dataset.description === "" ? e("div", { staticClass: "invalid-feedback" }, [t._v("Description required")]) : t._e()])]), e("hr", { staticClass: "my-4" }), e("div", { staticClass: "col-12", staticStyle: { margin: "20px" } }, [e("h3", { staticClass: "h4 mt-2 mb-3" }, [t._v(" Contributors ")]), e("div", [e("div", { staticClass: "mb-3" }, [e("autocomplete", { attrs: { "fetch-data": t.resolveEntityAuthor, "display-field": "label", "key-field": "node", placeholder: "Search for Author", "input-class": "form-control" }, on: { select: t.selectedAuthorChange }, scopedSlots: t._u([{ key: "option", fn: function({ item: i }) {
    return [e("span", [t._v(t._s(i.label || i.name))])];
  } }, { key: "no-results", fn: function({ query: i }) {
    return [e("div", [e("p", [t._v('No authors matching "' + t._s(i) + '" were found.')]), e("button", { staticClass: "btn btn-link btn-sm", attrs: { type: "button" }, on: { click: t.showNewAuthor } }, [t._v("Create new")])])];
  } }]), model: { value: t.selectedAuthorModel, callback: function(i) {
    t.selectedAuthorModel = i;
  }, expression: "selectedAuthorModel" } })], 1), e("table", { staticClass: "table", staticStyle: { "border-collapse": "collapse" }, attrs: { width: "100%" } }, [e("tbody", [e("tr", [e("td", { staticStyle: { width: "100%" } }, t._l(t.contributors, function(i, s) {
    return e("tr", { key: s + "contr", staticStyle: { "border-top": "0.5pt lightgray solid" } }, [e("td", { staticStyle: { width: "50%" } }, [t._v(" " + t._s(t.contributors[s].name) + " ")]), t.editableOrgs ? e("td", { staticStyle: { width: "40%" } }, [e("autocomplete", { attrs: { "fetch-data": t.resolveEntityInstitution, "display-field": "label", "key-field": "node", placeholder: "Organization", "input-class": "form-control" }, on: { select: (n) => t.selectedOrgChange(s, n) }, scopedSlots: t._u([{ key: "option", fn: function({ item: n }) {
      return [e("span", [t._v(t._s(n.label || n.name))])];
    } }, { key: "no-results", fn: function({ query: n }) {
      return [e("div", [e("p", [t._v('No organizations matching "' + t._s(n) + '" were found.')]), e("button", { staticClass: "btn btn-link btn-sm", attrs: { type: "button" }, on: { click: t.showNewInstitution } }, [t._v("Create new")])])];
    } }], null, !0), model: { value: i.onbehalfof, callback: function(n) {
      t.$set(i, "onbehalfof", n);
    }, expression: "row.onbehalfof" } })], 1) : e("td", { staticStyle: { width: "30%" } }), e("td", [e("a", { staticStyle: { cursor: "pointer" }, on: { click: function(n) {
      return t.removeElement(s);
    } } }, [t._v("Remove")])])]);
  }), 0)])])])])]), e("hr", { staticClass: "my-4" }), e("div", { staticClass: "col-12", staticStyle: { margin: "20px" } }, [e("h3", { staticClass: "h4 mt-2 mb-3" }, [t._v(" Publication Information ")]), e("div", { staticClass: "w-100" }, [e("div", { staticClass: "row g-3" }, [e("div", { staticClass: "col-md-6" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.datepub["@value"], expression: "dataset.datepub['@value']" }], staticClass: "form-control", attrs: { type: "date", id: "datepub", placeholder: "Date Published" }, domProps: { value: t.dataset.datepub["@value"] }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset.datepub, "@value", i.target.value);
  } } }), e("label", { attrs: { for: "datepub" } }, [t._v("Date Published")])])]), e("div", { staticClass: "col-md-6" }, [e("div", { staticClass: "form-floating" }, [e("input", { directives: [{ name: "model", rawName: "v-model", value: t.dataset.datemod["@value"], expression: "dataset.datemod['@value']" }], staticClass: "form-control", attrs: { type: "date", id: "datemod", placeholder: "Date Last Modified" }, domProps: { value: t.dataset.datemod["@value"] }, on: { input: function(i) {
    i.target.composing || t.$set(t.dataset.datemod, "@value", i.target.value);
  } } }), e("label", { attrs: { for: "datemod" } }, [t._v("Date Last Modified")])])])])])]), e("div", { staticClass: "d-flex gap-2 mb-3" }, [e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: t.checkSecondPage } }, [t._v("Next")]), t.isInvalidForm ? e("div", { staticClass: "text-danger align-self-center" }, [t._v("Check for errors in required fields")]) : t._e()])])]), e("div", { staticClass: "tab-pane fade", class: { show: t.active === "third", active: t.active === "third" }, attrs: { id: "third", role: "tabpanel" } }, [e("h3", { staticClass: "h4", staticStyle: { margin: "10px" } }, [t._v(" Form Results ")]), e("div", { staticClass: "card-body", staticStyle: { margin: "20px" } }, [e("p", [e("strong", [t._v("Title:")]), t._v(" " + t._s(t.dataset.title))]), e("p", [e("strong", [t._v("Contact Point:")]), t._v(" " + t._s(t.dataset.contactpoint.cpfirstname) + " " + t._s(t.dataset.contactpoint.cplastname) + " - " + t._s(t.dataset.contactpoint.cpemail) + " ")]), e("p", [e("strong", [t._v("Text Description:")]), t._v(" " + t._s(t.dataset.description))]), t._m(2), t._l(t.contributors, function(i, s) {
    return e("div", { key: s + "resContr", staticClass: "ms-3" }, [e("span", [t._v(t._s(i.name))]), i.onbehalfof !== null && i.onbehalfof.name !== void 0 ? [t._v(" - " + t._s(i.onbehalfof.name))] : t._e()], 2);
  }), e("p", [e("strong", [t._v("Date Published:")]), t._v(" " + t._s(t.dataset.datepub["@value"]))]), e("p", [e("strong", [t._v("Date Last Modified:")]), t._v(" " + t._s(t.dataset.datemod["@value"]))]), t._m(3), e("div", { staticClass: "ms-3" }, [t._v(" " + t._s(t.dataset.refby) + " ")]), t._m(4), t._l(t.uploadedFiles, function(i, s) {
    return e("div", { key: s + "confirm", staticClass: "ms-3" }, [t._v(" " + t._s(i.name) + " ")]);
  }), e("p", [e("strong", [t._v("Representative Image:")]), t._v(" " + t._s(t.rep_image))])], 2), e("div", { staticClass: "d-flex gap-2 p-3" }, [e("button", { staticClass: "btn btn-primary", attrs: { type: "button" }, on: { click: t.submitForm } }, [t._v(" Submit ")])])])])])])])]) : e("div", [e("div", [t._v("Error: user must be logged in to access this page.")])])])]], 2);
}, H = [function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("div", { staticClass: "spinner-border spinner-border-sm", attrs: { role: "status" } }, [t("span", { staticClass: "visually-hidden" }, [a._v("Loading...")])]);
}, function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("div", { staticClass: "text-center mb-4" }, [a._v(" Don't have an ORCID iD? "), t("a", { attrs: { href: "https://orcid.org/", target: "_blank" } }, [a._v("Create one here")])]);
}, function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("p", [t("strong", [a._v("Contributors")])]);
}, function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("p", [t("strong", [a._v("Related publication:")])]);
}, function() {
  var a = this, t = a._self._c;
  return a._self._setupProxy, t("p", { staticClass: "mt-2" }, [t("strong", [a._v("Distribution(s):")])]);
}], K = /* @__PURE__ */ k(
  J,
  X,
  H,
  !1,
  null,
  null
);
const et = K.exports;
export {
  et as default
};
