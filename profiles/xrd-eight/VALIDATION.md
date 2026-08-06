# XRd Eight Validation and Acceptance
## Accepted runtime evidence

- `12/12` containers running;
- `8/8` XRd vRouters healthy;
- every XRd container reported restart count zero and `oom=false`;
- AUTO1 and the three IOL-XE nodes remained running;
- no `UnicodeDecodeError`, traceback, fatal, panic or OOM indicator appeared in the final eight-node deployment;
- the host used no swap.

## Configuration acceptance boundary

The first full runtime reused startup files copied into `topology/clab-ccie-sp-xrd-eight/` during an earlier deployment. Consequently, the observed routers retained process `XR8-SP` while the current Source of Truth generates `500-SP`. The topology/runtime is accepted; the regenerated protocol candidate has static validation only until it is deliberately applied or used during a clean deployment.

This distinction is intentional and prevents documentation from claiming live acceptance that was not observed.

## Static checks

```bash
python3 tools/build_xrd_eight.py
python3 tools/render_xrd_eight.py
python3 -m py_compile tools/build_xrd_eight.py tools/render_xrd_eight.py
grep -h '^router isis 500-SP$' configs/xrd-eight/00-foundation/*.cfg | wc -l
grep -hE '^  segment-routing mpls( sr-prefer)?$' configs/xrd-eight/00-foundation/*.cfg | wc -l
grep -h '^   prefix-sid index' configs/xrd-eight/00-foundation/*.cfg | wc -l
```

Expected counts are 8, 16 and 16 respectively.
