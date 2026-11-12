<?php
// Runs only in the isolated image fixture with a synthetic page and database.
chdir('/var/www/html');
$REX = ['REDAXO' => false, 'HTDOCS_PATH' => './', 'BACKEND_FOLDER' => 'redaxo', 'LOAD_PAGE' => false];
ob_start();
require 'redaxo/src/core/boot.php';
include_once rex_path::core('packages.php');
// Mirror frontend.php consuming the render buffer before final output.
ob_get_clean();
rex_response::sendPage('<html><body>Public fixture<script defer src="https://umami.pdcd.net/script.js" data-website-id="fixture"></script></body></html>');
