# AGENTS.md

## Goal

Use the Mac as an on-demand ML helper when both laptops are available on the same WiFi network.

This is not an always-on server or generic cloud platform. It is a lightweight workflow for moving files to the Mac, running one of a few known ML jobs, and moving results back.

## Preferred Starting Mode

Start with SSH-based orchestration over trusted same-WiFi LAN:

1. Configure the Mac as an SSH host alias, e.g. `mac`.
2. Copy input files to the Mac with `scp` or `rsync`.
3. Run an allowlisted job on the Mac over SSH.
4. Copy outputs back to Linux.

Manual copy/run/copy remains an acceptable fallback for debugging or if SSH is unavailable.

## Job Interface

Each supported job should define:

- Job name
- Input path/type
- Output directory
- Python/env setup
- Exact command
- Expected output files
- Preferred device: `mps` or `cpu`

Possible future shape:

```bash
run-mac-job <job-name> <input-path> <output-dir>
```

## Supported Jobs

### `demucs-vocals`

Karaoke stem separation using **Demucs `htdemucs_ft`**.

- Input: audio file
- Output: separated stems
- Preferred device: `mps`, only if benchmarked faster than `cpu`
- Env: `~/demucs-env`

Mac setup:

```bash
brew install ffmpeg uv
uv venv ~/demucs-env
source ~/demucs-env/bin/activate
uv pip install demucs
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

Benchmark:

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
time caffeinate -i demucs --two-stems=vocals -d mps -n htdemucs_ft ~/test.mp3
time caffeinate -i demucs --two-stems=vocals -d cpu -n htdemucs_ft ~/test.mp3
```

First run downloads model weights; do not time that run.

Only use `mps` if it is clearly faster than `cpu`.

## Network Transport

The v1 transport is SSH plus `scp`/`rsync` on the trusted local WiFi network.

Preferred access uses a local SSH alias:

```sshconfig
Host mac
  HostName 192.168.x.x
  User <mac-username>
```

Example checks/transfers:

```bash
ssh mac "echo reachable"
rsync -avz ~/Music/test.mp3 mac:~/scratch/
```

Manual file transfer + running the command directly on the Mac remains acceptable as a fallback.

## Adding Another ML Job

Add a new explicit job entry. Do not make the runner execute arbitrary commands by default.

For each new job, document:

- Setup commands
- Invocation command
- Input/output contract
- Device choice: `mps` vs `cpu`
- Benchmark result

## Operational Rules

- Treat the Mac as on-demand, not always-on infrastructure.
- Run long Mac jobs with `caffeinate -i` to prevent sleep.
- Use scratch directories on the Mac.
- Clean up inputs and outputs after pulling results back.
- Watch for VPN, MDM, Remote Login, and corporate backup/DLP issues.
- Avoid assuming ONNX models will be fast on Apple Silicon; they are often CPU-bound.
- If the Mac is not faster for a job, run it locally on Linux instead.
