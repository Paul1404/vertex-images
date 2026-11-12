<?php
/** Versioned public-site consent gate; existing CMS content is preserved. */
add_action('template_redirect', function () {
    if (is_admin() || wp_doing_ajax() || wp_doing_cron() || (defined('REST_REQUEST') && REST_REQUEST)) return;
    $logged_in = is_user_logged_in();
    ob_start(function ($html) use ($logged_in) {
        if (stripos($html, '</body>') === false) return $html;
        // Retire legacy tracking injected by the persisted theme or old plugin.
        $html = preg_replace('~<script\b[^>]*src=["\']https://umami\.pdcd\.net/(?:script|recorder)\.js[^"\']*["\'][^>]*>.*?</script>~is', '', $html);
        if (!$logged_in) {
            $tag = '<script defer src="/site-analytics/consent.js" data-website-id="f88b711a-caa5-46f2-bc1c-44551d49042e" data-hosts="wengertsberg.de,www.wengertsberg.de" data-privacy="/datenschutzerklaerung/"></script>';
            $html = str_ireplace('</body>', $tag . '</body>', $html);
        }
        return $html;
    });
}, 0);
