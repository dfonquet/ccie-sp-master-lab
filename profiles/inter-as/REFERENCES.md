# References — Lab 2 Inter-AS

## Cisco IOS XR

- [OSPFv2 for IPv4 and OSPFv3 for IPv6](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ospf/ospf-configuration-guide-for-cisco-8000-series-routers-cisco-ios-xr-release/ospf-fundamentals-and-basic-configuration-w/information-about-implementing-ospf.html)
- [Verifying OSPF on IOS XR](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ospf/ospf-configuration-guide-for-cisco-8000-series-routers-cisco-ios-xr-release/ospf-fundamentals-and-basic-configuration-w/verify-config-and-operation-ospf.html)
- [Route Reflectors on IOS XR](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/bgp/bgp-config-cisco8000/r-wrapper-bgp-routing-optimisation-and-convergence-techniques/c-bgp-route-reflectors.html)
- [Inter-AS Option B for L3VPN](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/l3vpn/l3vpn-config-cisco8000/inter-as-option-b-for-l3vpn-w/inter-as-option-b-l3vpn.html)
- [IOS/IOS XR Option B configuration and verification](https://www.cisco.com/c/en/us/support/docs/multiprotocol-label-switching-mpls/mpls/200557-Configuration-and-Verification-of-Layer.html)
- [BGP/MPLS designs on IOS XR](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xr-software/217202-cisco-ios-xr-bgp-with-mpls-designs.pdf)

## IETF

- [RFC 2328 — OSPFv2](https://www.rfc-editor.org/rfc/rfc2328.html)
- [RFC 5340 — OSPFv3](https://www.rfc-editor.org/rfc/rfc5340.html)
- [RFC 4271 — BGP-4](https://www.rfc-editor.org/rfc/rfc4271.html)
- [RFC 4456 — BGP Route Reflection](https://www.rfc-editor.org/rfc/rfc4456.html)
- [RFC 4364 — BGP/MPLS IP VPNs](https://www.rfc-editor.org/rfc/rfc4364.html)
- [RFC 4684 — Route Target Constraints](https://www.rfc-editor.org/rfc/rfc4684.html)
- [RFC 8277 — BGP Labeled Unicast](https://www.rfc-editor.org/rfc/rfc8277.html)

RFC 4364 Section 10 is the primary reference for multi-AS backbones. Option A
keeps VRFs on the ASBRs; Option B exchanges VPN NLRI and labels between ASBRs;
Option C extends labeled reachability so RRs and PEs can establish MP-BGP
between domains.
