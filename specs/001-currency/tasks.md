# Implementation tasks
Prerequisites: constitution, spec, plan, research and data model committed before application code.

- [ ] T001 [US1] Implement strict XML parsing and nominal normalization in src/currency/rates.py.
- [ ] T002 [US1] Implement amount validation, same-currency and bidirectional Decimal conversion.
- [ ] T003 [US2] Implement bounded HTTPS retrieval and atomic persistent cache.
- [ ] T004 [US3] Implement empty-date fallback and date validation.
- [ ] T005 [US1] Implement JSON endpoints and local static serving in src/currency/server.py.
- [ ] T006 [US1] Implement accessible responsive UI in web/.
- [ ] T007 [US2] Implement cache offer, warning and date/source display.
- [ ] T008 Create Docker app/test targets and compose.yaml.
- [ ] T009 Add deterministic parser, conversion, input and failure tests in tests/.
- [ ] T010 Verify browser, real-source retrieval and persistent offline behavior.
- [ ] T011 Complete README and REPORT.md with actual observations and approved tool deviation.
- [ ] T012 Merge implementation and test branches through PRs, preserving process history.

Order: T001–T004 → T005–T008 → T009–T011 → T012. No model/agent delegation is required.
