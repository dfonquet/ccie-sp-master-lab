# SRv6 capability acceptance

## Stage A: one-node parser and commit canary

| Gate | Required evidence | Pass condition |
|---|---|---|
| Isolation | Docker container inventory | No other `clab-ccie-sp-*` node is running |
| Image identity | Docker image inspection | Exact local SHA-256 recorded in `READINESS.md` |
| Management | TCP/22 and IOS XR prompt | P1 reachable without retry storms |
| Base IPv6 | Running configuration and interface brief | Loopback committed; no CLI errors |
| Locator parser | Configuration session output | Entire locator hierarchy accepted |
| Locator commit | Commit output and failed-config check | Commit succeeds; failed configuration is empty |
| Operational state | SRv6 locator and SID show commands | Output recorded even if feature is unsupported |
| Rollback | Commit history and rollback result | Pre-SRv6 state restored successfully |
| Restart | Container restart counter and management test | Configuration remains consistent after restart |

Stage A does not prove End, End.X, End.DT4, End.DT6 or packet forwarding.

## Stage B: three-node control plane

| Gate | Required evidence | Pass condition |
|---|---|---|
| IPv6 /127 links | Directed neighbor pings | Four of four endpoint tests pass |
| IS-IS | Neighbor summary | Two expected Level 2 adjacencies are Up |
| Loopbacks | IPv6 route and ping evidence | All three /128 loopbacks reachable |
| Locators | IS-IS database and IPv6 RIB | All three /64 locators advertised and learned |
| Local SIDs | SRv6 SID operational output | Local End SID state classified per node |
| Stability | Docker stats, restarts, logs | Zero unexpected restarts or OOM events |

## Later gates

End.X, SRv6-TE, End.DT4, End.DT6 and VPN steering are separate experiments.
Failure convergence and TI-LFA require a redundant topology and cannot be
claimed using the linear capability mini-lab.

## Full-profile decision

The full SRv6 profile receives `GO` only when the required control-plane and
data-plane behaviors are demonstrated independently. Parser support alone is a
`NO-GO` for service or resiliency claims.
