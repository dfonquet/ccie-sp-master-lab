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
