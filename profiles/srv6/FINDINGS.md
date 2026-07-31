# SRv6 capability findings

## Stage A: P1 one-node canary

Assessment date: 2026-07-31

Image: `ios-xr/xrd-control-plane:24.2.11`

Image ID: `sha256:f160dc83ee7e6ef3c9e66254d32237c8d62052f91539da0defc38ddfcc2f36af`

### Result

**GO for the three-node control-plane stage.** This decision does not assert
end-to-end SRv6 forwarding or service support.

| Gate | Result | Evidence summary |
|---|---|---|
| Isolated P1 deployment | PASS | Node filter created only `clab-ccie-sp-srv6-P1` |
| Management | PASS | ICMP 3/3, TCP/22 open and Netmiko CLI login successful |
| Platform | PASS | XRd Control Plane, IOS XR 24.2.11 LNT |
| Link-independent baseline | PASS | Loopback0 Up/Up with `2001:db8:500:abcd::1/128` |
| Baseline rollback | PASS | Loopback removed by rollback and restored by phase reapply |
| Locator parser and commit | PASS | Global `segment-routing srv6` hierarchy committed |
| Locator operational state | PASS | Locator `MAIN`, `2001:db8:600:1::/64`, status Up |
| Local SID allocation | PASS | `2001:db8:600:1:1::`, End (PSP/USD), `sidmgr`, InUse |
| Locator rollback | PASS | Locator and SID removed without affecting Loopback0 |
| Locator reapply | PASS | Locator and End SID recreated successfully |
| Restart persistence | PASS | Loopback, locator and End SID returned after container restart |
| Local CEF programming | PASS | SID /128 programmed as SRv6 Endpoint End (PSP/USD) |
| End behavior with live traffic | NOT TESTED | Requires at least the three-node topology |
| End.X, DT4, DT6 and SRv6-TE | NOT TESTED | Explicitly outside Stage A |

### Operational findings

- The locator detail displayed `Number of SIDs: 0` while the global SRv6 SID
  table simultaneously displayed one End SID in `InUse` state. The SID table
  and CEF entry are retained as direct evidence; the counter discrepancy must
  not be hidden.
- The locator `/64` did not appear as a normal IPv6 RIB route. The locally
  allocated End SID `/128` did appear in CEF as an SRv6 endpoint. This is not
  yet proof that remote locator learning or live SRv6 packet processing works.
- `show ipv6 interface srv6-MAIN` was not accepted even though locator detail
  reported the internal `srv6-MAIN` interface and IFH.
- Restart added two ZTP-generated commits but preserved the user configuration.
- XRd freeze-monitor reported 231 ms during initial boot and 189 ms after the
  controlled restart. There were no crashes, OOM events or unexpected restarts.
- P1 stabilized near 2.0-2.5 GiB RAM. The VM retained approximately 57 GiB
  available memory with no swap use.

### Classification

- Global locator parser: `SUPPORTED`
- Global locator commit: `SUPPORTED`
- Locator and local SID control plane: `SUPPORTED`
- Local End SID CEF programming: `SUPPORTED`
- Live End packet execution: `NOT_TESTED`
- Remote locator advertisement and learning: `NOT_TESTED`
- End.X, End.DT4, End.DT6, SRv6-TE, uSID and TI-LFA: `NOT_TESTED`
