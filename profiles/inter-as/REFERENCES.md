# Referencias — Lab 2 Inter-AS

## Cisco IOS XR

- [OSPFv2 para IPv4 y OSPFv3 para IPv6](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ospf/ospf-configuration-guide-for-cisco-8000-series-routers-cisco-ios-xr-release/ospf-fundamentals-and-basic-configuration-w/information-about-implementing-ospf.html)
- [Verificación de OSPF en IOS XR](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/ospf/ospf-configuration-guide-for-cisco-8000-series-routers-cisco-ios-xr-release/ospf-fundamentals-and-basic-configuration-w/verify-config-and-operation-ospf.html)
- [Route Reflectors en IOS XR](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/bgp/bgp-config-cisco8000/r-wrapper-bgp-routing-optimisation-and-convergence-techniques/c-bgp-route-reflectors.html)
- [Inter-AS Option B para L3VPN](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/l3vpn/l3vpn-config-cisco8000/inter-as-option-b-for-l3vpn-w/inter-as-option-b-l3vpn.html)
- [Configuración y verificación Option B IOS/IOS XR](https://www.cisco.com/c/en/us/support/docs/multiprotocol-label-switching-mpls/mpls/200557-Configuration-and-Verification-of-Layer.html)
- [Diseños BGP/MPLS en IOS XR](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xr-software/217202-cisco-ios-xr-bgp-with-mpls-designs.pdf)

## IETF

- [RFC 2328 — OSPFv2](https://www.rfc-editor.org/rfc/rfc2328.html)
- [RFC 5340 — OSPFv3](https://www.rfc-editor.org/rfc/rfc5340.html)
- [RFC 4271 — BGP-4](https://www.rfc-editor.org/rfc/rfc4271.html)
- [RFC 4456 — BGP Route Reflection](https://www.rfc-editor.org/rfc/rfc4456.html)
- [RFC 4364 — BGP/MPLS IP VPNs](https://www.rfc-editor.org/rfc/rfc4364.html)
- [RFC 4684 — Route Target Constraints](https://www.rfc-editor.org/rfc/rfc4684.html)
- [RFC 8277 — BGP Labeled Unicast](https://www.rfc-editor.org/rfc/rfc8277.html)

RFC 4364, sección 10, es la referencia principal para multi-AS backbones.
Option A mantiene VRFs en los ASBR; Option B intercambia VPN NLRI y etiquetas
entre ASBR; Option C extiende reachability etiquetada para que los RRs/PEs
establezcan MP-BGP entre dominios.
