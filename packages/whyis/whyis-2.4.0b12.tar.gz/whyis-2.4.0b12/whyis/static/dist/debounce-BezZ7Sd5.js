function i(e, n) {
  let t;
  return function(...o) {
    const u = () => e.apply(this, o);
    clearTimeout(t), t = setTimeout(u, n);
  };
}
export {
  i as d
};
