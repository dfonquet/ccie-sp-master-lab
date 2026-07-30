# Master profile

The stable reference ISP remains AS 500. The target expansion adds P7/P8 and
PE7/PE8 to the existing redundant core. RR1/RR2 remain redundant RR/PCE nodes.

AAA uses two lightweight service containers: TACACS+ for command authorization
and FreeRADIUS for authentication/accounting, always with local fallback.
RPKI uses Krill as the lab CA/repository and Routinator as the validating cache
speaking RTR on TCP/3323.

The expansion must retain staggered XRd startup. P7/P8 start after P5/P6 and
PE7/PE8 after the existing PEs. Resource acceptance gates are: host RAM below
85%, Ubuntu available memory above 12 GiB, no sustained host CPU above 80%, and
all existing validation suites passing.

## Live acceptance evidence

The 30-node expansion was accepted with all containers running, no swap,
17 GiB available inside the 60 GiB Ubuntu VM, and 50.83 GiB free on the
127.85 GiB Windows host. P7/P8/PE7/PE8 formed every expected IS-IS adjacency,
installed IPv4 and IPv6 prefix-SIDs 15-18/615-618, and achieved 100% dual-stack
loopback reachability. PE7/PE8 established VPNv4 and VPNv6 sessions to both
RR1 and RR2.

The transient boot peak reached high Linux load and brief host CPU above 80%;
therefore staggered startup remains mandatory even though steady-state load
and memory passed all gates.
