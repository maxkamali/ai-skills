# Evidence Interpretation Rules

Use this reference only when the ticket includes raw diagnostics or when a claimed fault location needs validation.

## Evidence strength

From strongest to weakest:

1. Simultaneous packet captures or device drop counters during a controlled reproduction.
2. Before-and-after counter deltas tied to the test window.
3. Directional protocol-specific tests with valid controls.
4. One-way tests, isolated logs, and single counter snapshots.
5. Human assertions without included output.

Do not promote a weaker item above a stronger contradictory result.

## Direction handling

- Treat every report and measurement as one-way unless the ticket contains a separate reverse-direction result.
- Label the actual traffic or test direction explicitly as source to destination or destination to source.
- A one-way result says nothing about reverse-direction performance.
- If the customer says the issue is bidirectional, create two reported directions. Confirm each direction independently.
- Never combine two directions into one throughput, loss, latency, or health statement.

## Traceroute and MTR

- Label an MTR row by the direction in which the MTR was run.
- A source-to-destination MTR does not replace a destination-to-source MTR.
- Loss at a middle hop that does not continue through later hops is usually ICMP rate limiting, not forwarding loss.
- `* * *` means no ICMP response from that hop. It does not prove packet loss.
- A trace exposes the forward hop sequence, while probe replies also depend on the return path. Do not use one trace to describe both directions.
- Destination-only ICMP loss can be destination firewall behavior, CPU pressure, or ICMP policing.
- Latency that rises at one hop and returns to normal later is usually control-plane behavior.
- Latency that rises and remains high through the destination may indicate a path change or congestion, but still requires correlation.
- ECMP hop variation is not route flapping by itself.
- For external paths, record carrier names or ASNs separately for each trace direction and preserve their visible order.
- Do not invent a carrier identity from an IP address when the ticket does not establish it.

## Ping

- Successful ping proves only that ICMP echo succeeds at that size and time.
- Clean ping plus poor TCP or UDP can indicate policy, MTU, congestion, host behavior, or protocol-specific handling.
- Test PMTU with DF-set probes and increasing payload sizes when fragmentation or black-holing is plausible.

## Throughput and iPerf

Capture protocol, actual traffic direction, duration, streams, datagram size, target rate, retransmissions, loss, and receiver result.

- Determine which endpoint is the iPerf client and server.
- Account for `iperf3 -R`; reverse mode sends traffic from the server toward the client.
- TCP sender and receiver rates describe one traffic direction. Do not interpret them as opposite directions.
- UDP sender rate is the offered rate, not delivered throughput. Use receiver throughput and receiver loss.
- Slow TCP with loss or retransmissions supports congestion, errors, policing, or drops.
- Slow TCP without loss can involve receiver window, bandwidth-delay product, MSS or PMTU, shaping, single-flow hashing, CPU, or application behavior.
- A short single-stream test across meaningful RTT is weak evidence.
- Compare the reverse direction, parallel streams, and smaller UDP datagrams when useful.
- Same endpoints fast on a private path but slow on a public path points to a path-specific difference. It does not identify a specific gateway or device.
- Same-subnet fast but inter-subnet slow points to the routed path as a class. Require captures, counters, or equivalent evidence before naming a device.
- A relay improving performance proves the relay changes the path or transport behavior. It does not identify the defective element.
- When several endpoint pairs were tested, give each exact pair its own page and keep every directional result on that pair's page.

## Interface counters

- CRC, FCS, runts, giants, carrier errors, and input errors that increase during the test support a physical-layer issue.
- Output discards or queue drops that increase during the test support congestion, microburst, or egress queue pressure.
- Input discards can indicate policing, ACL drops, receive exhaustion, or platform-specific forwarding drops.
- A nonzero historical counter with no timestamped delta is not root-cause evidence.
- Average utilization can miss microbursts. Prefer queue counters or telemetry aligned to the test.
- Link state `up` and zero CRC do not prove clean forwarding above L1.

## L2 switching

Useful evidence includes:

- Correct VLAN membership and trunk allowance.
- Stable MAC learning on the expected interface.
- No MAC moves, STP block, loop-protection event, storm-control drop, or port-security violation during the test.
- ARP or ND resolution consistent with the expected adjacency.

A missing or stale MAC or ARP entry can localize the problem only when collected during reproduction and interpreted with the topology supplied in the ticket.

## L3 routing and forwarding

Useful evidence includes:

- Matching RIB and FIB entries.
- Valid next-hop adjacency.
- Stable routing adjacency and expected route preference.
- Separate forward and reverse path evidence when asymmetry matters.
- Hardware forwarding or exception counters tied to the flow.

A route existing in the RIB does not prove it is installed correctly in hardware or that return routing is valid.

## Policy, security, and policing

- ACL, firewall, uRPF, CoPP, QoS, and policer configuration presence is not evidence of impact.
- Require matching hit counters, logs, hardware drop reasons, or captures.
- Strict uRPF can be relevant in asymmetric designs, but do not call it causal without drop evidence.
- Protocol or port specificity raises policy or middlebox probability.

## Packet captures

For endpoint-to-endpoint localization, prefer simultaneous captures:

- Does the source transmit the packet?
- Does the destination receive it?
- Does the destination respond?
- Does the response return to the source?
- Are retransmissions caused by missing data, missing ACKs, resets, ICMP errors, or PMTU behavior?

Captures prove what reached the capture point, not what happened elsewhere.

## Controls and contradictions

High-value controls include:

- Same source to a different destination.
- Different source to the same destination.
- Reverse direction.
- Same-subnet versus routed traffic.
- Private versus public path.
- Same protocol with a different port or packet size.
- Test before and after the claimed onset.

State contradictions directly. Do not force the data into the customer's narrative.

## Unsafe triage shortcuts

Do not:

- Blame an intermediate MTR hop solely because it shows loss.
- Blame a device solely because it appears in the path.
- Treat a single historical discard count as active congestion.
- Recommend TCP sysctl tuning before identifying the fault domain.
- Clear counters, bounce interfaces, change routes, disable policy, or alter production configuration without approval.
