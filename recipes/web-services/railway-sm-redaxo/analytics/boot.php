<?php
// Use REDAXO's final output hook: its frontend consumes PHP output buffers.
if (rex::isBackend() || PHP_SAPI === 'cli') return;
rex_extension::register('OUTPUT_FILTER', function (rex_extension_point $ep) {
    $html = $ep->getSubject();
    if (stripos($html, '</body>') === false) return $html;
    $html = preg_replace('~<script\b[^>]*src=["\']https://umami\.pdcd\.net/(?:script|recorder)\.js[^"\']*["\'][^>]*>.*?</script>~is', '', $html);
    if (strpos($html, '/site-analytics/consent.js') !== false) return $html;
    return str_ireplace('</body>', '<script defer src="/site-analytics/consent.js" data-website-id="2e537260-7c47-486c-8af2-3b6e77657582" data-hosts="schlossmuehle-untereuerheim.de,www.schlossmuehle-untereuerheim.de" data-article-ids="true" data-privacy="/index.php?article_id=8"></script></body>', $html);
}, rex_extension::LATE);
