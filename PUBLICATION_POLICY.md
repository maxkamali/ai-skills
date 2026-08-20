# Publication Policy

This repository must contain only generic, synthetic, public-safe material.

Before a skill or update is published:

1. Replace all real endpoint addresses with documentation-only addresses.
2. Replace real organization and personal names with generic labels.
3. Replace real carriers, sites, devices, hostnames, account IDs, circuit IDs, ticket IDs, and service IDs with synthetic identifiers.
4. Remove email addresses, phone numbers, URLs tied to real organizations, and identifying metadata.
5. Do not include raw tickets, production logs, packet captures, screenshots, or configuration excerpts.
6. Keep examples technically representative without preserving identifying operational details.
7. Run `python3 tools/check_public_data.py .` and resolve every finding before merge.
8. Manually review the diff because automated detection cannot reliably identify every proper name or operational identifier.

Documentation examples should prefer:

- IPv4: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`
- IPv6: `2001:db8::/32`
- private-use ASN examples: `AS64512` through `AS65534`
- labels such as `Source`, `Destination`, `Site A`, `Transit Provider A`, and `edge-router-01`
