---
name: network-ticket-triage
description: Convert a pasted network incident ticket, NOC thread, customer complaint, or raw diagnostics such as ping, traceroute or MTR, iPerf, packet captures, routing output, and interface counters into compact Level 1 or Level 2 triage. Use when asked to triage, summarize, localize, hand off, or determine what is evidenced in a network trouble report. Always return one copy-and-paste-ready plain-text code block and, when file generation is available, a separate white-background diagram. Keep every exact source/destination pair independent, preserve one-way loss and performance direction, and show trace-visible forward and return carriers per pair. Do not produce a long report or claim root cause without evidence.
---

# Network Ticket Triage

## Objective

Perform only Level 1 or Level 2 network triage:

- Confirm whether the reported symptom is evidenced.
- Evaluate every exact endpoint pair independently.
- Preserve the direction of every claim, trace, loss measurement, and performance test.
- Narrow the scope and likely fault domain.
- Identify the smallest set of read-only checks needed next.
- State whether escalation is ready and which team should receive it.

Do not write an incident report, root-cause analysis, or multi-page narrative. The text deliverable is a short operational note that can be pasted directly into the ticket.

## Required deliverables

Return exactly two deliverables when file generation is available:

1. One concise triage note inside a single fenced `text` code block.
2. One separate white-background diagram file.

Use PNG when the ticket contains one endpoint pair. Use a multi-page PDF when it contains multiple endpoint pairs, with exactly one pair per page. Never compress multiple pairs into one topology or one evidence table.

Outside the text block, include only the diagram link and any citations required by the platform. Never put citations, commentary, or the diagram inside the copy-and-paste block.

If file generation is unavailable, do not substitute Mermaid. Return the text block and one sentence outside it: `Diagram not generated: file-generation tool unavailable.`

## Workflow

1. Remove signatures, greetings, duplicate quoted replies, and unrelated discussion.
2. Extract every exact endpoint pair, test direction, protocol, time window, business impact, and reproduction method.
3. Build a pair inventory before interpreting results.
4. Assign every report and test to exactly one endpoint pair.
5. Separate reported claims from measured observations.
6. Separate source-to-destination evidence from destination-to-source evidence.
7. Evaluate each pair independently, then compare pairs for common patterns.
8. Identify working controls, negative findings, and contradictions.
9. Classify the overall triage status and likely fault domain.
10. Select no more than four read-only next checks.
11. Write the compact triage note.
12. Build the pair-separated JSON specification and create the diagram with `scripts/render_path_diagram.py`.

Read `references/evidence-rules.md` when the ticket contains diagnostic output or when interpreting a claimed fault location. Read `references/diagram-format.md` before creating the diagram specification.

## Endpoint-pair rules

These rules are mandatory:

- One page or panel represents one exact endpoint pair only.
- Never put multiple source IPs or multiple destination IPs in one endpoint box.
- Never aggregate measurements from different endpoint pairs into one row.
- Treat `A -> B` and `B -> A` as opposite directions of the same pair, not two separate pairs.
- Fix the panel orientation once: source stays on the left and destination stays on the right. Reverse tests use a right-to-left arrow.
- Create a separate pair page for a working control. Do not bury it in notes under a failed pair.
- If the same exact pair has materially different carrier paths at different times, create separate pages and label each time window or test context.
- Keep pair-specific conclusions separate. Compare pairs only after each pair has been evaluated.

## Triage boundaries

### Level 1

Collect and normalize:

- Exact source, destination, direction, protocol, port, and time window.
- Whether the issue affects one host, several hosts, a subnet, one site, or all traffic.
- A reproducible test and at least one valid control test when practical.
- Basic reachability, route, ARP or ND, interface state, and error counters when supplied.

### Level 2

Correlate without changing production state:

- Directional tests and packet captures.
- Counter deltas taken around a controlled reproduction.
- Queue, policer, ACL, uRPF, FIB, adjacency, MAC, VLAN, and routing-protocol state.
- PMTU or MSS behavior and protocol-specific differences.
- Forward and reverse trace paths, including trace-visible carriers or ASNs.

Stop before configuration changes, route manipulation, interface resets, policy edits, or service restarts. Mark any requested change as `[CHANGE - senior approval required]`.

## Evidence rules

- Treat human statements as `REPORTED`, even when plausible.
- Treat test output, logs, captures, and counter deltas as `VERIFIED` only when the ticket includes them.
- Never invent topology, hops, carriers, devices, interfaces, timestamps, or causal relationships.
- A one-way test proves only that measured direction. Do not infer the reverse direction.
- A source-to-destination MTR does not substitute for a destination-to-source MTR.
- A clean ping proves ICMP reachability only. It does not prove TCP, UDP, MTU, application, or throughput health.
- A lifetime counter value without a before-and-after delta is weak evidence.
- A working control path is often more valuable than another failed test. Give it its own pair page.
- Configuration presence is not evidence that the feature caused drops. Require matching counters, logs, or captures.
- Do not recommend generic tuning before narrowing the fault domain.
- Attribute measurements with the source and time when available.
- If evidence is insufficient, request the exact missing test and direction.
- Do not claim a specific failing device unless counters, captures, logs, or equivalent evidence isolate it.

## Status classification

Use one overall status:

- `CONFIRMED` - supplied measurements reproduce the reported symptom.
- `PARTIALLY CONFIRMED` - some of the claim is measured, but scope, direction, or magnitude differs.
- `NOT CONFIRMED` - supplied measurements are clean or contradict the claim.
- `INSUFFICIENT DATA` - no valid measurement establishes or rejects the symptom.

