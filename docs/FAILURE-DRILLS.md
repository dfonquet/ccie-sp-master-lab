# Failure Drills and the XRd BFD Boundary

The failure-drill stage covers link and node loss, IS-IS convergence, LFA,
TI-LFA where supported, BGP PIC, PCE failure, and restoration validation.

## Important BFD platform limitation

XRd Control Plane 24.2.11 accepts the IS-IS BFD configuration used by the lab,
but does not instantiate operational BFD sessions on these virtual data links.
An absent BFD session in this profile is therefore a platform boundary, not
automatically a student configuration fault.

Use the XRd nodes for control-plane configuration, parser practice, LFA and
failure-observation workflows. Use IOL-XE, XRv9k, or physical IOS XR when an
exercise requires live BFD session establishment and timer-driven failure
detection. Capture the selected platform and observed timers in the exercise
evidence instead of spending time troubleshooting unsupported XRd behavior.
