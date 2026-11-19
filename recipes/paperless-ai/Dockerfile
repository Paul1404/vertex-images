FROM python:3.15-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.13/site-packages/pip \
       /usr/local/lib/python3.13/site-packages/pip-*.dist-info \
       /usr/local/lib/python3.13/ensurepip \
    && rm -f /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.13

RUN python3 - <<'PY'
import hashlib, pathlib, tarfile, urllib.request
url = 'https://registry.npmjs.org/@openai/codex/-/codex-0.167.0-linux-x64.tgz'
archive = pathlib.Path('/tmp/codex.tgz')
urllib.request.urlretrieve(url, archive)
if hashlib.sha256(archive.read_bytes()).hexdigest() != '2dc9aa871abb513c3539d20d025f701faf1974c46ee906bda3a1e1f5026d4434':
    raise RuntimeError('Codex package checksum mismatch')
with tarfile.open(archive, 'r:gz') as tar:
    for part in ('bin/codex', 'codex-resources/bwrap'):
        source = 'package/vendor/x86_64-unknown-linux-musl/' + part
        target = pathlib.Path('/opt/codex') / part
        target.parent.mkdir(parents=True, exist_ok=True)
        with tar.extractfile(source) as reader, target.open('wb') as writer:
            while chunk := reader.read(1024 * 1024): writer.write(chunk)
        target.chmod(0o755)
archive.unlink()
PY

WORKDIR /app
COPY adapter/adapter.py adapter/invoice_metadata.py /app/
ENV HOME=/data CODEX_HOME=/data/codex PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 1000:1000
EXPOSE 18766
CMD ["python3", "/app/adapter.py"]
