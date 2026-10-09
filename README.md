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

## Docs

See `docs/PLAN.md` for the full implementation plan.
