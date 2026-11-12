<?php
defined('ABSPATH') || exit;

function wengertsberg_design_preview(): bool {
    return is_front_page() && isset($_GET['entwurf']) && is_string($_GET['entwurf']) && $_GET['entwurf'] === '2';
}

function wengertsberg_design_comparison(): bool {
    return is_front_page() && isset($_GET['vergleich']) && is_string($_GET['vergleich']) && $_GET['vergleich'] === '1';
}

function wengertsberg_direction_b(): bool {
    return is_front_page() && (!wengertsberg_design_comparison() || wengertsberg_design_preview());
}

add_filter('body_class', function ($classes) {
    if (wengertsberg_direction_b()) $classes[] = 'direction-b';
    if (wengertsberg_design_preview()) $classes[] = 'design-preview';
    return $classes;
});
add_filter('wp_robots', function ($robots) {
    if (wengertsberg_design_preview() || wengertsberg_design_comparison()) {
        unset($robots['index']);
        $robots['noindex'] = true;
    }
    return $robots;
});
add_action('wp_enqueue_scripts', function () {
    if (!wengertsberg_direction_b()) return;
    wp_enqueue_style('wengertsberg-design-preview', get_template_directory_uri() . '/' . wengertsberg_asset('design-preview.css'), ['wengertsberg'], null);
    if (wengertsberg_design_preview()) wp_enqueue_script('wengertsberg-design-preview', get_template_directory_uri() . '/' . wengertsberg_asset('design-preview.js'), ['wengertsberg'], null, true);
});

function wengertsberg_preview_find(array $blocks, string $class): ?array {
    foreach ($blocks as $block) {
        $classes = preg_split('/\s+/', $block['attrs']['className'] ?? '');
        if (in_array($class, $classes, true)) return $block;
        $found = wengertsberg_preview_find($block['innerBlocks'] ?? [], $class);
        if ($found) return $found;
    }
    return null;
}
function wengertsberg_preview_render(array $blocks): string {
    return implode("\n", array_map(fn($block) => do_shortcode(shortcode_unautop(render_block($block))), $blocks));
}
function wengertsberg_preview_heading(array $blocks): array {
    foreach ($blocks as $block) {
        if ($block['blockName'] === 'core/heading') return $block;
    }
    return [];
}

