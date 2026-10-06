# Runtime qualification

RetroAsset distinguishes deterministic structural tests from emulator/runtime
qualification.

## Status

| Target | Structural | Runtime |
|---|---|---|
| C64 PRG | PASS when qualification workflow is green | VICE: not yet qualified |
| Amiga ILBM uncompressed | unit-tested / round-trip | Amiga runtime: not yet qualified |
| Amiga ILBM ByteRun1 | structurally tested | Amiga runtime: not yet qualified |

A native file format is not labelled runtime-qualified until it has been loaded
by the documented emulator/runtime and evidence has been captured.

## Planned runtimes

- C64: VICE
- Amiga: project Amiga runtime infrastructure / compatible ILBM consumer

Qualification jobs remain separate from fast unit-test CI.
