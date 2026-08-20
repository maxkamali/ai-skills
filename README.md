# AI Skills

Reusable AI skills for technical and operational workflows.

## Repository layout

Each skill is self-contained under `skills/<skill-name>/` and can be reviewed, tested, and packaged independently.

```text
skills/
  network-ticket-triage/
    SKILL.md
    agents/
    references/
    scripts/
```

## Published skills

### Network Ticket Triage

Compact Level 1 / Level 2 network-ticket triage. It preserves exact endpoint pairs and one-way test direction, produces a copy-and-paste-ready text handoff, and creates a separate white-background directional diagram.

## Public-data policy

This repository is public-safe by design. Do not commit real operational or identifying data.

Prohibited content includes:

- organization, employer, customer, vendor, or partner names taken from real work
- personal names, personal contact details, or account identifiers
- production IP addresses or prefixes
- internal hostnames, device names, circuit IDs, customer IDs, ticket IDs, or service IDs
- production topology or routing details
- raw customer tickets, logs, screenshots, packet captures, or configuration excerpts containing identifying data

Examples must use synthetic labels and documentation-only address space such as `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`, and `2001:db8::/32`.

See `PUBLICATION_POLICY.md` for the release gate.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`.