// Direction B uses the supplied desktop/mobile reference. Its headline and
// subline are shared by the public homepage and review; other copy/media
// still come from published blocks.
// Never import the seed, write CMS data or invent client claims for this view.
add_filter('the_content', function ($content) {
    if (!wengertsberg_direction_b() || !in_the_loop() || !is_main_query()) return $content;
    $post = get_post();
    if (!$post || $post->post_status !== 'publish') return $content;
    $blocks = parse_blocks($post->post_content);
    $groups = [];
    foreach (['hero-copy', 'hero-portrait', 'about-copy', 'about-place', 'services', 'service-list', 'approach-copy', 'approach-photo', 'reference-intro', 'reference-list', 'contact-copy', 'contact-details'] as $class) {
        $groups[$class] = wengertsberg_preview_find($blocks, $class);
        if (!$groups[$class]) return $content;
    }
    $hero = $groups['hero-copy']['innerBlocks'];
    $description = wengertsberg_preview_find($hero, 'hero-description');
    if (!$description) return $content;
    $description_html = wengertsberg_preview_render([$description]);
    // This phrase is the reference hero headline, so it no longer repeats here.
    $description_html = str_replace(', vom Shopfloor bis in die Vorstandsetage', '', $description_html);
    $about_heading = wengertsberg_preview_heading($groups['about-copy']['innerBlocks']);
    $about_body = array_values(array_filter($groups['about-copy']['innerBlocks'], fn($b) => $b !== $about_heading));
    $service_children = $groups['services']['innerBlocks'][0]['innerBlocks'] ?? [];
    $service_intro = array_values(array_filter($service_children, fn($b) => $b['blockName'] !== 'core/group'));
    $approach = $groups['approach-copy']['innerBlocks'];
    $approach_heading = wengertsberg_preview_heading($approach);
    $approach_paragraphs = array_values(array_filter($approach, fn($b) => $b['blockName'] === 'core/paragraph'));
    if (!$about_heading || count($service_intro) < 2 || count($approach_paragraphs) !== 2) return $content;
    $case_example = '';
    foreach ($groups['reference-list']['innerBlocks'] as $reference) {
        $rendered_reference = wengertsberg_preview_render([$reference]);
        if (str_contains(wp_strip_all_tags($rendered_reference), 'Workshop in Lissabon')) {
            $case_example = $rendered_reference;
            break;
        }
    }
    $reference_intro = $groups['reference-intro']['innerBlocks'];
    $reference_heading = wengertsberg_preview_heading($reference_intro);
    if (!$reference_heading) return $content;
    $reference_body = array_values(array_filter($reference_intro, fn($b) => $b !== $reference_heading));
    $contact_html = wengertsberg_preview_render([$groups['contact-copy']]);
    $contact_question = 'Sie haben eine Frage oder ein konkretes Anliegen?';
    // Promote the existing opening question without duplicating the paragraph.
    if (str_contains(wp_strip_all_tags($contact_html), $contact_question)) {
        $contact_html = str_replace($contact_question, '', $contact_html);
        $contact_html = preg_replace('/<h2\b[^>]*>.*?<\/h2>/s', '<p class="preview-contact-label">Kontakt</p><h2>' . esc_html($contact_question) . '</h2>', $contact_html, 1);
    }
    $review = wengertsberg_design_preview();
    ob_start(); ?>
    <?php if ($review): ?>
    <aside class="preview-reviewbar" aria-label="Entwurf und Ideen für Alex">
        <div class="wrap preview-reviewbar-inner">
            <div class="preview-review-intro"><strong>Für Alex: Richtung B</strong><p>Desktop- und Handyvorlage in WordPress umgesetzt.</p></div>
            <div class="preview-review-controls">
                <div class="preview-view-switch" role="group" aria-label="Websiteansicht">
                    <button type="button" data-review-view="design" aria-pressed="true" aria-controls="preview-design-panel">Richtung B</button>
                    <button type="button" data-review-view="original" aria-pressed="false" aria-controls="preview-original-panel">Bisherige Website</button>
                </div>
                <nav class="preview-review-ideas" aria-label="Ideen ansehen"><button type="button" data-preview-notes>Änderungen</button><button type="button" data-preview-cases>Kunden &amp; Logos</button><button type="button" data-preview-consent>Analysehinweis</button></nav>
            </div>
        </div>
    </aside>
    <section id="preview-original-panel" class="preview-original-panel" hidden aria-label="Bisherige Website zum Vergleich"><iframe title="Bisherige Wengertsberg Website" data-original-src="<?php echo esc_url(add_query_arg('vergleich', '1', home_url('/'))); ?>" referrerpolicy="no-referrer"></iframe></section>
    <?php endif; ?>
    <div id="preview-design-panel">
    <section class="preview-hero" aria-label="Alexander Eckert">
        <div class="wrap preview-hero-grid">
            <div class="preview-hero-title"><p class="preview-hero-name">Alexander Eckert</p><h1><span>Vom Shopfloor</span> <span>bis in die</span> <span>Vorstandsetage.</span></h1></div>
            <div class="preview-introduction"><p class="preview-hero-subline">Menschlich. Wirksam. Mit Freude.</p><a class="button" href="<?php echo esc_url(home_url('/#kontakt')); ?>">Ins Gespräch kommen</a></div>
            <div class="preview-portrait"><?php echo wengertsberg_preview_render([$groups['hero-portrait']]); ?></div>
        </div>
    </section>
    <section id="ueber-mich" class="preview-about section">
        <div class="wrap preview-about-grid">
            <div class="preview-section-heading"><span class="preview-section-number" aria-hidden="true">01</span><?php echo wengertsberg_preview_render([$about_heading]); ?></div>
            <div class="about-copy"><p class="preview-person">Alexander Eckert: Coaching, Training und Beratung</p><div class="preview-about-introduction"><?php echo $description_html; ?></div><?php echo wengertsberg_preview_render($about_body); ?></div>
        </div>
    </section>
    <section id="leistungen" class="preview-services section">
        <div class="wrap preview-services-grid"><div class="preview-section-heading"><span class="preview-section-number" aria-hidden="true">02</span><?php echo wengertsberg_preview_render([$service_intro[0]]); ?></div><div class="preview-services-intro"><?php echo wengertsberg_preview_render(array_slice($service_intro, 1)); ?></div><?php echo wengertsberg_preview_render([$groups['service-list']]); ?></div>
    </section>
    <section id="mein-ansatz" class="preview-approach section">
        <div class="wrap preview-approach-grid"><div class="preview-section-heading"><span class="preview-section-number" aria-hidden="true">03</span><?php echo wengertsberg_preview_render([$approach_heading]); ?></div><div class="preview-approach-lead"><?php echo wengertsberg_preview_render([$approach_paragraphs[0]]); ?></div>
            <?php echo wengertsberg_preview_render([$groups['approach-photo']]); ?><div class="preview-approach-text"><?php echo wengertsberg_preview_render([$approach_paragraphs[1]]); ?></div>
        </div>
    </section>
    <section id="referenzen" class="preview-references section"><div class="wrap preview-reference-grid"><div class="preview-section-heading"><span class="preview-section-number" aria-hidden="true">04</span><?php echo wengertsberg_preview_render([$reference_heading]); ?></div><div class="reference-intro"><?php echo wengertsberg_preview_render($reference_body); ?></div><?php echo wengertsberg_preview_render([$groups['reference-list']]); ?></div></section>
    <section id="kontakt" class="contact section"><div class="wrap contact-grid"><?php echo $contact_html . wengertsberg_preview_render([$groups['contact-details']]); ?><div class="preview-contact-place"><?php echo wengertsberg_preview_render([$groups['about-place']]); ?></div></div></section>
    </div>
    <?php if ($review): ?>
    <dialog class="preview-dialog" id="preview-notes" aria-labelledby="preview-notes-title">
        <button class="preview-dialog-close" type="button" data-close-preview aria-label="Hinweise schließen">×</button>
        <h2 id="preview-notes-title">Was Richtung B verändert</h2>
        <p>Diese Vorschau folgt der gelieferten Richtung B für Desktop und Handy: grüner Einstieg, goldene Akzente, serifenlose Schrift und nummerierte Abschnitte. Die bisherige Website bleibt zum Vergleich verfügbar.</p>
        <div class="preview-change-list">
            <div><h3>Einstieg aus Richtung B</h3><p>Die Überschrift „Vom Shopfloor bis in die Vorstandsetage.“ steht mit goldener Unterzeile auf Grün. Am Rechner steht das Porträt rechts, am Handy folgt es unter dem Kontaktbutton.</p><button type="button" data-review-jump="#main">Einstieg ansehen</button></div>
            <div><h3>Über mich auf hellem Hintergrund</h3><p>Der persönliche Einstieg und die Erfahrung aus Betrieb und Verein stehen zusammen im hellen Abschnitt „Über mich“. Die Qualifikationen lassen sich auf dem Handy aufklappen.</p><button type="button" data-review-jump="#ueber-mich">Abschnitt ansehen</button></div>
            <div><h3>Leistungen leichter überblicken</h3><p>Die Leistungen stehen wie in der Vorlage in zwei Spalten, am Handy untereinander. Die Referenzen folgen als vier kleinere Karten. Linien und Abschnittsnummern geben Orientierung.</p><button type="button" data-review-jump="#leistungen">Leistungen ansehen</button></div>
            <div><h3>Kundenarbeit greifbar machen</h3><p>Kundengeschichten und Firmenlogos kommen mit echten Inhalten und Freigaben dazu. Der nächste Button zeigt den möglichen Aufbau.</p><button type="button" data-open-cases>Kundengeschichten und Logos ansehen</button></div>
        </div>
    </dialog>
    <dialog class="preview-dialog preview-cases-dialog" id="preview-cases" aria-labelledby="preview-cases-title">
        <button class="preview-dialog-close" type="button" data-close-preview aria-label="Kundenbeispiele schließen">×</button>
        <p class="preview-example-label">Bausteine zum Ausprobieren</p><h2 id="preview-cases-title">Kundengeschichten und Firmenlogos</h2>
        <p>So könnten wir die Arbeit konkreter zeigen. Namen, Logos, Zitate und Ergebnisse werden erst nach Freigabe veröffentlicht.</p>
        <article class="preview-case-example"><p class="preview-example-label">Beispielaufbau einer Kundengeschichte</p>
            <?php echo $case_example ?: '<h3>Eine Kundengeschichte</h3>'; ?>
            <dl><dt>Ausgangssituation</dt><dd>Welche Frage oder Herausforderung hatte das Team? Von Alex zu ergänzen.</dd><dt>Alex’ Beitrag</dt><dd>Was hat Alex konzipiert, moderiert oder begleitet? Das konkrete Vorgehen ergänzen.</dd><dt>Ergebnis</dt><dd>Was wurde erreicht oder geklärt? Nur belegbare und freigegebene Aussagen aufnehmen.</dd><dt>Kundenname und Zitat</dt><dd>Nach Freigabe nennen. Bei einem Einsatz über andere Auftraggeber Alex’ Rolle deutlich machen.</dd></dl>
        </article>
        <h3 class="preview-logo-heading">So könnten die Logos erscheinen</h3><p>Die Felder unten sind ausdrücklich Platzhalter und stehen für keine tatsächlichen Kunden.</p>
        <div class="preview-logo-options" role="group" aria-label="Logodarstellung"><button type="button" data-logo-mode="row" aria-pressed="true">Ruhige Reihe</button><button type="button" data-logo-mode="band" aria-pressed="false">Langsam laufendes Band</button></div>
        <div class="preview-logo-demo" data-logo-demo data-mode="row" data-paused="false" tabindex="0" role="region" aria-label="Logobeispiel mit Platzhaltern">
            <div class="preview-logo-track"><?php for ($copy = 0; $copy < 2; $copy++): ?><div class="preview-logo-group" <?php echo $copy ? 'aria-hidden="true"' : ''; ?>><?php for ($slot = 0; $slot < 6; $slot++): ?><div class="preview-logo-placeholder">Firmenlogo</div><?php endfor; ?></div><?php endfor; ?></div>
        </div>
        <button type="button" class="preview-logo-pause" data-logo-pause aria-pressed="false" hidden>Bewegung pausieren</button>
        <p class="preview-example-note">Bei wenigen Logos passt die ruhige Reihe. Bei ausreichend freigegebenen Logos kann das Band eingesetzt werden. Es pausiert bei Berührung mit dem Mauszeiger oder Tastaturfokus und bleibt bei reduzierter Bewegung statisch.</p>
        <p>Für die nächste Fassung brauchen wir zwei bis drei freigegebene Kundengeschichten und die zugehörigen Logodateien. Echte Fotos aus Workshops oder Gesprächen können die vorhandenen Bilder ergänzen.</p>
    </dialog>
    <dialog class="preview-dialog preview-consent-dialog" id="preview-consent" aria-labelledby="preview-consent-title">
        <button class="preview-dialog-close" type="button" data-close-preview aria-label="Beispiel schließen">×</button>
        <p class="preview-example-label">Gestaltungsbeispiel</p><h2 id="preview-consent-title">Darf ich diese Website auswerten?</h2>
        <p>Mit Ihrer Erlaubnis zähle ich Besuche und schaue mir stichprobenartig an, wie die Seite genutzt wird, zum Beispiel Klicks und Scrollbewegungen. Formulare werden dabei nicht aufgezeichnet. Die Website funktioniert auch, wenn Sie ablehnen.</p>
        <div class="preview-choice-example"><button type="button" disabled>Erlauben</button><button type="button" disabled>Ablehnen</button></div>
        <a href="<?php echo esc_url(home_url('/datenschutzerklaerung/')); ?>">Mehr dazu in der Datenschutzerklärung</a>
        <p class="preview-example-note">Im Entwurf wird keine Analyse gestartet. Die Auswahl oben zeigt nur die Gestaltung.</p>
    </dialog>
    <?php endif; ?>
    <?php
    return wp_filter_content_tags(ob_get_clean(), 'the_content');
}, 20);
