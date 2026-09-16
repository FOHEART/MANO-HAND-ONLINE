// ============================================================
//  Wrist cap
//
//  MANO's mesh is an open shell — the arm is simply cut off at the
//  wrist, leaving ONE 16-vertex boundary loop. Left alone you can
//  see straight into the hollow hand from the wrist end, so the
//  model reads as a shell rather than a solid.
//
//  Three properties of that loop make a plain triangle fan the
//  right tool, and they were measured, not assumed:
//
//    · every one of the 16 vertices is skinned 100% to joint 0, so
//      the cap rides the wrist rigidly and can never fight the LBS;
//    · it is convex (zero reflex vertices), so a fan from loop[0]
//      is a valid triangulation — no ear clipping needed;
//    · it is flat to ~3% of its radius, so the fan reads as a disc.
//
//  WINDING — the easy thing to get wrong. On a consistently-wound
//  shell the boundary loop taken in face order circulates so that
//  its Newell normal points INTO the solid (here dot(loop normal,
//  wrist→arm) = −0.99). The cap must face the other way, so the fan
//  is emitted in REVERSE loop order. Get this backwards and the cap
//  is backface-culled: invisible, with no error anywhere.
//
//  No new vertices are introduced, so `posedV` / `outV` / `weights`
//  and the LBS hot path are untouched.
//
//  Loaded as a classic script (see index.html) so it stays a plain
//  global and the page keeps working from `file://` — no modules,
//  no bundler, no build step.
// ============================================================
function capBoundaryLoops(faces, nV) {
  // Collect directed boundary edges, keeping the direction each face
  // traverses them; an edge seen twice is interior and must be dropped.
  const K = nV + 1;
  const dir = new Map();
  for (let t = 0; t < faces.length; t += 3) {
    for (let k = 0; k < 3; k++) {
      const a = faces[t + k], b = faces[t + (k + 1) % 3];
      const key = a < b ? a * K + b : b * K + a;
      if (dir.has(key)) dir.set(key, null);
      else              dir.set(key, [a, b]);
    }
  }
  const next = new Map();
  for (const d of dir.values()) if (d) next.set(d[0], d[1]);

  const extra = [];
  const visited = new Set();
  for (const start of next.keys()) {
    if (visited.has(start)) continue;
    const loop = [];
    let cur = start;
    while (cur !== undefined && !visited.has(cur)) {
      visited.add(cur);
      loop.push(cur);
      cur = next.get(cur);
    }
    if (cur !== start || loop.length < 3) continue;   // open chain / degenerate
    for (let i = 1; i + 1 < loop.length; i++) {
      extra.push(loop[0], loop[i + 1], loop[i]);      // reversed — see WINDING above
    }
  }
  if (!extra.length) return faces;

  const out = new Uint32Array(faces.length + extra.length);
  out.set(faces, 0);
  out.set(extra, faces.length);
  console.log('[mano] wrist cap: +' + (extra.length / 3) + ' tris');
  return out;
}
