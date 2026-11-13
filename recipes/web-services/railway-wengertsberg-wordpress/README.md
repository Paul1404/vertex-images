# Wengertsberg WordPress image

Fleet runs this image on Vertex RKE2 with a persistent `/var/www/html` volume and separate MariaDB service. Apache uses prefork on port 80. Preserve the existing table prefix, `https://wengertsberg.de` URL and populated volume.

## Theme and page content

`theme/` is the managed classic theme. The entrypoint syncs its files into `wp-content/themes/wengertsberg`; it does not activate the theme or replace pages, options, media or other themes. `site-content.html` is only an initial fixture seed. Do not import it over editorial changes.

Theme CSS and JavaScript use content-hashed URLs. Run `build-theme-assets.sh` after changing them. The editable share artwork is `share-preview.svg`; keep its PNG export in sync. `theme.json` preserves the Group block markup used by the classic theme.

`design-preview.php` renders the public layout from saved WordPress blocks without changing stored content. Missing managed groups fall back to the original page. The `direction-b` class scopes the public skin; `design-preview` adds review controls. The `/?entwurf=2` review route is noindex and contains comparison controls; `/?vergleich=1` shows the previous layout. Keep review controls and examples off the public homepage. Both routes stay out of analytics.

## Contact and privacy

Email and phone details are set in Appearance > Customize > Wengertsberg Kontakt. The recipient comes from the admin contact setting, not submitted fields. The REST contact form uses runtime variables `WENGERTSBERG_SMTP_HOST`, `WENGERTSBERG_SMTP_PORT`, `WENGERTSBERG_SMTP_USER` and `WENGERTSBERG_SMTP_PASSWORD`. Keep credentials in secret references and use authenticated STARTTLS with certificate verification. Do not log message bodies or SMTP debug output.

SMTP uses Stalwart on `mx.pdcd.net`, with `mail.pdcd.net` retained by some clients as a compatibility alias. Preserve the working hostname and TLS verification. STARTTLS uses port 587. Amazon SES can still relay outbound mail; the privacy notice must cover that route when used.

The form validates and rate-limits requests, prevents token reuse, and stores only short-lived hashed receipts. It does not save message content in WordPress. Hourly WordPress cron removes counters and receipts. Check request origins, field types/lengths and email; keep the honeypot and atomic global/per-email limits. Use HTTP 403 for invalid tokens: WordPress can return 200 for an unsupported 419 status. Keep the privacy notice aligned with the mail route. A successful SMTP response does not prove delivery; verify the destination mailbox without sending test mail to visitors.

The shared consent loader owns consent, expiry, DNT/GPC and withdrawal. The theme hides its unsolicited prompt and floating button, then opens a non-modal panel from the footer. The adapter must not write consent storage or infer consent from dismissal. Hide the footer trigger when analytics is unavailable; closing the panel must restore keyboard focus without scrolling to the footer. No analytics request should occur before an explicit choice. Preserve the working consent interface if the loader is unavailable. Check fresh-visitor silence, allow, reject and withdrawal with a local tracker stub.

Below 800px, JavaScript wraps the existing qualification text in a native details disclosure and restores the same nodes on desktop. Without JavaScript it stays expanded. Keep the mobile contact action's 44px target; below 360px it uses a labelled envelope icon. Use the same Sie-form page copy on desktop and mobile.

`seo.php` owns search/share metadata and the linked WebSite, Organization, Person and WebPage JSON-LD graph. Keep the document title `Training & Consulting | Wengertsberg`; share copy is separate. Attachment metadata supplies missing image dimensions without replacing explicit dimensions. `share-preview.png` is a 1200x630 export with a hashed public filename.

## Checks and recovery

Run `bash recipes/web-services/source-checks.sh` from the repository root. For PHP edits, run `php -l` on each file; the source checks cover shell, JavaScript and fixtures. After a theme change, check the public page at desktop and 320px, keyboard navigation, contact success and failure, canonical metadata, JSON-LD, robots, sitemap and real 404 responses. Keep `blog_public=1`; review URLs remain noindex. Check page and database health through the canonical URL.

Before changing the active theme or front-page option, back up the database, media and current theme outside Git. Restore requires WordPress content and options as well as the image. Production administration, mail receipt and restore are separate from the image fixtures.

When retiring Elementor, deactivate it in a separate request before changing
WordPress options; its hooks stay loaded for that request. Set an authorized
WordPress user before importing trusted block markup so inline SVG is retained.
