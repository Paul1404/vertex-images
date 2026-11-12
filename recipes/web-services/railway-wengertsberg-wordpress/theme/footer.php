<?php defined('ABSPATH') || exit; ?>
</main>
<footer class="site-footer">
    <div class="wrap">
        <div class="footer-top"><?php wengertsberg_brand(); ?></div>
        <div class="footer-bottom"><span>© <?php echo esc_html(wp_date('Y')); ?> Alexander Eckert</span><nav class="footer-links" aria-label="Rechtliche Informationen"><a href="<?php echo esc_url(home_url('/impressum/')); ?>">Impressum</a><a href="<?php echo esc_url(home_url('/datenschutzerklaerung/')); ?>">Datenschutz</a><button class="analytics-settings-link" type="button" data-analytics-open hidden aria-expanded="false" aria-controls="wengertsberg-analytics-panel">Analyse-Einstellungen</button><a href="#main">Nach oben ↑</a></nav></div>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
