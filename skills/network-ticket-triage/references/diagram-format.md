# Pair-Separated Directional Diagram Format

Create one page per exact endpoint pair. Never place several source IPs or several destination IPs in the same endpoint box.

A page represents one unordered pair. The source endpoint remains on the left and the destination endpoint remains on the right. Forward tests use a left-to-right arrow. Reverse tests use a right-to-left arrow.

## Required JSON structure

```json
{
  "title": "Public IPv4 inter-subnet performance",
  "paths": [
    {
      "label": "Affected public path",
      "source": {
        "label": "Source",
        "value": "192.0.2.10",
        "detail": "VPS"
      },
      "destination": {
        "label": "Destination",
        "value": "198.51.100.20",
        "detail": "VPS"
      },
      "assessment": {
        "status": "impaired",
        "text": "Throughput collapse confirmed in both tested directions"
      },
      "topology": {
        "mode": "internal",
        "nodes": [
          {
            "label": "Internal network",
            "detail": "Public routed path"
          }
        ]
      },
      "reported": [
        {
          "direction": "source_to_destination",
          "details": [
            "Client reports extremely slow public IPv4 traffic"
          ]
        }
      ],
      "observed": [
        {
          "direction": "source_to_destination",
          "status": "impaired",
          "details": [
            "TCP measured about 105 Kbit/s"
          ]
        },
        {
          "direction": "destination_to_source",
          "status": "impaired",
          "details": [
            "TCP measured about 105 Kbit/s"
          ]
        }
      ],
      "mtr": {
        "source_to_destination": {
          "status": "not_provided",
          "details": ["Not provided"]
        },
        "destination_to_source": {
          "status": "not_provided",
          "details": ["Not provided"]
        }
      },
      "iperf": {
        "source_to_destination": {
          "status": "impaired",
          "details": [
            "TCP: 105 Kbit/s sender, 0 bit/s receiver, 28 retransmissions"
          ]
        },
        "destination_to_source": {
          "status": "impaired",
          "details": [
            "TCP: 105 Kbit/s sender, 0 bit/s receiver, 34 retransmissions"
          ]
        }
      },
      "notes": [
        "Private-IP control between the same VPSs was about 940 Mbit/s"
      ]
    },
    {
      "label": "Working same-subnet control",
      "source": {
        "label": "Source",
        "value": "203.0.113.30"
      },
      "destination": {
        "label": "Destination",
        "value": "203.0.113.31"
      },
      "assessment": {
        "status": "healthy",
        "text": "Working source-to-destination control; reverse not tested"
      },
      "topology": {
        "mode": "internal",
        "nodes": ["Internal network"]
      },
      "reported": [
        {
          "direction": "source_to_destination",
          "details": [
            "Client supplied this pair as a working control"
          ]
        }
      ],
      "observed": [
        {
          "direction": "source_to_destination",
          "status": "healthy",
          "details": [
            "UDP 0% loss; TCP approximately 9.17 Gbit/s"
          ]
        }
      ],
      "mtr": {
        "source_to_destination": {
          "status": "not_provided",
          "details": ["Not provided"]
        },
        "destination_to_source": {
          "status": "not_provided",
          "details": ["Not provided"]
        }
      },
      "iperf": {
        "source_to_destination": {
          "status": "healthy",
          "details": [
            "TCP approximately 9.17 Gbit/s; UDP 10 Mbit/s with 0% loss"
          ]
        },
        "destination_to_source": {
          "status": "not_provided",
          "details": ["Not provided"]
        }
      }
    }
  ]
}
```

## Top-level fields

- `title` is the diagram title repeated on every page.
- `paths` is a list containing one object per exact endpoint pair.
- Use one path object for `A <-> B`, with separate directional rows inside it.
- Do not create another path object for `B <-> A`.
- Do not combine `A -> B` and `C -> D` in one object, even when both tests show the same symptom.

When the same exact pair has materially different traced carrier paths at different times, create separate path objects and set a distinct `context` string on each one, such as `2026-08-19 17:02 test`.

## Endpoint fields

Each endpoint object supports:

- `label`: heading shown in the box, normally `Source` or `Destination`.
- `value`: one exact IP address, hostname, or explicitly named endpoint. It must be a string, not a list.
- `detail`: optional short role, site, or service label.

