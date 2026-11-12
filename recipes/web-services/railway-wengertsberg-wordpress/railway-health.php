<?php
// A read-only core/database probe. Do not load plugins, themes or WP cron.
ini_set('display_errors', '0');
$ready = false;
ob_start();
register_shutdown_function(static function () use (&$ready): void {
    while (ob_get_level() > 0) {
        ob_end_clean();
    }
    http_response_code($ready ? 200 : 503);
    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: no-store');
    echo $ready ? 'ok' : 'unavailable';
});

try {
    define('SHORTINIT', true);
    define('DISABLE_WP_CRON', true);
    define('WP_DEBUG_DISPLAY', false);
    require __DIR__ . '/wp-load.php';
    global $wpdb;
    $wpdb->suppress_errors(true);
    $site = $wpdb->get_var("SELECT option_value FROM {$wpdb->options} WHERE option_name = 'siteurl' LIMIT 1");
    $ready = is_string($site) && $site !== '';
} catch (Throwable $error) {
    // Health responses must never contain configuration or database details.
}
