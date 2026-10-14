FROM postgres:17-alpine
# Extend the same major-version/libc base; preserve the existing application volume.
RUN apk add --no-cache --virtual .vector-build build-base wget \
    && wget -q https://codeload.github.com/pgvector/pgvector/tar.gz/refs/tags/v0.8.7 -O /tmp/vector.tgz \
    && echo "cac0b10c360f05b2d521200105ba3697e773d4cd3731f5a915a7e37ebe0bea85  /tmp/vector.tgz" | sha256sum -c - \
    && tar -xzf /tmp/vector.tgz -C /tmp \
    && make -C /tmp/pgvector-0.8.7 OPTFLAGS="" with_llvm=no \
    && make -C /tmp/pgvector-0.8.7 install with_llvm=no \
    && rm -rf /tmp/pgvector-0.8.7 /tmp/vector.tgz \
    && apk del .vector-build
