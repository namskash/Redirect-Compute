# HTTP Runner PLAN

## Why pivot from SSH-first v1

The original v1 plan used SSH because it is simple, standard, and avoids running a custom service.

However, in the current environment SSH is timing out even though:

- macOS Remote Login is enabled.
- The Mac IP appears correct.
- Both machines appear to be on the same WiFi.

That suggests the blocker may be outside the CLI itself, for example:

- macOS firewall/security policy
- VPN or MDM restrictions
- router/client isolation
- local network rules blocking port 22

Because SSH is proving unreliable for this setup, v1 should move to a Mac-side HTTP runner while keeping SSH documented as a possible future/fallback transport.

## New v1 direction

Run a small local HTTP runner on the Mac and send allowlisted job requests to it from the Linux orchestrator.

High-level shape:

```text
Linux CLI → HTTP request over WiFi → Mac runner → allowlisted local job → output returned to Linux
```

Example target commands:

```bash
# On Mac
redirect-compute runner serve --host 0.0.0.0 --port 8765

# On Linux
redirect-compute config set-provider http://<mac-ip>:8765
redirect-compute provider status
redirect-compute run demucs-vocals ~/Music/song.mp3 --output ./song-stems
```

## Security stance for v1

This is still a trusted-LAN prototype, not an open compute service.

Minimum safeguards:

- Bind to LAN intentionally, not public internet.
- Require a shared token for requests.
- Only expose allowlisted job names.
- Never accept arbitrary shell commands by default.
- Store uploaded inputs in a scratch directory.
- Return explicit output files/directories only.
- Print a warning when serving on `0.0.0.0`.

Suggested config:

```json
{
  "provider": "http://192.168.x.x:8765",
  "transport": "http",
  "token": "local-shared-secret",
  "remoteScratchDir": "~/redirect-compute/scratch"
}
```

## Runner API sketch

### `GET /health`

Returns runner status.

```json
{
  "ok": true,
  "name": "redirect-compute-runner"
}
```

### `GET /jobs`

Returns allowlisted jobs.

```json
{
  "jobs": [
    {
      "name": "demucs-vocals",
      "description": "Separate vocals using Demucs htdemucs_ft"
    }
  ]
}
```

### `POST /run`

Initial simple version can be synchronous.

Request:

- multipart upload containing input file
- `job_name`
- auth token header, e.g. `Authorization: Bearer <token>`

Response:

- either a zip archive of outputs
- or JSON containing a downloadable output path/job id

For v1 simplicity, prefer:

```text
POST /run → zip file response
```

Longer-term async shape:

```text
POST /jobs        → job id
GET /jobs/<id>    → status/logs
GET /jobs/<id>/output.zip → results
```

## Implementation phases

### Phase 1: HTTP runner skeleton

- Add `runner serve` command.
- Implement `GET /health`.
- Implement token check.
- Update `provider status` to support HTTP providers.

### Phase 2: Job listing

- Implement `GET /jobs`.
- Reuse existing local job registry.

### Phase 3: Synchronous run endpoint

- Implement `POST /run` for one uploaded file.
- Save input to scratch directory.
- Run allowlisted local worker job.
- Zip output directory.
- Return zip response.

### Phase 4: Orchestrator HTTP run

- Update `redirect-compute run <job> <input> --output <dir>`.
- Upload input file to provider.
- Save returned zip.
- Extract to output directory.

### Phase 5: Async jobs and logs

- Add job IDs.
- Add polling status endpoint.
- Add log streaming or log retrieval.
- Add cleanup policy.

## SSH remains documented

SSH is not discarded.

It remains useful when available because:

- no custom server is needed
- authentication is mature
- file copy tools are standard
- remote shell execution is easy to inspect

But for this environment, HTTP runner is the more controllable v1 path because we can choose the port, protocol, errors, and auth behavior ourselves.
