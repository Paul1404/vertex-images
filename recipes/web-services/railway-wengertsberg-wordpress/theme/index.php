<?php
defined('ABSPATH') || exit;
get_header();
if (have_posts()) {
    while (have_posts()) {
        the_post();
        if (is_front_page()) {
            the_content();
        } else {
            echo '<article class="wrap legal-content"><h1>' . esc_html(get_the_title()) . '</h1>';
            the_content();
            echo '</article>';
        }
    }
}
get_footer();
