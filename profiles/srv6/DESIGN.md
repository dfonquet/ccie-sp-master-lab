# SRv6 profile

This is an IPv6-first profile, not an unverified copy of the SR-MPLS setup.
Before full deployment AUTO1 must test parser and operational support for:

- `segment-routing srv6`
- locator creation and advertisement through IS-IS
- End, End.X, End.DT4 and End.DT6 behaviors
- SRv6 policy/candidate path support
- VPNv4/VPNv6 service steering
- TI-LFA and, separately, uSID

Proposed blocks:

| Purpose | Prefix |
|---|---|
| Loopbacks | `2001:db8:500:abcd::/64` |
| Infrastructure links | `2001:db8:1000::/40` |
| SRv6 locators | `2001:db8:600::/40` |

Unsupported capabilities must be recorded as platform limitations rather than
silently omitted. The first runnable version is a P1-P2-PE1 capability mini-lab;
the full profile is generated only after those checks pass.
