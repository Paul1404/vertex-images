<?php
defined('ABSPATH') || exit;

function wengertsberg_contact_ready(): bool {
    foreach (['HOST', 'PORT', 'USER', 'PASSWORD'] as $key) {
        if (!getenv('WENGERTSBERG_SMTP_' . $key)) {
            return false;
        }
    }
    return (bool) is_email(get_theme_mod('wengertsberg_email', ''));
}

function wengertsberg_contact_form(): string {
    if (!wengertsberg_contact_ready()) {
        return '';
    }
    ob_start(); ?>
    <form class="contact-form" method="post" action="<?php echo esc_url(rest_url('wengertsberg/v1/contact')); ?>" hidden data-token-url="<?php echo esc_url(rest_url('wengertsberg/v1/contact-token')); ?>" data-send-url="<?php echo esc_url(rest_url('wengertsberg/v1/contact')); ?>">
        <div class="contact-field"><label for="contact-name">Ihr Name</label><input id="contact-name" name="name" autocomplete="name" required minlength="2" maxlength="120"></div>
        <div class="contact-field"><label for="contact-email">Ihre E-Mail-Adresse</label><input id="contact-email" name="email" type="email" autocomplete="email" required maxlength="254"></div>
        <div class="contact-field"><label for="contact-message">Ihre Nachricht</label><textarea id="contact-message" name="message" rows="5" required minlength="10" maxlength="5000"></textarea></div>
        <div class="contact-trap" aria-hidden="true"><label for="contact-fax">Dieses Feld bitte leer lassen</label><input id="contact-fax" name="contact_company_fax" tabindex="-1" autocomplete="off"></div>
        <p class="contact-privacy">Ihre Angaben werden zur Beantwortung Ihrer Anfrage verarbeitet. Mehr dazu in der <a href="<?php echo esc_url(home_url('/datenschutzerklaerung/')); ?>">Datenschutzerklärung</a>.</p>
        <button class="contact-submit" type="submit" disabled>Nachricht senden</button>
        <p class="contact-status" role="status" aria-live="polite" tabindex="-1"></p>
    </form>
    <noscript><p>Bitte nutzen Sie die E-Mail-Adresse oder Telefonnummer oben, um Kontakt aufzunehmen.</p></noscript>
    <?php return ob_get_clean();
}

function wengertsberg_contact_response(array $body, int $status = 200): WP_REST_Response {
    return new WP_REST_Response($body, $status, ['Cache-Control' => 'no-store, private, max-age=0']);
}

function wengertsberg_contact_token(): WP_REST_Response {
    $payload = time() . '.' . bin2hex(random_bytes(16));
    return wengertsberg_contact_response(['token' => $payload . '.' . hash_hmac('sha256', $payload, wp_salt('nonce'))]);
}

// Atomic counters and send receipts contain hashes/status only, never message
// contents or raw visitor identifiers. Expiration is encoded in each key.
function wengertsberg_contact_slot(string $scope, int $period, int $limit): bool {
    global $wpdb;
    $window = (int) floor(time() / $period) * $period;
    $key = 'wengertsberg_contact_rate_' . ($window + $period + 3600) . '_' . $scope;
    add_option($key, '0', '', false);
    return $wpdb->query($wpdb->prepare(
        "UPDATE {$wpdb->options} SET option_value = CAST(option_value AS UNSIGNED) + 1 WHERE option_name = %s AND CAST(option_value AS UNSIGNED) < %d",
        $key, $limit
    )) === 1;
}

function wengertsberg_contact_cleanup(): void {
    global $wpdb;
    $names = $wpdb->get_col($wpdb->prepare(
        "SELECT option_name FROM {$wpdb->options} WHERE option_name LIKE %s ORDER BY option_name LIMIT 1000",
        $wpdb->esc_like('wengertsberg_contact_') . '%'
    ));
    foreach ($names as $name) {
        if (preg_match('/^wengertsberg_contact_(?:rate|send)_(\d+)_/', $name, $match) && (int) $match[1] < time()) {
            delete_option($name);
        }
    }
}
add_action('wengertsberg_contact_cleanup', 'wengertsberg_contact_cleanup');
add_action('init', function () {
    if (!wp_next_scheduled('wengertsberg_contact_cleanup')) {
        wp_schedule_event(time() + 3600, 'hourly', 'wengertsberg_contact_cleanup');
    }
});

