# Wengertsberg WordPress image

Fleet runs this image on Vertex RKE2 with a persistent `/var/www/html` volume and separate MariaDB service. Apache uses prefork on port 80. Preserve the existing table prefix, `https://wengertsberg.de` URL and populated volume.

## Theme and page content

`theme/` is the managed classic theme. The entrypoint syncs its files into `wp-content/themes/wengertsberg`; it does not activate the theme or replace pages, options, media or other themes. `site-content.html` is only an initial fixture seed. Do not import it over editorial changes.

Theme CSS and JavaScript use content-hashed URLs. Run `build-theme-assets.sh` after changing them. The editable share artwork is `share-preview.svg`; keep its PNG export in sync. `theme.json` preserves the Group block markup used by the classic theme.

The public homepage uses the default theme layout. The `/?entwurf=2` review route is noindex and contains comparison controls; `/?vergleich=1` shows the previous layout. Keep review controls and examples off the public homepage. Both routes stay out of analytics.

## Contact and privacy

Email and phone details are set in Appearance > Customize > Wengertsberg Kontakt. The REST contact form uses runtime variables `WENGERTSBERG_SMTP_HOST`, `WENGERTSBERG_SMTP_PORT`, `WENGERTSBERG_SMTP_USER` and `WENGERTSBERG_SMTP_PASSWORD`. Keep credentials in secret references and use authenticated STARTTLS with certificate verification. Do not log message bodies or SMTP debug output.

The form validates and rate-limits requests, prevents token reuse, and stores only short-lived hashed receipts. It does not save message content in WordPress. Keep the privacy notice aligned with the actual mail route. A successful SMTP response does not prove delivery; verify the destination mailbox without sending test mail to visitors.

The shared consent loader owns consent, expiry, DNT/GPC and withdrawal. The theme changes only its presentation. No analytics request should occur before an explicit choice. Preserve the working consent interface if the loader is unavailable. Check fresh-visitor silence, allow, reject and withdrawal with a local tracker stub.

## Checks and recovery

Run `bash recipes/web-services/source-checks.sh` from the repository root. For PHP edits, run `php -l` on each file; the source checks cover shell, JavaScript and fixtures. After a theme change, check the public page at desktop and 320px, keyboard navigation, contact success and failure, canonical metadata, JSON-LD, robots, sitemap and real 404 responses. Keep `blog_public=1`; review URLs remain noindex. Check page and database health through the canonical URL.

Before changing the active theme or front-page option, back up the database, media and current theme outside Git. Restore requires WordPress content and options as well as the image. Production administration, mail receipt and restore are separate from the image fixtures.
