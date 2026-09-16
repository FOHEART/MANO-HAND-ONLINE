# MANO HAND ONLINE VIEWER

### [💻 Live Demo](https://kairui-shi.github.io/MANO-HAND-ONLINE/)  ·  [🖐 Download MANO](https://mano.is.tue.mpg.de)

## Step 0 — Download MANO yourself (required)

The MANO model is **not** included in this repository, will never be, and
is not hosted on the demo page. Register at
[mano.is.tue.mpg.de](https://mano.is.tue.mpg.de), accept the non-commercial
research license, download the archive, and locate `MANO_RIGHT.pkl` inside
`mano_v1_2/models/`. Without this file the viewer has nothing to load.

## Usage

Two ways to run, pick whichever you prefer.

### Option A — Hosted page (zero install)

1. Open the [Live Demo](https://kairui-shi.github.io/MANO-HAND-ONLINE/)
2. Drag `MANO_RIGHT.pkl` into the modal

The file is parsed locally and cached in your browser's IndexedDB, so you
only do this once per machine. No server ever sees the model.

### Option B — Run locally

```bash
git clone https://github.com/Kairui-SHI/MANO-HAND-ONLINE.git
cd MANO-HAND-ONLINE
python -m http.server 8765
```

Open `http://localhost:8765/` and drop the pkl into the modal.

#### One-click launcher (same thing, less typing)

| Platform | Do this | What happens |
| --- | --- | --- |
| Windows | double-click `serve.bat` | starts the server on port 8765 and opens the browser |
| macOS / Linux | `./serve.sh` | same |
| Any | `python serve.py` | same, if you prefer the terminal |

`serve.py` is the actual launcher; `serve.bat` / `serve.sh` just locate a
Python 3 interpreter and hand over to it. Useful flags:

```bash
python serve.py --port 9000     # use another port
python serve.py --no-browser    # start the server only
python serve.py --bind 0.0.0.0  # expose it on your local network
```

Notes:

- It binds to `127.0.0.1` by default, so nothing is exposed to your LAN
  unless you pass `--bind 0.0.0.0`.
- If the port is busy it automatically moves to the next free one and
  prints the URL it actually used.
- On macOS, `chmod +x serve.sh` first, or rename a copy to `serve.command`
  to get a double-clickable file.

## License

- **Viewer code**: MIT.
- **MANO model**: © Max-Planck, non-commercial research license only —
  see [mano.is.tue.mpg.de](https://mano.is.tue.mpg.de).
