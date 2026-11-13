FROM python:3.13-slim@sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20

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
