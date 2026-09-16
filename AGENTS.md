# AGENTS.md

Browser viewer for the [MANO](https://mano.is.tue.mpg.de) hand model. Zero build step:
`index.html` **is** the application. See [README.md](README.md) for the user-facing guide.

## Licensing constraint — read first

MANO is © Max-Planck and licensed for **non-commercial research only**. The model files and
anything derived from them must never be committed, redistributed, or served.

- Never add `*.pkl`, `mano_v1_2/`, or `mano_right.bin` to a commit — not even temporarily.
- Never add code that downloads the model. The user always supplies it by drag-and-drop and it
  is parsed locally in the browser. This is a product promise, stated in the modal and the README.
- The MIT license covers the viewer code only, never the model.

> Known issue: `MANO_LEFT.pkl` and `MANO_RIGHT.pkl` are currently tracked in git (commit
> `168f637`), which contradicts the rule above and `.gitignore`'s own header comment.
> `.gitignore` still has no `*.pkl` pattern.

## Build, run, verify

No build, no bundler, no `package.json`, no tests, no linter, no CI beyond an OpenSpec setup
workflow. Editing `index.html` takes effect on reload.

| Task | Command |
| --- | --- |
| Serve + open browser | `python serve.py` (Windows: `serve.bat` · POSIX: `./serve.sh`) |
| Serve, no browser, fixed port | `python serve.py --port 9000 --no-browser` |
| Expose on LAN | `python serve.py --bind 0.0.0.0` |
| Plain fallback | `python -m http.server 8765` |
| Regenerate the `.bin` model | `python export_mano.py` (needs `numpy`) |

`serve.py` is stdlib-only (Python 3.7+), binds `127.0.0.1:8765` by default and walks up to the
next free port, printing the URL it actually used. `export_mano.py` is a straight-line script
with no CLI, hard-coded to `mano_v1_2/models/MANO_RIGHT.pkl`, and it exits early if that path is
missing (the pkl currently sits at the repo root, so it needs moving first).

Verification is manual only: load the page, drop in a model file, and watch the browser console.
Both parsers log `[mano] …` diagnostics and **throw** on anything they do not understand.

## Architecture

CSS 37–163, markup 165–229, one classic `<script>` 231–1121. Global mutable state plus direct DOM
manipulation — there is no framework, no reactive layer, and inline `onclick="fn()"` attributes
depend on those functions staying at top-level script scope (no IIFE wrapper).

three.js is pinned to **r128** (`THREE` global, cdnjs) with OrbitControls 0.128.0 from jsDelivr's
legacy `examples/js` path. `import`, `type="module"` and `defer` are not used anywhere and must
not be introduced.

| Lines | Area |
| --- | --- |
| 241–316 | `FINGERS` joint table, `pose[16][3]`, imperative slider construction |
| 319–416 | three.js scene, lights, skeleton spheres/bones, local-axis helpers |
| 418–627 | MANO state, `activateMano()`, `rodrigues()`, `updateMesh()` (the LBS hot path) |
| 629–771 | presets, view toggles, camera reset, XYZ gizmo (a **second** WebGL context), theme, render loop |
| 773–999 | `parseManoBin()`, the hand-written pickle VM, `manoStructFromPickleDict()` |
| 1001–1046 | IndexedDB cache |
| 1048–1120 | modal status helpers, `ingest()`, bootstrap IIFE |

## Domain conventions

- **Joint index order**: `0` = wrist (also the global orientation), then Index 1–3, Middle 4–6,
  **Pinky 7–9, Ring 10–12**, Thumb 13–15. Pinky-before-ring is the non-obvious part, and it is
  mirrored in `FINGERS`, the slider DOM, the sphere colors and the bone segments — change one and
  you change all four.
- **`MANO_PARENTS` (index.html:968) is hardcoded on purpose.** The comment above it says
  hardcoding beats "gambling on the pkl's kintree dtype / memory order". Do not "fix" it by
  reading `kintree_table`; that value is parsed only for a diagnostic log. It must stay in sync
  with `export_mano.py`, which does take parents from `kintree_table`.
- **The pickle VM only implements protocol 2** (`index.html:799–936`). A pkl re-saved with
  Python 3's default protocol throws `unsupported pickle opcode`. Extend the interpreter — do not
  swallow the error.
- **The `.bin` layout is a cross-language contract**: the docstring in `export_mano.py` ↔
  `parseManoBin()`. Its 4-byte alignment padding (JSON padded with trailing spaces) exists so the
  browser can build a `Float32Array` view over the payload without copying. Change both sides
  together.
- **The theme system is CSS custom properties only** (`:root` + the `body.light` override).
  Never hardcode a color in a rule; per-slider colors flow through the `--fc` / `--pct` inline
  variables.
- **SEO strings must stay in sync.** Canonical, `og:url`, the JSON-LD `url`, the `Sitemap:` line
  in `robots.txt` and `<loc>` in `sitemap.xml` all carry the same absolute URL. The author/site
  metadata names the upstream project, not this fork.
- UI copy is **English only** — there is no i18n layer.

## Pitfalls

- **IndexedDB has no schema tag.** The store is `mano-viewer` / `files` / key `'model'`, holding
  the raw `ArrayBuffer` with the DB version hardcoded to `1`. Any change to parser semantics or to
  the `.bin` layout silently invalidates existing caches — bump the DB name/version or clear the
  record as part of the change.
- **Cache-hit path returns before the dropzone is wired** (`ingest()` / `init()`) and there is no
  recovery button if that cached blob then fails to parse. Keep this in mind when touching startup.
- **Keep the page openable from `file://`.** No `fetch()`/XHR for local assets, no ES modules.
  IndexedDB and `localStorage` are wrapped in `try/catch` because they legitimately fail on opaque
  origins — keep those guards rather than removing the "dead" error handling.
- **`updateMesh()` must not allocate.** It reuses module-level scratch buffers (`R_local`,
  `G_rot`, `G_trans`, `T_trans`, `poseFeat`) on every slider `input` event.
- **Faces must end up in a `Uint32Array`** for three.js `BufferAttribute`. The `Number()`
  conversion that rescues `BigInt64Array` input is deliberate.
- **`hands_mean` is parsed on both paths but never applied.** If you implement the mean pose, both
  `parseManoBin()` and `manoStructFromPickleDict()` have to do it.
- The dtype byte-order marker is stripped, then a native-endian typed array is built; only
  little-endian hosts are supported. Fortran order is ignored (C order is assumed throughout).
- The explanatory comment blocks in `index.html` are the design record for the MANO math. Keep
  that style; do not strip them.

## Change workflow

This repo uses **OpenSpec** for change management (`.github/agents/openspec.agent.md`,
`.github/prompts/opsx-*.prompt.md`, `.github/skills/openspec-*`).

- Propose before implementing: `openspec new change <name>` → `openspec status --change <name> --json`
  → `openspec instructions <artifact> --change <name> --json` → `openspec validate <name> --json`.
- Run `openspec list --json` first to see what is already in flight.
- `openspec/config.yaml` holds the project context shown to the AI when creating artifacts — keep
  it current, and link to this file rather than duplicating it.