Give each endpoint pair its own short assessment in the diagram, such as `Impaired S -> D; reverse not tested` or `Working in both tested directions`.

## Fault-domain classification

Use the narrowest supported category:

- `L1 / physical`
- `L2 / switching`
- `L3 / routing`
- `Policy / security / policing`
- `Host / hypervisor / application`
- `Path-specific`
- `Unknown`

Do not label a specific device as the fault domain unless the evidence supports that device or interface.

## Copy-and-paste output contract

Use one fenced `text` block. Do not use Markdown tables. Target 150 to 220 words. Hard limit: 300 words and 35 nonblank lines.

Use this template and omit sections that add no operational value:

```text
TRIAGE - <ticket reference or short subject>
STATUS: <CONFIRMED | PARTIALLY CONFIRMED | NOT CONFIRMED | INSUFFICIENT DATA>
CONFIDENCE: <High | Medium | Low> - <brief reason>
IMPACT: <one line>
SCOPE: <affected population, protocols, and time window>
REPORTED: <one line describing the client claim without merging endpoint pairs>

PAIR RESULTS:
- <source> -> <destination>: <directional result>; reverse: <result or not tested>
- <one line per operationally relevant pair, including working controls>

WORKING / NOT SEEN:
- <useful control or negative finding; maximum three lines>

ASSESSMENT: <one or two short sentences; no unsupported root-cause claim>
LIKELY AREA: <fault-domain category> - <brief basis>

MISSING:
- <exact missing direction, data, or test; maximum three lines>

NEXT CHECKS:
1. <read-only command or controlled test; maximum four lines>
2. <state who should run it when not obvious>

ESCALATION: <Not ready | Ready for Network | Ready for Systems | Ready for Security | other team> - <one-line reason>
```

Do not write one `PAIR RESULTS` line that combines several sources or several destinations. Keep commands short and directly runnable. Do not include generic advice such as `check the network`.

## Diagram contract

Generate the diagram with the bundled renderer.

### File selection

- One exact pair: create one PNG.
- Multiple exact pairs: create one multi-page PDF with one pair per page.
- Do not create a contact sheet, combined endpoint box, or grouped evidence table.

### Per-pair page

Each page must contain:

1. One source endpoint box on the left.
2. One destination endpoint box on the right.
3. Pair-specific topology at the top.
4. A short pair assessment.
5. Client-reported rows, one per stated direction.
6. Observed rows, one per measured direction.
7. MTR source to destination.
8. MTR destination to source.
9. iPerf source to destination.
10. iPerf destination to source.

### Topology

- For an internal path, use one center box labeled `Internal network` by default. Add named internal devices only when they materially help the triage.
- For an external path, show two separate trace lanes:
  - Source-to-destination carriers visible in that pair's forward trace.
  - Destination-to-source carriers visible in that pair's reverse trace.
- List only carrier names or ASNs supported by the supplied trace, in observed order.
- Do not create unknown-carrier boxes or guess missing transit networks.
- Never reuse one pair's carrier path for another pair unless the ticket supplies the same trace path for both.

### Directional rows

- Every row has at most one arrowhead and represents one direction only.
- Never use a double-headed arrow for a report, observation, MTR, or iPerf result.
- For a bidirectional claim or measurement, create two rows.
- Always include both MTR directions and both iPerf directions on every pair page.
- When a test direction was not supplied, render that row in gray with `Not provided`.
- Reported rows use blue dashed arrows.
- Impaired measured rows use red solid arrows.
- Working measured rows use green solid arrows.
- Inconclusive rows use amber.
- Keep performance values unidirectional. Never turn sender and receiver values into a bidirectional summary.
- For iPerf, determine the actual traffic direction, including whether `-R` was used. Include receiver throughput, loss, retransmissions, target rate, streams, or duration when supplied and useful.
- For MTR, label the direction in which the test was run. Include useful destination loss/latency and persistent loss only.
- Do not return Mermaid source.

Create a JSON specification using `references/diagram-format.md`, then run:

```bash
python3 scripts/render_path_diagram.py --spec /tmp/network-triage-diagram.json --output /mnt/data/network-triage-diagram.pdf
```

Use `.png` instead when the specification contains one pair.

## Prioritization rules

- Use no more than five high-value evidence facts in the text note.
- Prefer the latest valid reproduction, earliest supported onset, strongest control, and evidence that best narrows the domain.
- Use no more than four next checks. Each check must resolve a specific uncertainty.
- Do not repeat the same fact under multiple text headings.
- Include all operationally distinct endpoint pairs in the diagram, even when some are healthy.
- For unrelated faults, triage the primary fault and note the others in one `OTHER:` line unless the user explicitly asks for separate triage notes.

## Escalation readiness

Mark escalation `Ready` only when the note includes:

- Exact affected endpoint pairs.
- A reproducible symptom or valid measurement.
- The measured direction or explicit statement that the reverse direction was not tested.
- At least one control or comparison when practical.
- Evidence that points toward the receiving team.
- The next data that team should collect if a specific device has not been isolated.

Otherwise mark `Not ready` and state the blocking evidence gap.

## Privacy and ticket hygiene

Remove personal email addresses, phone numbers, signatures, and pleasantries. Preserve operational identifiers such as IP addresses, prefixes, hostnames, interfaces, VLANs, ASNs, circuit IDs, and ticket references. Do not draft a customer reply unless explicitly requested.
