FROM docker.io/rockylinux/rockylinux@sha256:827d37bc128288ccf160ee318bb3cb92d591164cb217e92f8bc61e3982ae1834 AS build
RUN dnf -y install ca-certificates clang clang-devel cmake curl gcc gcc-c++ git make openssl-devel perl pkgconf-pkg-config python3 xz && dnf clean all
RUN curl -fsSL --retry 3 -o /tmp/rust.tar.xz https://static.rust-lang.org/dist/rust-1.99.1-x86_64-unknown-linux-gnu.tar.xz \
    && echo '231fcae47ee950621374725b5fc3b5441d2fbda2955ac45dd7dc816d8876cfe7  /tmp/rust.tar.xz' | sha256sum -c - \
    && mkdir /tmp/rust && tar -xJf /tmp/rust.tar.xz --strip-components=1 -C /tmp/rust \
    && /tmp/rust/install.sh --prefix=/opt/rust --without=rust-docs \
    && rm -rf /tmp/rust /tmp/rust.tar.xz
RUN git config --global url.https://github.com/open-telemetry/opentelemetry-rust.insteadOf https://github.com/stalwartlabs/opentelemetry-rust
ENV PATH=/opt/rust/bin:$PATH CARGO_NET_GIT_FETCH_WITH_CLI=true CARGO_BUILD_JOBS=4 CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 CARGO_PROFILE_RELEASE_LTO=false CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
WORKDIR /build/stalwart
COPY source/ ./
RUN cargo build --locked -p stalwart --no-default-features --features sqlite,enterprise \
    && STORE=Sqlite STALWART_LEGACY_PASSWORD_IMPORT=1 cargo test --locked -p tests --no-default-features --features sqlite --test legacy_password -- --test-threads=1 \
    && STORE=Sqlite cargo test --locked -p tests --no-default-features --features sqlite --test legacy_password -- --test-threads=1 \
    && python3 -m unittest discover -s tools -p test_legacy_password_import.py -v \
    && cargo build --locked --release -p stalwart

FROM docker.io/rockylinux/rockylinux@sha256:827d37bc128288ccf160ee318bb3cb92d591164cb217e92f8bc61e3982ae1834
RUN dnf -y upgrade && dnf -y install libstdc++ libgcc ca-certificates libcap && dnf clean all
COPY --from=build /build/stalwart/target/release/stalwart /usr/local/bin/stalwart
RUN ldd /usr/local/bin/stalwart && chmod 0755 /usr/local/bin/stalwart \
    && setcap cap_net_bind_service=+ep /usr/local/bin/stalwart \
    && getcap /usr/local/bin/stalwart
USER 993:993
ENTRYPOINT ["/usr/local/bin/stalwart"]
CMD ["--config=/etc/stalwart/config.json"]
