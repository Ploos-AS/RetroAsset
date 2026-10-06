# Runtime qualification

RetroAsset distinguishes deterministic structural tests from emulator/runtime
qualification.

## Status

| Target | Structural | Runtime |
|---|---|---|
| C64 PRG | PASS | PASS — VICE 3.7.1 + MEGA65 Open ROMs |
| Amiga ILBM uncompressed | round-trip + independent consumer PASS | Amiga runtime: not yet qualified |
| Amiga ILBM ByteRun1 | round-trip + independent consumer PASS | Amiga runtime: not yet qualified |

A native file format is not labelled runtime-qualified until it has been loaded
by the documented emulator/runtime and evidence has been captured.

## Amiga ILBM interoperability evidence

The qualification workflow generates ILBM fixtures with RetroAsset and then
decodes them with an independent consumer rather than RetroAsset's own decoder.
ImageMagick 6.9.12-98 (via ilbmtoppm) successfully reads both fixtures as
16x2, 1-plane ILBM images:

- uncompressed ILBM: PASS
- ByteRun1-compressed ILBM: PASS

This establishes independent file-format interoperability. It is intentionally
not labelled Amiga runtime qualification until the assets are loaded in the
documented Amiga emulator/runtime environment.

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
