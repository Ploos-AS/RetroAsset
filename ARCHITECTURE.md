# RetroAsset architecture

RetroAsset is an AI-assisted compiler/toolchain for native retro-computing assets.

## Design principles

1. **Hardware-authentic output.** A preview that looks retro is not sufficient; target validators decide whether an asset is valid.
2. **Provider-independent AI.** Generation is an optional source stage. The core pipeline must work without any AI service.
3. **Deterministic compilation.** Given a source asset, manifest and tool version, conversion and validation should be reproducible.
4. **Targets own constraints.** Machine-specific rules live in target profiles and validators, not in the generic image pipeline.
5. **Native output first.** PNG/SVG may be previews; ILBM, planar data, character cells and other native forms are first-class outputs.

## Pipeline

source -> import/generate -> RetroAsset IR -> transform -> target validator -> exporter -> native asset

## Target families

- raster: Amiga OCS/ECS/AGA, later Atari ST, EGA/VGA and Mac68k
- character: ANSI/CP437, PETSCII, ATASCII
- tile/sprite: machine-specific tile, Bob and sprite representations

## M0

M0 establishes the IR/manifest, CLI, target registry, Amiga OCS baseline validator and character-art extension points. AI backends are intentionally deferred.
