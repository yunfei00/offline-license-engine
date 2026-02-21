# AGENTS.md

## Goal
Build an offline-first licensing engine for packaged desktop apps (PyInstaller EXE).

## Rules
- Never commit private keys; public key only may live in verifier.
- Keep signer (issuer-side) and verifier (client-side) separated.
- Prefer stable, canonical JSON for signing.
- Add tests for core crypto + license validation.

## Repo layout
Use src/ole/{core,signer,verifier,cli}.
