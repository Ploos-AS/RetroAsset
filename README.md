# RetroAsset

**AI-assisted compiler and validator for genuine retro-computing assets.**

RetroAsset turns generated, imported or hand-authored source material into assets that obey the constraints of real retro platforms. The goal is not merely to make modern images *look* retro.

## Status

M0 foundation is under development. The first executable target is **Amiga OCS**.

Planned target families include:

- Amiga OCS / ECS / AGA
- ANSI / IBM CP437
- Commodore PETSCII
- Atari ATASCII
- Atari ST
- DOS EGA / VGA
- Mac68k

## Pipeline

```text
source
  |
  +-- hand authored
  +-- imported
  +-- AI generated
  |
  v
RetroAsset IR / manifest
  |
  v
deterministic transforms
  |
  v
target validator
  |
  v
native exporter
```

AI is optional and provider-independent. Native target validation remains deterministic.

## M0 CLI

```sh
python -m pip install -e .
retroasset targets
retroasset validate examples/amiga-ocs-sprite.json
```

Expected validation result:

```text
PASS
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design.

## License

Software is licensed under the MIT License.
