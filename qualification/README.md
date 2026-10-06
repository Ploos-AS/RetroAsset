# Runtime qualification

RetroAsset distinguishes deterministic structural tests from emulator/runtime
qualification.

## Status

| Target | Structural | Runtime |
|---|---|---|
| C64 PRG | PASS | PASS — VICE 3.7.1 + MEGA65 Open ROMs |
| Amiga ILBM uncompressed | unit-tested / round-trip | Amiga runtime: not yet qualified |
| Amiga ILBM ByteRun1 | encode/decode round-trip PASS | Amiga runtime: not yet qualified |

A native file format is not labelled runtime-qualified until it has been loaded
by the documented emulator/runtime and evidence has been captured.

## Planned runtimes

- C64: VICE
- Amiga: project Amiga runtime infrastructure / compatible ILBM consumer

Qualification jobs remain separate from fast unit-test CI.

## C64 evidence

The public qualification workflow builds the redistributable MEGA65 Open ROMs,
loads the generated PRG directly into VICE 3.7.1, executes the viewer at
`$080d`, stops at its completion point, and compares raw emulator RAM against
the expected generated assets.

Qualified evidence:

- screen RAM `$0400-$07e7`: PASS (1000 bytes)
- color RAM `$d800-$dbe7`: PASS (1000 bytes)
- proprietary Commodore ROMs are not stored in or required by the repository

<!-- qualification-trigger: direct-monitor-load -->
