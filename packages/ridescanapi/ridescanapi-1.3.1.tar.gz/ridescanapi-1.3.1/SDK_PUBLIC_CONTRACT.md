# RideScan SDK – Public Contract (Internal)

## Status
Internal engineering policy  
Not customer-facing • Not legal • Not marketing

---

## Purpose

This document defines the **public contract** for the RideScan SDK.

The public contract is the **boundary between what RideScan exposes externally and what must remain internal forever**.

Its goals are to:
- protect RideScan’s IP and safety intelligence
- prevent accidental leakage of internal logic
- keep the SDK thin, stable, and enterprise-grade
- provide a clear rulebook for SDK and API development

---

## Core Principle (Non-Negotiable)

> **The SDK exposes what RideScan does, never how RideScan does it.**

---

## What the SDK MAY expose (Allowed)

The SDK may expose **high-level platform capabilities and results**, including:

### Platform Operations
- Robot creation, listing, updates, deletion
- Mission creation, listing, updates, deletion
- File uploads (calibration and inference data)
- Triggering calibration
- Triggering inference
- Retrieving job / model status
- Retrieving final outputs (e.g. risk score, state)

### High-Level Workflow
- Robot → Mission → Data
- Calibration → Inference → Status

These reflect **product usage**, not implementation.

---

## What the SDK MUST NOT expose (Forbidden)

The SDK must never expose or imply:

### ❌ Algorithms & Models
- Model architectures
- Training logic
- Inference logic
- Thresholds
- Confidence computation
- Feature engineering
- Learned parameters or weights
- Uncertainty modelling internals

### ❌ Internal System Details
- Backend service names
- Internal database schema
- Internal identifiers (e.g. `*_pid`)
- Internal field names (e.g. `epochs1`, internal blob names)
- Internal file paths
- Internal routing structure

### ❌ Diagnostic or Reasoning Intelligence
- Stack traces
- Model reasoning
- Sensor-level explanations
- Physical signal thresholds
- Failure explanations that reveal decision logic

**Rule of thumb:**  
If exposing it would help someone reverse-engineer RideScan, it does not belong in the SDK.

---

## Error Handling Contract

### Allowed
- High-level error categories
- Sanitized, generic messages
- Stable, non-descriptive error codes

### Not Allowed
- Stack traces
- Model explanations
- Threshold values
- Backend-specific diagnostics
- Sensor or actuator reasoning

All intelligence remains server-side.

---

## API Design Rules (SDK-side)

- `GET` requests → query parameters only  
- `POST` / `PUT` → JSON body or multipart form  
- Public field names must be:
  - neutral
  - stable
  - backend-agnostic

The SDK may internally translate public fields into backend-specific formats, but this must remain invisible externally.

---

## Versioning Expectations

- **Patch (x.y.Z)**  
  Bug fixes, security hardening, hygiene, naming cleanup

- **Minor (x.Y.z)**  
  New endpoints or optional parameters (non-breaking)

- **Major (X.y.z)**  
  Breaking changes (to be avoided unless absolutely necessary)

---

## Governance

- This contract applies to:
  - SDK code
  - API response design
  - Error handling
  - Public documentation

- Any change that may violate this contract requires:
  - explicit review
  - founder or platform approval

---

## Audience

This document is intended for:
- RideScan engineers
- SDK maintainers
- Contractors contributing to APIs or SDKs

It must **not** be shared externally.

---

## Final Reminder

> **The SDK is a window, not a mirror.**  
> Customers see results. RideScan keeps the intelligence.
