# BNM Converter Constitution
Version 1.0.0 · Ratified 2026-10-28

1. Specifications precede application code and are preserved in Git before implementation.
2. Decimal arithmetic and currency nominal normalization are mandatory; binary floats are not used for financial calculation.
3. Network errors, empty responses and invalid input produce understandable messages, never fabricated rates.
4. Validated source responses persist across container replacement. Cached data always show their date and require explicit user choice after a failed refresh.
5. The graphical interface and all dependencies run from Docker on Linux and Windows Docker Desktop. No external CDN or host Python installation.
6. Parser, conversion, validation and failure behavior have deterministic tests runnable with one command.
7. Stage branches merge through Pull Requests with meaningful intermediate commits.
8. Reports describe actual tools and observed errors. The approved Codex workflow is not mislabeled as Copilot or Antigravity.

The application is a local educational converter, not a bank transaction service. Changes to requirements must update the specification and corresponding checks.
