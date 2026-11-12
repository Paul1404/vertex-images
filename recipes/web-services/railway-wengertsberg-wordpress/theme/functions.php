<?php
defined('ABSPATH') || exit;
require_once __DIR__ . '/contact.php';
require_once __DIR__ . '/seo.php';
require_once __DIR__ . '/design-preview.php';

add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('responsive-embeds');
    add_theme_support('editor-styles');
    add_editor_style(wengertsberg_asset('style.css'));
    add_theme_support('html5', ['search-form', 'gallery', 'caption', 'style', 'script']);
});

function wengertsberg_asset(string $file): string {
    $digest = substr(hash_file('sha256', get_template_directory() . '/' . $file), 0, 12);
    $parts = pathinfo($file);
    return 'assets/' . $parts['filename'] . '.' . $digest . '.' . $parts['extension'];
}

add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('wengertsberg', get_template_directory_uri() . '/' . wengertsberg_asset('style.css'), [], null);
    wp_enqueue_script('wengertsberg', get_template_directory_uri() . '/' . wengertsberg_asset('site.js'), [], null, true);
});

// This site uses local system fonts and local photography only.
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');
add_filter('wp_resource_hints', function ($urls, $relation) {
    return $relation === 'dns-prefetch' ? array_filter($urls, fn($url) => !str_contains(is_array($url) ? $url['href'] : $url, 's.w.org')) : $urls;
}, 10, 2);

function wengertsberg_brand(): void {
    echo '<a class="brand" href="' . esc_url(home_url('/')) . '" aria-label="Wengertsberg, zur Startseite"><span class="brand-letter" aria-hidden="true">W</span><span class="brand-name">WENGERTSBERG<span class="brand-subtitle">TRAINING &amp; CONSULTING</span></span></a>';
}

add_action('customize_register', function ($customizer) {
    $customizer->add_section('wengertsberg_contact', ['title' => 'Wengertsberg Kontakt']);
    $customizer->add_setting('wengertsberg_email', ['default' => '', 'sanitize_callback' => 'sanitize_email']);
    $customizer->add_control('wengertsberg_email', ['label' => 'Geschäftliche E-Mail-Adresse', 'section' => 'wengertsberg_contact', 'type' => 'email']);
    $customizer->add_setting('wengertsberg_phone', ['default' => '', 'sanitize_callback' => 'sanitize_text_field']);
    $customizer->add_control('wengertsberg_phone', ['label' => 'Geschäftliche Telefonnummer', 'section' => 'wengertsberg_contact', 'type' => 'text']);
});

function wengertsberg_contact_icon(string $name): string {
    $shapes = [
        'email' => '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3 6 9 7 9-7"/>',
        'phone' => '<path d="M5 3h4l2 5-3 2a16 16 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2A18 18 0 0 1 3 5a2 2 0 0 1 2-2Z"/>',
        'location' => '<path d="M20 10c0 6-8 11-8 11S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
    ];
    if (!isset($shapes[$name])) {
        return '';
    }
    return '<svg class="contact-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' . $shapes[$name] . '</svg>';
}

add_shortcode('wengertsberg_contact', function () {
    $email = sanitize_email(get_theme_mod('wengertsberg_email', ''));
    $phone = sanitize_text_field(get_theme_mod('wengertsberg_phone', ''));
    $html = '';
    if ($email) {
        $html .= '<a class="contact-link contact-address" href="' . esc_url('mailto:' . $email) . '">' . wengertsberg_contact_icon('email') . '<span class="contact-text">' . esc_html($email) . '</span></a>';
    }
    if ($phone) {
        $dial = preg_replace('/[^+0-9]/', '', $phone);
        if (str_starts_with($dial, '0')) {
            $dial = '+49' . substr($dial, 1);
        }
        $html .= '<p class="contact-phone"><a class="contact-link" href="' . esc_url('tel:' . $dial) . '">' . wengertsberg_contact_icon('phone') . '<span class="contact-text">' . esc_html($phone) . '</span></a></p>';
    }
    $html .= '<p class="contact-place">' . wengertsberg_contact_icon('location') . '<span>Region Schweinfurt in Bayern</span></p>';
    $form = wengertsberg_contact_form();
    return '<div class="contact-methods' . ($form ? ' with-form' : '') . '">' . $html . '</div>' . $form;
});
