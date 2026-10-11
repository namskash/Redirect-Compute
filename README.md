# RedirectCompute

Run selected compute jobs on a nearby Mac from a Linux orchestrator over trusted local WiFi.

## Current v1 plan

- Use SSH to reach the Mac provider.
- Save the selected provider as a local SSH alias, e.g. `mac`.
- Copy inputs to the Mac with `scp`/`rsync`.
- Run allowlisted jobs remotely.
- Copy outputs back to the orchestrator.

## Example target flow

```bash
redirect-compute config set-provider mac
redirect-compute run demucs-vocals ~/Music/song.mp3 --output ./song-stems
```

## Provider config

`set-provider` saves which SSH alias should be used as the Mac provider.

Example:

```bash
PYTHONPATH=src python -m redirect_compute.cli config set-provider mac
```

This writes a local config file at:

```text
~/.redirect-compute/config.json
```

Example contents:

```json
{
  "provider": "mac",
  "remoteScratchDir": "~/redirect-compute/scratch",
  "transport": "ssh"
}
```

After that, future commands know to run provider operations through:

```bash
ssh mac ...
```

## Docs

See `docs/PLAN.md` for the full implementation plan.
