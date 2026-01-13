# Changelog

All notable changes to `nimbus-bci` will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [0.2.8] - 2025-12-31

### Added
- `StreamingSessionSTS` for correct stateful streaming with `NimbusSTS`.
- Optional-dependency smoke tests for Softmax (JAX) and STS sequence semantics.
- `nimbus_bci/py.typed` typing marker (sdist/wheel completeness).

### Changed
- NimbusSTS prediction semantics: per-row latent evolution is now **opt-in** via `evolve_state=True` in the functional API; sklearn `predict_proba` treats rows as independent by default.
- Made JAX optional via `nimbus-bci[softmax]`; core LDA/GMM/STS can be used without JAX installed.
- Hardened packaging behavior so protected sources are only excluded when explicitly requested and extension build succeeds.
- Data validation: allow arbitrary non-negative label codes (common in MNE) and enforce `chunk_size` in streaming chunk validation.

### Fixed
- Corrected outdated package name hints in MNE compatibility helpers and publishing docs.

## [0.3.0] - 2026-01-05

### Changed
- **Breaking**: renamed the Bayesian class-conditional Gaussian model from **GMM** naming to **QDA** naming across the SDK:
  - `NimbusGMM` → `NimbusQDA`
  - `nimbus_gmm_*` → `nimbus_qda_*`
  - `NimbusModel.model_type`: `"nimbus_gmm"` → `"nimbus_qda"`


