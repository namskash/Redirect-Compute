# RedirectCompute PLAN

## Goal

Run the same CLI software on two machines on the same WiFi:

- **Hardware provider**: the Mac that actually runs compute jobs.
- **Orchestrator**: the machine where I request jobs and receive outputs.

Start simple: trusted LAN, SSH-based execution using a local SSH alias, explicit user-selected provider, local preference file, no sandboxing in v1. SMB + Mac worker remains an optional fallback if SSH becomes unavailable.

---

## 1. Define the CLI shape

Use one CLI on both machines, for example:

```bash
redirect-compute provider init
redirect-compute provider status

redirect-compute config set-provider <ssh-host-alias>
redirect-compute config get-provider

redirect-compute run <job-name> <input-path> --output <output-dir>
```

Initial behavior:

- The same codebase installs on Mac and orchestrator.
- The orchestrator reaches the Mac over SSH.
- The selected SSH host alias is saved locally on the orchestrator.
- No Mac-side watcher is required for v1.

Suggested local config path:

```text
~/.redirect-compute/config.json
```

Example:

```json
{
  "provider": "mac",
  "remoteScratchDir": "~/redirect-compute/scratch",
  "transport": "ssh"
}
```

---

## 2. Keep v1 transport simple: SSH + scp/rsync

Assume both machines are on the same WiFi and SSH works from the orchestrator to the Mac.

Preferred setup uses a local SSH alias in `~/.ssh/config`:

```sshconfig
Host mac
  HostName 192.168.x.x
  User <mac-username>
```

Orchestrator flow:

1. Resolve configured provider from `~/.redirect-compute/config.json`.
2. Create a unique remote job directory over SSH.
3. Copy inputs to the Mac using `scp` or `rsync`.
4. Run the selected allowlisted job command remotely over SSH.
5. Stream logs to the local terminal.
6. Copy outputs back.
7. Optionally clean remote scratch files.

Example internal flow:

```bash
ssh mac "mkdir -p ~/redirect-compute/scratch/job-123/input ~/redirect-compute/scratch/job-123/output"
scp input.mp3 mac:~/redirect-compute/scratch/job-123/input/
ssh mac "redirect-compute worker run demucs-vocals ~/redirect-compute/scratch/job-123/input/input.mp3 ~/redirect-compute/scratch/job-123/output"
scp -r mac:~/redirect-compute/scratch/job-123/output/ ./output/
```

Optional fallback: SMB shared folder + Mac worker can be added later if SSH becomes blocked or unreliable.

---

## 3. Add an explicit job registry

Even if the long-term idea is “ANY compute,” v1 should use named job definitions.

Each job should declare:

- Name
- Input type
- Output directory
- Required setup
- Exact command
- Device preference: `mps` or `cpu`
- Expected output files

Example built-in job:

```json
{
  "name": "demucs-vocals",
  "command": "caffeinate -i demucs --two-stems=vocals -d mps -n htdemucs_ft {input} -o {output}",
  "env": "~/demucs-env",
  "device": "mps"
}
```

This avoids turning v1 into arbitrary remote command execution by accident. SSH only invokes allowlisted job names through the CLI.

---

## 4. Implement Mac provider setup

On the Mac:

```bash
brew install ffmpeg uv
uv venv ~/demucs-env
source ~/demucs-env/bin/activate
uv pip install demucs
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

Benchmark before choosing MPS:

```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
time caffeinate -i demucs --two-stems=vocals -d mps -n htdemucs_ft ~/test.mp3
time caffeinate -i demucs --two-stems=vocals -d cpu -n htdemucs_ft ~/test.mp3
```

Only default to `mps` if it is clearly faster.

---

## 5. Implement orchestrator-side command flow

For `redirect-compute run demucs-vocals song.mp3 --output ./stems`:

1. Read provider config.
2. Validate SSH connectivity, e.g. `ssh mac "echo ok"`.
3. Create local job ID.
4. Create remote scratch directory.
5. Copy input to remote scratch directory.
6. Execute provider command remotely over SSH.
7. Stream logs to local terminal.
8. Copy output directory back.
9. Print final output path.

Failure handling:

- If provider config is missing, prompt/set it.
- If SSH fails, show the exact failing command.
- If job fails, leave remote scratch dir for debugging unless `--cleanup` is passed.

---

## 6. Preliminary “ANY compute” analysis

The system can theoretically run any batch compute that fits this shape:

```text
input files → remote command → output files
```

Good fits:

- Audio/video processing
- ML inference
- Batch image generation
- Data conversion
- CPU/GPU-heavy scripts
- Jobs where latency does not matter much

Poor fits initially:

- Interactive workloads
- Long-lived services
- Jobs needing complex bidirectional streaming
- Jobs needing GPU sharing or scheduling
- Untrusted third-party code

Recommended path:

1. Start with explicit named jobs.
2. Add custom local job definitions later.
3. Add arbitrary command execution only behind a clear `--allow-unsafe-command` or similar flag.
4. Add sandboxing before running untrusted workloads.

---

## 7. Future sandboxing/security scope

Not required for v1, but important before “ANY compute” becomes real.

Possible safeguards:

- Run jobs under a dedicated macOS user.
- Restrict jobs to a scratch directory.
- Pass explicit input/output paths only.
- Avoid shell interpolation; use argv arrays where possible.
- Maintain an allowlist of job names.
- Add resource limits where available.
- Add containerization only if practical for the workload.
- Never expose this as an open LAN server without authentication.

Security stance for v1:

```text
Trusted user + trusted machines + trusted WiFi + explicit jobs only
```

---

## 8. Suggested implementation phases

### Phase 1: Local CLI skeleton

- Create `redirect-compute` CLI.
- Add config read/write.
- Add `config set-provider` and `config get-provider`.
- Add local `worker run <job>` command.

### Phase 2: SSH remote runner

- Add `run <job> <input> --output <dir>`.
- Copy input to provider using `scp` or `rsync`.
- Execute remote worker command over SSH.
- Pull outputs back.

### Phase 3: First real job

- Add `demucs-vocals`.
- Document Mac setup.
- Benchmark `mps` vs `cpu`.
- Save chosen device in job config.

### Phase 4: Job registry expansion

- Add more explicit jobs.
- Support user-defined job files.
- Add validation for required binaries/envs.

### Phase 5: Safer generic compute

- Add opt-in arbitrary command mode.
- Add sandboxing boundaries.
- Add cleanup policies.
- Add job history/logs.

---

## 9. Minimal v1 success criteria

This should work:

```bash
redirect-compute config set-provider mac
redirect-compute run demucs-vocals ~/Music/song.mp3 --output ./song-stems
```

Expected result:

- Input is copied to the Mac over SSH/scp.
- Demucs runs on the Mac with `caffeinate -i`.
- Stems are copied back to `./song-stems`.
- Provider preference remains saved for future runs.
