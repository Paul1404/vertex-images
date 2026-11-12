<?php
// Check migrated files and the configured database without booting site code.
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
    $config = __DIR__ . '/redaxo/data/core/config.yml';
    if (!is_file(__DIR__ . '/index.php') || !is_file($config) || filesize($config) === 0) {
        exit;
    }
    $host = parse_url('mysql://' . getenv('REDAXO_DB_HOST'));
    if (!$host || !isset($host['host'])) {
        exit;
    }
    // REDAXO's image provides PDO MySQL, not WordPress's mysqli extension.
    $connection = new PDO(
        'mysql:host=' . trim($host['host'], '[]') . ';port=' . ($host['port'] ?? 3306)
            . ';dbname=' . getenv('REDAXO_DB_NAME') . ';charset=utf8mb4',
        getenv('REDAXO_DB_LOGIN'),
        getenv('REDAXO_DB_PASSWORD'),
        [PDO::ATTR_TIMEOUT => 3, PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
    );
    // Respect custom REDAXO prefixes without exposing any table or row data.
    $tables = $connection->query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND (table_name LIKE '%article' OR table_name LIKE '%user')")->fetchColumn();
    $ready = (int) $tables >= 2;
} catch (Throwable $error) {
    // Health responses must never contain configuration or database details.
}
