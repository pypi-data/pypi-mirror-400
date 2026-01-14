# Security Policy

Agent Observatory takes security seriously, especially as it is intended to be used
inside production systems and long-running agent processes.

That said, this project is a **library**, not a hosted service.
Its security model is intentionally narrow and explicit.

---

## Supported Versions

Only the **latest released version** of Agent Observatory is supported with
security updates.

Older versions may receive fixes at maintainer discretion but are not guaranteed.

---

## Security Scope

Agent Observatory is designed as an **observability primitive**.

### In Scope

The following are considered security-relevant:

- crashes or panics triggered by malformed inputs
- unbounded memory growth caused by observability logic
- denial-of-service vectors introduced by tracing or buffering
- unintended data leakage across sessions or spans
- unsafe interaction with OpenTelemetry or exporter pipelines
- vulnerabilities introduced by dependencies

---

### Out of Scope

The following are **explicitly out of scope**:

- vulnerabilities in OpenTelemetry, Jaeger, or external backends
- security of exported data once it leaves the process
- encryption in transit or at rest (handled by exporters / infrastructure)
- application-level authentication or authorization
- user-provided exporter implementations

Agent Observatory does **not**:

- accept untrusted network input
- expose network services
- persist data
- manage credentials or secrets

---

## Reporting a Vulnerability

If you believe you have found a security vulnerability:

**Do not open a public issue.**

Instead, please report it using GitHub’s **Private Security Advisory** feature:

https://github.com/darshankparmar/agent-observatory/security/advisories/new

Please include:

- a clear description of the issue
- affected versions
- a minimal reproduction (if possible)
- potential impact assessment

You will receive an acknowledgment within **72 hours**.

---

## Disclosure Process

1. Report is received and acknowledged
2. Maintainer investigates and validates
3. Fix is developed and reviewed
4. Coordinated release is prepared
5. Public disclosure is made (if applicable)

We aim to minimize disruption while prioritizing user safety.

---

## Secure Usage Guidelines

When using Agent Observatory in production:

- Prefer **inline mode** for short-lived processes
- Always call `shutdown()` in async mode
- Treat exported traces as potentially sensitive
- Apply filtering or redaction in exporters if needed
- Do not attach secrets or credentials to span attributes

---

## Final Note

Agent Observatory is designed to be:

- predictable
- transparent
- low-risk

If observability ever compromises system security, that is considered a **critical bug**.

Thank you for helping keep the project safe.