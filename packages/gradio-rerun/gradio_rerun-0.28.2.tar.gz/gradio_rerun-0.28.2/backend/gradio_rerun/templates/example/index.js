import "../../../../../assets/svelte/svelte_internal_flags_legacy.js";
import * as e from "../../../../../assets/svelte/svelte_internal_client.js";
var m = e.from_html('<div><img alt="" class="svelte-s3apn9"/></div>');
function u(c, t) {
  e.push(t, !1);
  let l = e.prop(t, "value", 8), s = e.prop(t, "type", 8), d = e.prop(t, "selected", 8, !1);
  e.init();
  var i = e.comment(), n = e.first_child(i);
  {
    var v = (r) => {
      var a = m();
      let p;
      var f = e.child(a);
      e.reset(a), e.template_effect(() => {
        p = e.set_class(a, 1, "container svelte-s3apn9", null, p, {
          table: s() === "table",
          gallery: s() === "gallery",
          selected: d()
        }), e.set_attribute(f, "src", (e.deep_read_state(l()), e.untrack(() => l().url)));
      }), e.append(r, a);
    };
    e.if(n, (r) => {
      l() && r(v);
    });
  }
  e.append(c, i), e.pop();
}
export {
  u as default
};
