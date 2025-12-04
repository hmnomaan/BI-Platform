Version 1.0.1 - Development Release

Date: 2025-11-22

Summary
- Bumped package version from 1.0.0 to 1.0.1 in `setup.py`.
- This release focuses on housekeeping for a development patch and documents the next steps to make the platform more dynamic, configurable, and production-ready.

What was changed
- `setup.py`: version updated to `1.0.1`.

Planned enhancements and rationale (next steps)
1) Configuration management (high priority)
   - Implement a dynamic configuration loader that reads YAML/JSON and environment variables with precedence order: env > YAML > default.
   - Provide helper `config_loader.load_config(path, schema=None, env_prefix=None)` to return validated dicts.
   - Apply to `configs/datasource_config.yaml`, `configs/api_config.yaml`, and `configs/shared_config.yaml`.
   - Rationale: avoid hardcoding and allow switching providers via config files or environment in CI/CD.

2) Versioning & packaging (done/short term)
   - Publish `1.0.1` artifacts: sdist (tar.gz) and wheel. Add a small packaging script `build_package.py` already present can be used to create release archive.
   - Add `CHANGELOG.md` with semantic notes going forward.

3) BI Dashboard improvements (module 1)
   - Add a configuration-driven dashboard runner: `bi_dashboard.run(config_path)` reading data sources and chart definitions.
   - Implement `configurable chart factory`: chart types declared by JSON/YAML config, mapping fields to axes and styles.
   - Make chart interactivity data-driven: define linkage rules in `chart_config.json` instead of code.
   - Add data source connectors supporting CSV, SQL (via SQLAlchemy), and REST API with automatic type inference.
   - Add export endpoints: PDF, PNG, and self-contained HTML (static bundle of dashboard) for sharing.
   - Rationale: non-technical users can configure dashboards by editing small config files or using a GUI that persists configs.

4) Third-party API integration engine (module 2)
   - Centralize provider adapters with a `providers` registry and apply the Strategy pattern to switch providers by config.
   - Add robust retry/backoff and provider-failover logic (configurable thresholds and alternate providers list).
   - Integrate secret retrieval abstraction `secrets_manager.get_secret(path)` with pluggable backends: HashiCorp Vault, AWS Secrets Manager, or local encrypted store.
   - Provide standardized wrapper APIs: `send_email()`, `create_signature_envelope()`, `upload_object()` with unified input/output schemas.
   - Add structured API call logging to `logs/api_call_logs.jsonl` with request/response/latency/error details.

5) Testing, metrics, and performance (medium priority)
   - Add unit tests for connectors, providers, and config loader; add integration tests that mock external services.
   - Add basic performance benchmark scripts to validate chart rendering times with up to 1M rows (sampling + aggregation recommended).

6) Documentation & examples (ongoing)
   - Add `CHANGELOG.md`, update `README.md` with quick start for `bi-dashboard` and `api_engine` modules.
   - Provide step-by-step examples: "How to call `send_email()` in Django", "How to load CSV and create a line chart via config".

7) Security & operational concerns
   - Ensure no secrets are stored in repo; add `.env.example` and instructions for Vault integration.
   - Add health-check and metrics endpoints to `api_engine.http_service` for uptime and request counts.

Actionable files to add/modify next (suggested)
- `bi_dashboard/config_loader.py` - dynamic config loader and validator
- `bi_dashboard/factory.py` - chart factory mapping configs to Plotly constructors
- `api_engine/config_manager.py` - extend for secrets manager and provider registry
- `third_party_api/` - add adapters and `api_demo.py` examples
- `CHANGELOG.md` - record user-facing changes

How you can help me next
- Shall I: (A) create the `RELEASE.md` and `CHANGELOG.md` (done for RELEASE), (B) implement the config loader utility and update `bi_dashboard` to use it, or (C) implement provider registry + secrets abstraction for the API engine? Reply with choices or "All" to proceed in sequence.

Notes
- I updated only `setup.py` to avoid broad changes in this patch. Further changes will be incremental and tested.
- If you want me to also tag a git release or build artifacts now, say so and I'll proceed.