The renderer rejects endpoint lists. Use the `detail` field for host or site context rather than adding another endpoint.

## Pair assessment

Each path should include:

```json
"assessment": {
  "status": "impaired",
  "text": "Impaired source to destination; reverse not tested"
}
```

Valid assessment status values:

- `impaired`
- `healthy`
- `inconclusive`
- `neutral`

Keep the text pair-specific and directional.

## Internal topology

Use one `Internal network` node by default. Add named switches or routers only when they materially help triage or are tied to supplied evidence.

```json
"topology": {
  "mode": "internal",
  "nodes": [
    {"label": "Internal network", "detail": "DC routed path"}
  ]
}
```

## External topology

List only carriers or ASNs identified in that exact pair's supplied traces. Preserve the order for each direction. Do not add unknown-carrier boxes.

```json
"topology": {
  "mode": "external",
  "source_to_destination": [
    {"label": "Transit Provider A", "detail": "AS64512"},
    {"label": "Transit Provider B", "detail": "AS64513"}
  ],
  "destination_to_source": [
    {"label": "Transit Provider C", "detail": "AS64514"},
    {"label": "Transit Provider A", "detail": "AS64512"}
  ]
}
```

`source_to_destination` is the trace run from the left endpoint toward the right endpoint. `destination_to_source` is the reverse trace. The renderer places reverse-path carriers right-to-left.

Do not copy one pair's carrier sequence onto another pair unless the thread supplies that same pair-specific trace.

## Reported and observed rows

`reported` and `observed` are lists. Each row belongs only to the page's exact pair.

Reported row fields:

- `direction`: `source_to_destination`, `destination_to_source`, or `not_stated`.
- `details`: one or more short client-claim lines.

Observed row fields:

- `direction`: `source_to_destination`, `destination_to_source`, or `not_stated`.
- `status`: `impaired`, `healthy`, `not_provided`, `inconclusive`, or `neutral`.
- `details`: one or more short measurement lines.

For a bidirectional report or observation, create two rows. Do not summarize it with one double-headed row.

When there is no pair-specific client claim, `reported` may be an empty list. The renderer inserts a gray `No pair-specific report provided` row.

When there is no pair-specific observation, `observed` may be an empty list. The renderer inserts a gray `No pair-specific observation provided` row.

## Mandatory MTR and iPerf rows

Every pair object must contain all four directional test objects:

1. `mtr.source_to_destination`
2. `mtr.destination_to_source`
3. `iperf.source_to_destination`
4. `iperf.destination_to_source`

When a direction was not tested, use:

```json
{
  "status": "not_provided",
  "details": ["Not provided"]
}
```

Do not omit the row. The gray row makes the missing direction visible.

### MTR details

Include only useful pair-specific facts:

- Exact test direction is already established by the row.
- Final-hop loss and latency.
- Persistent loss that continues to the destination.
- Named carriers visible in that trace direction.
- Time or sample count when supplied and useful.

Do not promote isolated intermediate-hop ICMP loss into an end-to-end fault.

### iPerf details

Account for `iperf3 -R` before assigning the result to a direction. Include the most useful pair-specific fields:

- TCP or UDP.
- Duration and parallel-stream count when supplied.
- TCP sender and receiver throughput plus retransmissions.
- UDP offered rate, receiver throughput, and receiver loss.

Sender and receiver figures from one iPerf run describe one traffic direction. Never reinterpret them as opposite directions.

## Status colors

- Client report: blue dashed.
- `impaired`: red solid.
- `healthy`: green solid.
- `not_provided`: gray dashed.
- `inconclusive`: amber solid.
- `neutral`: dark gray solid.

## Output rules

Use PNG only when `paths` contains one object:

```bash
python3 scripts/render_path_diagram.py \
  --spec /tmp/network-triage-diagram.json \
  --output /mnt/data/network-triage-diagram.png
```

Use PDF when `paths` contains more than one object. The renderer creates one white-background page per pair:

```bash
python3 scripts/render_path_diagram.py \
  --spec /tmp/network-triage-diagram.json \
  --output /mnt/data/network-triage-diagram.pdf
```

The renderer rejects a multi-pair PNG because stacking or shrinking pairs would recreate the ambiguity this format is designed to eliminate.
