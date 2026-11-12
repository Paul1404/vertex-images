<?php
if (getenv('WEB_SERVICES_RELEASE_TEST') !== '1' || getenv('WORDPRESS_DB_NAME') !== 'release') {
    exit('This fixture requires an isolated release database.');
}
define('WP_INSTALLING', true);
define('DISABLE_WP_CRON', true);
require '/var/www/html/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/upgrade.php';
add_filter('pre_wp_mail', '__return_true');
wp_install('Release fixture', 'release-admin', 'release@example.invalid', false, '', 'release-fixture-password');
update_option('siteurl', getenv('RELEASE_URL'));
update_option('home', getenv('RELEASE_URL'));
if (getenv('RELEASE_THEME') === 'wengertsberg') {
    switch_theme('wengertsberg');
    update_option('blog_public', 1); // Exercise production indexability in this isolated fixture.
}
$content = '<!-- wp:paragraph --><p>Release fixture content</p><!-- /wp:paragraph -->';
if (getenv('RELEASE_THEME') === 'wengertsberg') {
    $content = file_get_contents('/wengertsberg-layout-fixture.html');
    $content = str_replace('Ich unterstütze Führungskräfte', 'Release fixture content. Ich unterstütze Führungskräfte', $content);
}
$page = wp_insert_post([
    'post_type' => 'page',
    'post_status' => 'publish',
    'post_title' => 'Release persistence fixture',
    'post_content' => $content,
]);
if (!$page || is_wp_error($page)) {
    exit(1);
}
update_option('show_on_front', 'page');
update_option('page_on_front', $page);
echo "Synthetic WordPress fixture installed.\n";
