#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#ifdef RETROASSET_EMBEDDED_FIXTURES
#include "generated_fixtures.h"
#endif

static uint16_t be16(const unsigned char *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

static uint32_t be32(const unsigned char *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | p[3];
}

static int decode_row(const unsigned char *src, size_t size, size_t *pos,
                      unsigned char *dst, size_t expected) {
    size_t out = 0;
    while (out < expected) {
        int8_t n;
        size_t count;
        if (*pos >= size) return 0;
        n = (int8_t)src[(*pos)++];
        if (n >= 0) {
            count = (size_t)n + 1;
            if (*pos + count > size || out + count > expected) return 0;
            memcpy(dst + out, src + *pos, count);
            *pos += count;
            out += count;
        } else if (n != -128) {
            count = (size_t)(1 - n);
            if (*pos >= size || out + count > expected) return 0;
            memset(dst + out, src[(*pos)++], count);
            out += count;
        }
    }
    return 1;
}

static int verify_buffer(const unsigned char *data, size_t file_size) {
    const unsigned char *bmhd = NULL, *cmap = NULL, *body = NULL;
    size_t bmhd_size = 0, cmap_size = 0;
    size_t pos = 12, body_size = 0, stream_pos = 0;
    uint16_t width, height;
    unsigned planes, compression;
    size_t stride, rows, i;
    unsigned char *row;
    static const unsigned char expected_cmap[] = {0, 0, 0, 255, 255, 255};
    static const unsigned char expected_planar[] = {0x55, 0x55, 0xaa, 0xaa};
    size_t planar_pos = 0;

    if (file_size < 12) return 0;

    if (memcmp(data, "FORM", 4) || memcmp(data + 8, "ILBM", 4)) {
        return 0;
    }
    if ((size_t)be32(data + 4) + 8 != file_size) return 0;
    while (pos + 8 <= (size_t)file_size) {
        uint32_t size = be32(data + pos + 4);
        const unsigned char *payload = data + pos + 8;
        if (pos + 8 + size > (size_t)file_size) { return 0; }
        if (!memcmp(data + pos, "BMHD", 4)) { bmhd = payload; bmhd_size = size; }
        if (!memcmp(data + pos, "CMAP", 4)) { cmap = payload; cmap_size = size; }
        if (!memcmp(data + pos, "BODY", 4)) { body = payload; body_size = size; }
        pos += 8 + size + (size & 1);
    }
    if (!bmhd || !cmap || !body || bmhd_size < 20) { return 0; }
    if (cmap_size != sizeof(expected_cmap) ||
        memcmp(cmap, expected_cmap, sizeof(expected_cmap))) return 0;

    width = be16(bmhd);
    height = be16(bmhd + 2);
    planes = bmhd[8];
    compression = bmhd[10];
    if (width != 16 || height != 2 || planes != 1 || compression > 1) { return 0; }

    stride = ((width + 15) / 16) * 2;
    rows = (size_t)height * planes;
    row = (unsigned char *)malloc(stride);
    if (!row) { return 0; }

    if (stride * rows != sizeof(expected_planar)) { free(row); return 0; }
    if (compression == 0) {
        if (body_size != sizeof(expected_planar) ||
            memcmp(body, expected_planar, sizeof(expected_planar))) {
            free(row); return 0;
        }
    } else {
        for (i = 0; i < rows; ++i) {
            if (!decode_row(body, body_size, &stream_pos, row, stride)) {
                free(row); return 0;
            }
            if (memcmp(row, expected_planar + planar_pos, stride)) {
                free(row); return 0;
            }
            planar_pos += stride;
        }
        if (stream_pos != body_size) { free(row); return 0; }
    }

    printf("RETROASSET_ILBM_%s_PASS %ux%u %u-plane\n",
           compression ? "BYTERUN1" : "UNCOMPRESSED",
           (unsigned)width, (unsigned)height, planes);
    free(row);
    return 1;
}

static int verify(const char *path) {
    FILE *f;
    unsigned char *data;
    long size;
    int ok;
    f = fopen(path, "rb");
    if (!f) return 0;
    fseek(f, 0, SEEK_END); size = ftell(f); rewind(f);
    if (size < 0) { fclose(f); return 0; }
    data = (unsigned char *)malloc((size_t)size);
    if (!data) { fclose(f); return 0; }
    if (fread(data, 1, (size_t)size, f) != (size_t)size) { free(data); fclose(f); return 0; }
    fclose(f);
    ok = verify_buffer(data, (size_t)size);
    free(data);
    return ok;
}

int main(int argc, char **argv) {
    int i;
#ifdef RETROASSET_EMBEDDED_FIXTURES
    if (argc == 1) {
        if (!verify_buffer(fixture_uncompressed, fixture_uncompressed_len)) return 1;
        if (!verify_buffer(fixture_byterun1, fixture_byterun1_len)) return 1;
        return 0;
    }
#endif
    if (argc < 2) {
        fprintf(stderr, "usage: ilbm-verify file.ilbm [...]\n");
        return 2;
    }
    for (i = 1; i < argc; ++i) {
        if (!verify(argv[i])) {
            fprintf(stderr, "RETROASSET_ILBM_FAIL %s\n", argv[i]);
            return 1;
        }
    }
    return 0;
}
