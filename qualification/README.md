# Runtime qualification

RetroAsset distinguishes deterministic structural tests from emulator/runtime
qualification.

## Status

| Target | Structural | Runtime |
|---|---|---|
| C64 PRG | PASS | PASS — VICE 3.7.1 + MEGA65 Open ROMs |
| Amiga ILBM uncompressed | round-trip + independent consumer PASS | PASS — Q3 AROS/m68k under FS-UAE |
| Amiga ILBM ByteRun1 | round-trip + independent consumer PASS | PASS — Q3 AROS/m68k under FS-UAE |

A native file format is not labelled runtime-qualified until it has been loaded
by the documented emulator/runtime and evidence has been captured.

## Amiga ILBM interoperability evidence

The qualification workflow generates ILBM fixtures with RetroAsset and then
decodes them with an independent consumer rather than RetroAsset's own decoder.
ImageMagick 6.9.12-98 (via ilbmtoppm) successfully reads both fixtures as
16x2, 1-plane ILBM images:

- uncompressed ILBM: PASS
- ByteRun1-compressed ILBM: PASS

This establishes independent file-format interoperability.

## Amiga AROS/m68k runtime evidence

The qualification workflow embeds the exact generated uncompressed and
ByteRun1 fixtures into an independent C verifier, cross-builds it as an m68k
Amiga Hunk with the qualified `Ploos-AS/amiga-dev` toolchain, and hands the
Q1 artifact to the stable `Ploos-AS/amiga-runtime` consumer contract.

GitHub Actions run `37433194653`, job `amiga-aros-q3`, passed with the
immutable runtime image `ghcr.io/ploos-as/amiga-runtime:sha-fd7cc88`.
The runtime prepared the redistributable AROS/m68k environment and executed
the project contract with profile `a1200-020-aros`. The contract requires
both guest markers:

- `RETROASSET_ILBM_UNCOMPRESSED_PASS 16x2 1-plane`
- `RETROASSET_ILBM_BYTERUN1_PASS 16x2 1-plane`

A successful contract run requires these lines, so both ILBM variants are
qualified at Q3 under AROS/m68k with FS-UAE. The strengthened verifier also
requires the exact source fixture palette (black/white) and decoded planar
bytes (`55 55 aa aa`). Actions run `37466194514` passed these exact-content
checks for both uncompressed and ByteRun1 ILBM.

This is redistributable AROS/m68k runtime evidence. It is **not** Q4 classic
AmigaOS qualification and must not be reported as such.

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
