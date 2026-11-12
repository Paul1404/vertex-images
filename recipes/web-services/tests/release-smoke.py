#!/usr/bin/env python3
"""Production-image checks on disposable, private Docker resources only."""
import base64
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITES = {
    'svu': ('sv-untereuerheim.de', 'X-SVU-Origin-Key'),
    'wengertsberg': ('wengertsberg.de', 'X-Wengertsberg-Origin-Key'),
    'sm-redaxo': ('schlossmuehle-untereuerheim.de', 'X-SM-Origin-Key'),
}
directory, image = sys.argv[1:]
site = next((name for name in SITES if directory in (
    f'railway-{name}-origin', f'railway-{name}-wordpress', 'railway-sm-redaxo' if name == 'sm-redaxo' else '',
)), None)
assert site, 'Unknown build directory'
prefix = 'web-services-release-' + uuid.uuid4().hex[:10]
containers, volumes = [], []
network = prefix + '-network'


def docker(*args, check=True, input=None):
    result = subprocess.run(['docker', *args], capture_output=True, text=True, input=input)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def container(role, *args, selected_image=image, command=(), entrypoint=None):
    name = prefix + '-' + role
    containers.append(name)
    options = ['run', '-d', '--name', name, '--network', network]
    if entrypoint:
        options += ['--entrypoint', entrypoint]
    docker(*options, *args, selected_image, *command)
    return name


def request(base, path='/', headers=None, data=None):
    assert urllib.parse.urlsplit(base).hostname in [prefix + '-cms', prefix + '-origin']
    payload = json.dumps({'url': base + path, 'headers': headers or {},
                          'data': data.decode() if data is not None else None})
    result = docker('exec', '-i', client, 'python3', '/http-client.py', input=payload)
    response = json.loads(result.stdout)
    return response['status'], response['headers'], base64.b64decode(response['body'])


def wait_for(base, path, status=200, attempts=60):
    last = None
    for _ in range(attempts):
        try:
            last = request(base, path)
            if last[0] == status:
                return last
        except (OSError, RuntimeError):
            pass
        time.sleep(1)
    raise AssertionError(f'{path} did not reach {status}; last status: {last[0] if last else "unreachable"}')


def origin_checks():
    fixture = ROOT / 'tests/fixtures/upstream.mjs'
    upstream = container('upstream', '-v', f'{fixture}:/fixture.mjs:ro',
                         selected_image='node:24-alpine', command=('node', '/fixture.mjs'))
    container('origin', '-e', 'ORIGIN_VERIFY=release-fixture-key',
              '-e', f'WORDPRESS_UPSTREAM=http://{upstream}:9000',
              '-e', f'REDAXO_UPSTREAM=http://{upstream}:9000')
    base = f'http://{prefix}-origin:8080'
    assert wait_for(base, '/healthz')[2] == b'ok'
    host, header = SITES[site]
    for path in ['/', '/wp-admin/', '/redaxo/', '/railway-health.php', '/healthz/']:
        assert request(base, path)[0] == 403, path
        assert request(base, path, {header: 'wrong'})[0] == 403, path
    status, _, body = request(base, '/fixture?check=1', {header: 'release-fixture-key'})
    assert status == 200
    assert json.loads(body) == {'path': '/fixture?check=1', 'host': host, 'protocol': 'https'}
    docker('stop', upstream)
    assert request(base, '/healthz')[0] >= 500, 'Origin health ignored a failed upstream'
    docker('start', upstream)
    assert wait_for(base, '/healthz')[2] == b'ok'
    missing = docker('run', '--rm', '--network', network, '-e', 'WORDPRESS_UPSTREAM=http://unused',
                     '-e', 'REDAXO_UPSTREAM=http://unused', image, 'true', check=False)
    assert missing.returncode != 0, 'Origin started without its verification key'
    print(f'{directory}: health, authorized proxy headers, denial, upstream failure and recovery passed')


