# CCIE SP XRd Eight v2 — Service Provider Engineering Lab

> **A compact but highly capable full-dataplane Service Provider lab for advanced routing, MPLS, Segment Routing, BGP, EVPN and automation studies.** XRd Eight combines eight Cisco XRd vRouter nodes, three IOL-XE customer routers and a dedicated Linux automation environment into a deterministic 12-node architecture designed for implementation, troubleshooting, failure testing and NetDevOps workflows.

![CCIE SP XRd Eight topology](topology.svg)

# CCIE SP XRd Eight v2 — Full-Dataplane Service Provider Lab

> **Compact, reproducible and automation-ready Service Provider lab built with Cisco XRd vRouter, Cisco IOL-XE, Containerlab and Linux-based NetDevOps tooling.**

XRd Eight v2 is a compact Service Provider laboratory designed to provide a realistic full-dataplane environment for advanced routing, MPLS, Segment Routing, BGP, VPN, EVPN, multicast, QoS and automation studies.

The objective of this profile is not to reproduce a large production network node-for-node. Instead, it provides a deliberately small but highly interconnected topology capable of reproducing many of the architectural decisions, failure scenarios and service-provider design patterns encountered in advanced **CCIE Service Provider**, **JNCIE-SP**, network design and NetDevOps practice.

The environment combines:

- Cisco XRd vRouter 26.2.1;
- Cisco IOL-XE 17.12.1;
- Containerlab;
- dual-stack IPv4/IPv6 addressing;
- IS-IS Level 2;
- Segment Routing MPLS;
- deterministic configuration generation;
- topology and addressing validation;
- Linux-based automation through `AUTO1`;
- Git-based infrastructure lifecycle management.

The profile intentionally separates the **provider infrastructure foundation** from the **service configuration layer**.

The repository builds the transport and addressing foundation deterministically, while technologies such as BGP, VPN services, EVPN, PCE, multicast, QoS, SRv6, AAA and RPKI remain available as implementation, troubleshooting and automation exercises.

---

## Project Goals

XRd Eight v2 was designed around several engineering objectives.

### 1. Real dataplane behavior

All provider nodes use **Cisco XRd vRouter**, allowing the lab to exercise forwarding behavior rather than operating purely as a control-plane simulation.

This is particularly important for technologies where dataplane validation matters, including:

- MPLS label forwarding;
- SR-MPLS;
- VPN forwarding;
- EVPN;
- L2VPN;
- multicast forwarding;
- Segment Routing policies;
- QoS;
- traffic-engineering scenarios;
- convergence and failure testing.

### 2. Small topology, high scenario density

Instead of building dozens of routers, the topology uses a carefully selected set of P, PE, RR and CE nodes.

The current design provides:

```text
4  Provider Core routers
3  Provider Edge routers
1  Route Reflector / control-plane router
3  Customer Edge routers
1  Automation node
--------------------------------
12 total nodes
