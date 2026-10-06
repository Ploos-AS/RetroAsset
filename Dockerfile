FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/Ploos-AS/RetroAsset"
LABEL org.opencontainers.image.description="RetroAsset native retro-asset compiler and validator"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . \
    && addgroup -S retroasset \
    && adduser -S -G retroasset retroasset

WORKDIR /work
USER retroasset
ENTRYPOINT ["retroasset"]
CMD ["--help"]
