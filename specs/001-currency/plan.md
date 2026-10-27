# Implementation plan
Date: 2026-10-28 · Spec: [spec.md](spec.md)

## Technical context
Python 3.12 standard library: urllib, ElementTree, Decimal, http.server, pathlib, threading.
Buildless HTML/CSS/JavaScript served locally by the same process. No third-party application dependencies.
Persistent raw XML cache in /data/latest.xml. pytest is confined to the test image.
Docker Compose app listens on container port 8080 mapped to localhost:8083.
Target: Linux amd64 and Windows 11 AMD Docker Desktop.

## Constitution check
Specs before code: enforced by a dedicated specifications PR before implementation.
Accurate rates: Decimal and Value/Nominal normalization.
Offline: atomic validated XML cache with explicit UI selection.
Reproducibility: pinned Python base, separate test target, local assets.
Honest provenance: root report explicitly records Codex substitution.

## Structure
src/currency/{rates.py,server.py,__main__.py}
web/{index.html,style.css,app.js}
tests/{test_rates.py,test_http.py}
Dockerfile, compose.yaml, REPORT.md
specs/001-currency/{spec.md,plan.md,tasks.md,research.md,data-model.md,analysis.md}

## API
GET /api/rates?date=YYYY-MM-DD: current network data, or understandable error with cache availability.
GET /api/rates?cached=1: validated persistent cache without a network request.
POST /api/convert: JSON amount/from/to using the current validated rate set selected by date or explicit cache mode.
GET /api/health: local service health.
Static assets use an allow-list and local files. JSON responses contain strings for Decimal values.

## Complexity
No framework, database, external frontend assets or cloud hosting is needed for this local educational application.
