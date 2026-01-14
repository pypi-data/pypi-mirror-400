# vmux

Run anything in the cloud. Replace `uv run` with `vmux run`.

**[vmux.sdan.io](https://vmux.sdan.io)** | **[demos](https://vmux.sdan.io/demos.html)**

## Install

```bash
uv tool install vmux-cli
```

## Usage

```bash
vmux run python train.py
# like uv run, but in the cloud. you get a tmux session.

vmux run -d python train.py
# detached. close your laptop. job keeps running (up to 7 days).

vmux attach abc123
# back in your tmux session. from your phone, another laptop, wherever.

vmux run -d -p 8000 python server.py
# expose a port, get a preview URL. websockets just work.

vmux ps
vmux logs -f abc123
vmux stop abc123
```

## How it works

- AST parses your imports, bundles only what you need (skips .git, venvs, checkpoints, etc.)
- auto-detects deps from pyproject.toml, requirements.txt, or PEP 723 inline scripts
- editable packages? we find them, bundle them, install them (transitive deps too)
- runs on [cloudflare containers](https://developers.cloudflare.com/containers/) with 168h keepalive
- real tmux session inside. survives disconnects. reattach from anywhere.
- pre-baked image: pytorch, transformers, numpy, pandas, fastapi

## Limits

- 0.25 vCPU, 1GB RAM per job
- 2GB disk (ephemeral, R2 mount soon)
- 7 day max runtime (indefinitely soon)
- outbound network unrestricted, inbound via preview URLs
- experimental: some jobs may be randomly evicted

## Pricing

Free for the holidays, then $2/mo.

## License

MIT
