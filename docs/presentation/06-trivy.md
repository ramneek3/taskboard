# Trivy

Trivy scans the built backend image and the built frontend image.

## Gate

- Severity: `HIGH,CRITICAL`
- `exit-code: 1`
- `ignore-unfixed: false`
- No `.trivyignore` file

A finding you can patch should fail the job. The Dockerfiles run `apk upgrade` so Alpine security updates are in the image, and Python dependencies are pinned to releases that clear the Starlette HIGH findings seen on the older pin.

## How to talk about a result

Read the log. If the scan is clean, say which images were scanned and that no HIGH or CRITICAL issue was reported. If it is not clean, name one CVE, the package, and whether a fixed version exists. Do not describe a scan you did not run.
