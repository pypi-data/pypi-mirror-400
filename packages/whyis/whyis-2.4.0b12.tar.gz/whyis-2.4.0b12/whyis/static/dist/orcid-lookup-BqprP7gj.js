import { c as a } from "./main-0dzOc6ov.js";
async function c(e, r) {
  if (h(e)) {
    var n = await a.get(`/orcid/${e}?view=describe`, {
      headers: {
        Accept: "application/ld+json"
      }
    }), t = n.data;
    return t = i(t, `http://orcid.org/${e}`, r), t;
  } else
    return "Invalid";
}
function h(e) {
  return /^\d{16}$/.test(e) && (e = e.replace(/^\(?([0-9]{4})\)?([0-9]{4})?([0-9]{4})?([0-9]{4})$/, "$1-$2-$3-$4")), /^\(?([0-9]{4})\)?[-]?([0-9]{4})[-]?([0-9]{4})[-]?([0-9]{4})$/.test(e);
}
function i(e, r, n) {
  if ("@graph" in e) {
    if (!e["@graph"].length)
      return n == "contactPoint" ? this.resetContactPoint() : void 0;
    for (var t in e["@graph"])
      if (e["@graph"][t]["@id"] === r)
        return e["@graph"][t];
  } else
    return e;
}
export {
  c as l
};
