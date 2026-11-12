<?php
defined('ABSPATH') || exit;

add_action('wp_head', function () {
    if (!is_front_page()) {
        return;
    }
    $description = 'Coaching, Training und Beratung mit Alexander Eckert. Für Führungskräfte, Teams und Organisationen in der Region Schweinfurt.';
    $share_title = 'Training & Consulting aus Schweinfurt | Wengertsberg';
    $share_description = 'Für Führungskräfte, Teams und Organisationen: vom Einzelcoaching bis zum Leitungsteam, vom Shopfloor bis in die Vorstandsetage.';
    $image = get_template_directory_uri() . '/' . wengertsberg_asset('share-preview.png');
    echo '<meta name="description" content="' . esc_attr($description) . '">' . "\n";
    $properties = [
        'og:type' => 'website',
        'og:locale' => 'de_DE',
        'og:site_name' => 'Wengertsberg Training & Consulting',
        'og:title' => $share_title,
        'og:description' => $share_description,
        'og:url' => home_url('/'),
        'og:image' => esc_url_raw($image),
        'og:image:type' => 'image/png',
        'og:image:width' => '1200',
        'og:image:height' => '630',
        'og:image:alt' => 'Wengertsberg Training & Consulting, Alexander Eckert',
    ];
    foreach ($properties as $property => $content) {
        echo '<meta property="' . esc_attr($property) . '" content="' . esc_attr($content) . '">' . "\n";
    }

    $home = home_url('/');
    $organization = [
        '@type' => 'Organization',
        '@id' => $home . '#organization',
        'name' => 'Wengertsberg Training & Consulting',
        'alternateName' => 'Wengertsberg',
        'url' => $home,
        'description' => $description,
        'areaServed' => ['@type' => 'Place', 'name' => 'Region Schweinfurt, Bayern'],
    ];
    $logo = get_site_icon_url(192);
    if ($logo) {
        $organization['logo'] = esc_url_raw($logo);
    }
    $email = sanitize_email(get_theme_mod('wengertsberg_email', ''));
    if (is_email($email)) {
        $organization['email'] = $email;
    }
    $phone = preg_replace('/[^+0-9]/', '', get_theme_mod('wengertsberg_phone', ''));
    if ($phone) {
        $organization['telephone'] = str_starts_with($phone, '0') ? '+49' . substr($phone, 1) : $phone;
    }
    // Describe only published facts. Do not invent ratings, opening hours,
    // qualifications, social profiles or a customer-facing business address.
    $graph = [
        '@context' => 'https://schema.org',
        '@graph' => [
            $organization,
            [
                '@type' => 'Person',
                '@id' => $home . '#alexander-eckert',
                'name' => 'Alexander Eckert',
                'url' => $home,
                'jobTitle' => 'Coach, Trainer und Organisationsentwickler',
                'worksFor' => ['@id' => $home . '#organization'],
            ],
            [
                '@type' => 'WebSite',
                '@id' => $home . '#website',
                'name' => 'Wengertsberg Training & Consulting',
                'alternateName' => 'Wengertsberg',
                'url' => $home,
                'inLanguage' => 'de-DE',
                'publisher' => ['@id' => $home . '#organization'],
            ],
            [
                '@type' => 'WebPage',
                '@id' => $home . '#webpage',
                'url' => $home,
                'name' => wp_get_document_title(),
                'description' => $description,
                'inLanguage' => 'de-DE',
                'isPartOf' => ['@id' => $home . '#website'],
                'about' => [
                    ['@id' => $home . '#organization'],
                    ['@id' => $home . '#alexander-eckert'],
                ],
            ],
        ],
    ];
    echo '<script type="application/ld+json">' . wp_json_encode($graph, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT) . '</script>' . "\n";
});

add_filter('document_title_separator', fn() => '|');
add_filter('pre_get_document_title', function ($title) {
    return is_front_page() ? 'Training & Consulting | Wengertsberg' : $title;
});

// Reserve the real image space even when an optimized file extension differs
// from the original media URL. Let core handle loading and priority hints.
add_filter('render_block_core/image', function ($html, $block) {
    $id = (int) ($block['attrs']['id'] ?? 0);
    if (!$id || !is_front_page()) {
        return $html;
    }
    $metadata = wp_get_attachment_metadata($id);
    if (empty($metadata['width']) || empty($metadata['height'])) {
        return $html;
    }
    $tags = new WP_HTML_Tag_Processor($html);
    if ($tags->next_tag('IMG') && !$tags->get_attribute('width') && !$tags->get_attribute('height')) {
        $tags->set_attribute('width', (int) $metadata['width']);
        $tags->set_attribute('height', (int) $metadata['height']);
    }
    return $tags->get_updated_html();
}, 10, 2);
