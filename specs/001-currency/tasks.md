# Implementation tasks
Prerequisites: constitution, spec, plan, research and data model committed before application code.

- [x] T001 [US1] Implement strict XML parsing and nominal normalization in src/currency/rates.py.
- [x] T002 [US1] Implement amount validation, same-currency and bidirectional Decimal conversion.
- [x] T003 [US2] Implement bounded HTTPS retrieval and atomic persistent cache.
- [x] T004 [US3] Implement empty-date fallback and date validation.
- [x] T005 [US1] Implement JSON endpoints and local static serving in src/currency/server.py.
- [x] T006 [US1] Implement accessible responsive UI in web/.
- [x] T007 [US2] Implement cache offer, warning and date/source display.
- [x] T008 Create Docker app/test targets and compose.yaml.
- [x] T009 Add deterministic parser, conversion, input and failure tests in tests/.
- [x] T010 Verify browser, real-source retrieval and persistent offline behavior.
- [x] T011 Complete README and REPORT.md with actual observations and approved tool deviation.
- [ ] T012 Merge implementation and test branches through PRs, preserving process history.

Order: T001–T004 → T005–T008 → T009–T011 → T012. No model/agent delegation is required.
