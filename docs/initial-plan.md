# Mac ML Helper Plan

## The Plan

Use the Mac as an on-demand ML helper when both laptops are nearby and on the same WiFi network.

Linux does not need to treat the Mac as an always-on server. Start simple:

1. Move input files to the Mac.
2. Run a supported ML job on the Mac.
3. Move outputs back to Linux.

SSH/rsync can make this smoother later, but they are not required for the first version.

## Core Idea

Keep the generic layer thin:

```text
job name + input path + output directory
```

Each actual ML task stays explicit and documented.

## Initial Supported Job: `demucs-vocals`

Karaoke vocal separation using **Demucs `htdemucs_ft`**.

Why this job works well:

- Batch workload
- No real latency sensitivity
- Simple file input/output
- PyTorch can use Apple Silicon MPS/Metal

## Model Notes

| Name | Use |
| --- | --- |
| Demucs `htdemucs_ft` | Default karaoke/stem-separation model. Best first target. |
| MDX-Net / MDX23C | Possible later option for dense mixes. |
| BS-Roformer / Mel-Band Roformer | Strong vocal models, but often less convenient on Apple Silicon. |
| UVR5 / audio-separator | Hosts/wrappers for separation models; useful later, not the first target. |

## Important Constraints

- **MPS**: PyTorch's Apple GPU backend. Test it against CPU before relying on it.
- **ONNX**: Often CPU-bound on Apple Silicon unless specifically accelerated.
- **Sleep**: Use `caffeinate -i` for long Mac jobs.
- **VPN/MDM**: May block network access or Remote Login.
- **Work machine hygiene**: Use scratch dirs and clean up files.

## Mac Setup for Demucs

```bash
brew install ffmpeg uv
uv venv ~/demucs-env
source ~/demucs-env/bin/activate
uv pip install demucs
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

## Demucs Benchmark

First run downloads model weights; do not time that run.

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
time caffeinate -i demucs --two-stems=vocals -d mps -n htdemucs_ft ~/test.mp3
time caffeinate -i demucs --two-stems=vocals -d cpu -n htdemucs_ft ~/test.mp3
```

Only use the Mac for this job if `mps` is clearly faster than `cpu`.

## Optional WiFi Workflow

Manual workflow is fine:

```text
copy file to Mac → run command on Mac → copy stems back
```

If SSH is convenient later:

```bash
ssh <you>@<mac-hostname>.local "echo reachable"
rsync -avz ~/Music/test.mp3 <you>@<mac-hostname>.local:~/scratch/
```

## Adding More ML Jobs

Add jobs explicitly, for example:

```text
demucs-vocals
some-other-ml-task
```

Do not start with arbitrary remote command execution. A small job list is enough.

For each new job, define:

- Job name
- Input type
- Output location
- Environment
- Command
- Whether `mps` or `cpu` is faster

## Verdict

Yes: the same same-WiFi/manual workflow can support multiple ML tasks. SSH can be added later, but the first version can simply use the Mac as an on-demand machine you control directly.