def cms_checks():
    base = f'http://{prefix}-cms'
    volume = prefix + '-site'
    database_volume = prefix + '-database'
    volumes.extend([volume, database_volume])
    docker('volume', 'create', volume)
    docker('volume', 'create', database_volume)
    database = container('db', '--network-alias', 'release-db',
                         '-e', 'MARIADB_ROOT_PASSWORD=release-root-password',
                         '-e', 'MARIADB_DATABASE=release', '-e', 'MARIADB_USER=release',
                         '-e', 'MARIADB_PASSWORD=release-fixture-password',
                         '-v', f'{database_volume}:/var/lib/mysql', selected_image='mariadb:12.3')
    for _ in range(60):
        if docker('exec', database, 'healthcheck.sh', '--connect', '--innodb_initialized', check=False).returncode == 0:
            break
        time.sleep(1)
    else:
        raise AssertionError('Disposable database did not become ready')
    mount = ['-v', f'{volume}:/var/www/html']
    if site == 'sm-redaxo':
        empty = docker('run', '--rm', '--network', network, image, 'true', check=False)
        assert empty.returncode != 0 and 'refusing a fresh install' in empty.stderr
        environment = ['-e', 'REDAXO_DB_HOST=release-db', '-e', 'REDAXO_DB_NAME=release',
                       '-e', 'REDAXO_DB_LOGIN=release', '-e', 'REDAXO_DB_PASSWORD=release-fixture-password',
                       '-e', f'REDAXO_SERVER={base}', '-e', 'REDAXO_SERVERNAME=Release fixture',
                       '-e', 'REDAXO_ERROR_EMAIL=release@example.invalid', '-e', 'REDAXO_LANG=en_gb',
                       '-e', 'REDAXO_TIMEZONE=Europe/Berlin', '-e', 'REDAXO_DB_CHARSET=utf8mb4',
                       '-e', 'REDAXO_ADMIN_USER=release-admin', '-e', 'REDAXO_ADMIN_PASSWORD=release-fixture-password']
        # Test-only upstream setup on a newly created volume and an internal network.
        docker('run', '--rm', '--network', network, *mount, *environment,
               '--entrypoint', 'docker-entrypoint.sh', image, 'true')
        cms = container('cms', *mount, *environment, '-v', f'{ROOT / "tests/fixtures/redaxo-analytics.php"}:/var/www/html/analytics-fixture.php:ro')
        assert wait_for(base, '/healthz')[2] == b'ok'
        assert request(base, '/redaxo/index.php')[0] == 200, 'REDAXO backend did not boot'
    else:
        fixture = ROOT / 'tests/fixtures/wordpress.php'
        cms = container('cms', *mount,
                        '-v', f'{fixture}:/release-fixture.php:ro',
                        '-v', f'{ROOT / "railway-wengertsberg-wordpress/site-content.html"}:/wengertsberg-layout-fixture.html:ro',
                        '-e', 'WORDPRESS_DB_HOST=release-db', '-e', 'WORDPRESS_DB_NAME=release',
                        '-e', 'WORDPRESS_DB_USER=release', '-e', 'WORDPRESS_DB_PASSWORD=release-fixture-password',
                        '-e', 'WEB_SERVICES_RELEASE_TEST=1', '-e', f'RELEASE_URL={base}',
                        '-e', f'RELEASE_THEME={site}')
        wait_for(base, '/wp-admin/install.php')
        assert request(base, '/healthz')[0] == 503, 'An uninstalled WordPress reported ready'
        docker('exec', cms, 'php', '/release-fixture.php')
        assert wait_for(base, '/healthz')[2] == b'ok'
        assert b'Release fixture content' in request(base)[2]
        request(base, '/wp-login.php')
        login = urllib.parse.urlencode({'log': 'release-admin', 'pwd': 'release-fixture-password',
                                       'redirect_to': base + '/wp-admin/', 'testcookie': '1'}).encode()
        status, _, body = request(base, '/wp-login.php', data=login)
        assert status == 200 and b'wpbody-content' in body, 'WordPress editor login failed'
        if site == 'wengertsberg':
            status, _, body = request(base)
            for filename in ['style.css', 'site.js', 'share-preview.png', 'design-preview.css', 'design-preview.js']:
                digest = docker('exec', cms, 'php', '-r',
                                f'echo substr(hash_file("sha256", "/var/www/html/wp-content/themes/wengertsberg/{filename}"),0,12);').stdout
                stem, extension = filename.rsplit('.', 1)
                asset = f'/wp-content/themes/wengertsberg/assets/{stem}.{digest}.{extension}'
                assert request(base, asset)[0] == 200, asset
            assert b'preview-hero-grid' in body and b'direction-b' in body, 'Approved homepage layout missing'
            assert b'<h1><span>Vom Shopfloor</span> <span>bis in die</span> <span>Vorstandsetage.</span></h1>' in body
            assert b'noindex' not in body, 'Public homepage must remain indexable'
            for review_only in [b'preview-reviewbar', b'<dialog', b'<iframe', b'Firmenlogo', b'design-preview.js']:
                assert review_only not in body, 'Review-only markup or script escaped onto the public homepage'
            assert not re.search(rb'<script[^>]+design-preview', body), 'Review script loaded on public homepage'
            assert b'data-analytics-open hidden' in body, 'Footer settings must stay hidden until consent integration is available'
            assert b'/#kontakt' in body, 'Public CTA must point at the live contact section'
            snapshot = 'require "/var/www/html/wp-load.php"; echo hash("sha256", get_post((int)get_option("page_on_front"))->post_content);'
            before = docker('exec', cms, 'php', '-r', snapshot).stdout
            preview_status, _, preview = request(base, '/?entwurf=2')
            assert preview_status == 200 and b'preview-hero-grid' in preview, 'Review route did not render its layout'
            assert b'data-review-view="original"' in preview and b'id="preview-design-panel"' in preview
            assert b'<h1><span>Vom Shopfloor</span> <span>bis in die</span> <span>Vorstandsetage.</span></h1>' in preview
            assert b'Menschlich. Wirksam. Mit Freude.' in preview and b'preview-section-number' in preview
            assert b'preview-hero-subline' in body, 'Approved headline treatment missing on the public homepage'
            assert not re.search(rb'<iframe[^>]+\ssrc=', preview), 'Comparison loaded before being selected'
            comparison_status, _, comparison = request(base, '/?vergleich=1')
            assert comparison_status == 200 and b'noindex' in comparison
            assert b'preview-hero-grid' not in comparison and b'design-preview.' not in comparison
            assert b'noindex' in preview and b'design-preview.' in preview
            assert b'preview-choice-example' in preview and b'disabled' in preview
            assert not re.search(rb'contact-details[^>]*>\s*<p>\s*</p>', preview), 'Shortcode wrapper created an empty layout row'
            assert docker('exec', cms, 'php', '-r', snapshot).stdout == before, 'Review rendering changed editor content'
            for query in ['/?entwurf=other', '/?entwurf%5B%5D=2']:
                ordinary = request(base, query)[2]
                assert b'preview-hero-grid' in ordinary and b'preview-reviewbar' not in ordinary
    # The consent loader is served locally; backend/authenticated HTML must not
    # receive a tracker. Use a synthetic public PHP page for the REDAXO filter.
    assert request(base, '/site-analytics/consent.js')[0] == 200
    if site == 'sm-redaxo':
        html = request(base, '/analytics-fixture.php')[2]
        assert b'/site-analytics/consent.js' in html, 'Native REDAXO output filter missing'
        assert b'https://umami.pdcd.net/script.js' not in html, 'Legacy tracker escaped final output filter'
        assert b'/site-analytics/consent.js' not in request(base, '/redaxo/index.php')[2]
    else:
        # The client is now logged in, so instrumentation must be absent.
        assert b'/site-analytics/consent.js' not in request(base)[2]
    modules = docker('exec', cms, 'apache2ctl', '-M').stdout
    assert 'mpm_prefork_module' in modules and 'mpm_event_module' not in modules
    docker('exec', cms, 'sh', '-c', 'mkdir -p /var/www/html/release-sentinel; echo fixture > /var/www/html/release-sentinel/preserved.txt')
    docker('restart', cms)
    assert wait_for(base, '/healthz')[2] == b'ok'
    assert request(base, '/release-sentinel/preserved.txt')[2].strip() == b'fixture'
    if site != 'sm-redaxo':
        assert b'Release fixture content' in request(base)[2], 'Restart lost editor content'
    docker('stop', database)
    status, _, body = request(base, '/healthz')
    assert status == 503 and body == b'unavailable', 'Health did not safely reject an unavailable database'
    docker('start', database)
    assert wait_for(base, '/healthz')[2] == b'ok'
    print(f'{directory}: CMS/database readiness, prefork, persistent files, database failure and recovery passed')


try:
    docker('network', 'create', '--internal', network)
    client = container('client', '-v', f'{ROOT / "tests/fixtures/http-client.py"}:/http-client.py:ro',
                       selected_image='python:3.13-alpine',
                       command=('python3', '-c', 'import time; time.sleep(3600)'))
    if directory.endswith('-origin'):
        origin_checks()
    else:
        cms_checks()
except Exception:
    for name in containers:
        logs = docker('logs', '--tail', '30', name, check=False)
        print(logs.stdout + logs.stderr, file=sys.stderr)
    raise
finally:
    for name in reversed(containers):
        docker('rm', '-f', '-v', name, check=False)
    for name in volumes:
        docker('volume', 'rm', name, check=False)
    docker('network', 'rm', network, check=False)
