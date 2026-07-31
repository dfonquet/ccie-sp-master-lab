# Contributing

Contributions that improve reproducibility, validation, documentation, or
CCIE Service Provider study coverage are welcome.

## Workflow

1. Start from the latest `main` branch.
2. Create a focused branch such as `feature/srv6-validation`,
   `fix/inter-as-addressing`, or `docs/bfd-platform-note`.
3. Keep generated artifacts consistent with their CSV Source of Truth.
4. Do not commit licensed network operating-system images, credentials,
   private keys, device backups, packet captures, or generated lab state.
5. Run the relevant checks before opening a pull request.

```bash
python3 -m compileall -q tools
python3 tools/build_lab.py
python3 tools/validate_artifacts.py
git diff --check
```

For profile-specific changes, also run the generator and validator documented
in that profile's README. Live validation must use only one heavy profile at a
time and must record image versions, node counts, protocol checks, restarts,
OOM state, and host resource observations.

## Pull requests

Explain what changed, why it changed, the validation performed, and any known
platform limitation. Prefer small pull requests with no unrelated formatting
or generated-file churn.