function wengertsberg_contact_send(WP_REST_Request $request): WP_REST_Response {
    $fail = fn($message, $status) => wengertsberg_contact_response(['ok' => false, 'message' => $message], $status);
    $origin = rtrim($request->get_header('origin'), '/');
    $site = wp_parse_url(home_url('/'));
    $expected_origin = $site['scheme'] . '://' . $site['host'] . (isset($site['port']) ? ':' . $site['port'] : '');
    if ($origin !== $expected_origin) {
        return $fail('Bitte nutzen Sie das Kontaktformular auf dieser Website.', 403);
    }
    if (strlen($request->get_body()) > 26000) {
        return $fail('Ihre Nachricht ist zu lang.', 413);
    }
    $data = $request->get_json_params();
    foreach (['name', 'email', 'message', 'token', 'contact_company_fax'] as $field) {
        if (!is_array($data) || !isset($data[$field]) || !is_string($data[$field])) {
            return $fail('Bitte füllen Sie Name, E-Mail-Adresse und Nachricht aus.', 400);
        }
    }
    $token = $data['token'];
    if (!preg_match('/^(\d{10})\.([a-f0-9]{32})\.([a-f0-9]{64})$/D', $token, $parts)
        || !hash_equals(hash_hmac('sha256', $parts[1] . '.' . $parts[2], wp_salt('nonce')), $parts[3])) {
        return $fail('Bitte laden Sie das Formular neu und versuchen Sie es noch einmal.', 403);
    }
    $age = time() - (int) $parts[1];
    if ($age < 2 || $age > 1800) {
        return $fail('Bitte laden Sie das Formular neu und versuchen Sie es noch einmal.', 403);
    }
    $name = trim($data['name']);
    $email = trim($data['email']);
    $message = sanitize_textarea_field($data['message']);
    if ($data['contact_company_fax'] !== '' || mb_strlen($name) < 2 || mb_strlen($name) > 120
        || preg_match('/[\r\n\x00]/', $name . $email) || strlen($email) > 254 || !is_email($email)
        || mb_strlen($message) < 10 || mb_strlen($message) > 5000) {
        return $fail('Bitte prüfen Sie Ihren Namen, Ihre E-Mail-Adresse und Ihre Nachricht.', 400);
    }
    if (!wengertsberg_contact_ready()) {
        return $fail('Das Formular ist gerade nicht verfügbar. Bitte schreiben Sie direkt per E-Mail.', 503);
    }
    $fingerprint = hash_hmac('sha256', wp_json_encode([$name, $email, $message]), wp_salt('auth'));
    $key = 'wengertsberg_contact_send_' . ((int) $parts[1] + 3600) . '_' . hash('sha256', $token);
    $receipt = get_option($key);
    if ($receipt) {
        if (!hash_equals($receipt['fingerprint'], $fingerprint)) {
            return $fail('Bitte laden Sie das Formular für eine neue Nachricht neu.', 409);
        }
        return $receipt['status'] === 'sent'
            ? wengertsberg_contact_response(['ok' => true, 'message' => 'Vielen Dank! Ihre Nachricht wurde versendet.'])
            : $fail('Ihre Nachricht wird bereits versendet. Bitte versuchen Sie es gleich noch einmal.', 409);
    }
    if (!add_option($key, ['status' => 'sending', 'fingerprint' => $fingerprint], '', false)) {
        return $fail('Ihre Nachricht wird bereits bearbeitet. Bitte versuchen Sie es gleich noch einmal.', 409);
    }
    $email_scope = hash_hmac('sha256', strtolower($email), wp_salt('auth'));
    if (!wengertsberg_contact_slot('minute', 60, 3) || !wengertsberg_contact_slot('hour', 3600, 30)
        || !wengertsberg_contact_slot($email_scope, 3600, 3)) {
        delete_option($key);
        $response = $fail('Es wurden gerade mehrere Nachrichten gesendet. Bitte versuchen Sie es später oder schreiben Sie direkt per E-Mail.', 429);
        $response->header('Retry-After', '60');
        return $response;
    }
    $configure = function ($mailer) {
        $mailer->isSMTP();
        $mailer->Host = getenv('WENGERTSBERG_SMTP_HOST');
        $mailer->Port = (int) getenv('WENGERTSBERG_SMTP_PORT');
        $mailer->SMTPAuth = true;
        $mailer->Username = getenv('WENGERTSBERG_SMTP_USER');
        $mailer->Password = getenv('WENGERTSBERG_SMTP_PASSWORD');
        $mailer->SMTPSecure = 'tls';
        $mailer->SMTPDebug = 0;
        $mailer->Timeout = 10;
        $mailer->Sender = 'info@wengertsberg.de';
    };
    $headers = ['Content-Type: text/plain; charset=UTF-8', 'From: Wengertsberg Website <info@wengertsberg.de>', 'Reply-To: ' . $email];
    $body = "Neue Anfrage über wengertsberg.de\n\nName: {$name}\nE-Mail: {$email}\n\nNachricht:\n{$message}\n\nAnfrage-ID: " . substr($parts[2], 0, 12);
    add_action('phpmailer_init', $configure);
    try {
        $sent = wp_mail(sanitize_email(get_theme_mod('wengertsberg_email')), 'Kontaktanfrage über wengertsberg.de: ' . $name, $body, $headers);
    } catch (Throwable $error) {
        $sent = false;
    } finally {
        remove_action('phpmailer_init', $configure);
    }
    if (!$sent) {
        delete_option($key);
        return $fail('Ihre Nachricht konnte nicht versendet werden. Bitte versuchen Sie es erneut oder schreiben Sie direkt per E-Mail.', 502);
    }
    update_option($key, ['status' => 'sent', 'fingerprint' => $fingerprint], false);
    return wengertsberg_contact_response(['ok' => true, 'message' => 'Vielen Dank! Ihre Nachricht wurde versendet.']);
}

add_action('rest_api_init', function () {
    register_rest_route('wengertsberg/v1', '/contact-token', ['methods' => 'GET', 'callback' => 'wengertsberg_contact_token', 'permission_callback' => '__return_true']);
    register_rest_route('wengertsberg/v1', '/contact', ['methods' => 'POST', 'callback' => 'wengertsberg_contact_send', 'permission_callback' => '__return_true']);
});
