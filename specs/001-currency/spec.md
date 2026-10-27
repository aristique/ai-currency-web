# Feature Specification: BNM currency converter
Feature branch: specs/currency-converter
Created: 2026-10-28
Status: Ready for implementation

## User scenarios and testing

### US1 Convert an amount (P1)
A user enters a positive amount and chooses source/target currencies. The button remains disabled until fields are valid. A successful result shows the converted amount, pair, actual rate date and BNM source.
Acceptance: 100 EUR to MDL uses the validated EUR rate; reversing the pair uses the reciprocal relation. Identical currencies return the same amount.

### US2 Continue without network (P1)
A user refreshes rates without internet. If a validated cache exists, the interface offers a button to use it and labels its date. Without cache, it explains that rates are unavailable and does not invent a result.
Acceptance: an online fetch, container restart and network-disabled fetch preserve the cached response and allow explicit use.

### US3 Choose a rate date (P2)
A user chooses today or an earlier ISO calendar date. If the source returns an empty rate set, try preceding dates up to 14 days back. Show requested and returned dates and a fallback notice.
Acceptance: a simulated empty day followed by a valid prior day succeeds and reports the substitution. A valid weekend response is used as published rather than presumed missing.

## Functional requirements
- FR-001: A browser-based graphical interface with amount, two currency selectors, date, conversion button, result, source and rate date.
- FR-002: Trim amount input; accept decimal point or comma; reject blank, letters, non-finite values, zero, negatives and values above 10^15.
- FR-003: Normalize BNM Value / Nominal to MDL per one currency unit; MDL has a normalized rate of 1.
- FR-004: Compute amount * sourceRate / targetRate with Decimal; round the displayed result to two decimal places with half-up rounding.
- FR-005: Reject malformed XML, invalid dates, duplicate currencies and non-positive or non-finite rates.
- FR-006: Fetch over HTTPS with a bounded timeout, response size limit and no browser CORS dependency.
- FR-007: Save the most recent successful validated XML response atomically in a mounted data folder. Failed fetches do not replace it.
- FR-008: Offer explicit cache use after refresh failure; show a visible cache warning and source date.
- FR-009: Empty source dates fall back by date up to 14 prior days; transport or malformed-source errors are reported immediately with cache availability.
- FR-010: Preserve sources, specs, tests, stage branches and root REPORT.md.

## Entities
- RateSet: source date, currency-to-normalized-Decimal-rate map.
- FetchResult: rate set, requested date, origin (network/cache), warning.
- Conversion: validated amount, source currency, target currency, rounded result.

## Success criteria
All required deterministic tests pass; a real BNM request succeeds; browser checks show a valid conversion and invalid-input handling; an isolated offline check reads persistent cache after restart. Windows/real-device checks remain explicitly pending until performed.

## Assumptions
Local single-user service, no account system, no server deployment. The user explicitly approved Codex instead of Copilot/Antigravity. Month history belongs to Lab 4 and is outside this application's scope.
