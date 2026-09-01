<?php
require_once __DIR__ . '/inc/includes.php';

$user = new User();
if ($user->getFromDBByCrit(['name' => 'glpi'])) {
    $token = $user->generateToken('api_token');
    echo "GENERATED_GLPI_USER_TOKEN=" . $token . "\n";
} else {
    echo "USER_NOT_FOUND\n";
}

$apiClient = new APIClient();
if ($apiClient->getFromDBByCrit(['name' => 'Laravel'])) {
    $appToken = $apiClient->generateToken('app_token');
    echo "GENERATED_GLPI_APP_TOKEN=" . $appToken . "\n";
}
