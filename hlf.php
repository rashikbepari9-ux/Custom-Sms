<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 0);

// CORS Headers
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Get parameters from URL
$sms = isset($_GET['sms']) ? $_GET['sms'] : '';
$number = isset($_GET['number']) ? $_GET['number'] : '';
$owner = isset($_GET['owner']) ? $_GET['owner'] : '@RASHIK_69';
$business = isset($_GET['business']) ? $_GET['business'] : 'Carrybee Shop';

// Validate inputs
if (empty($sms) || empty($number)) {
    $response = [
        "success" => false,
        "owner" => $owner,
        "reason" => "Missing required fields: sms and number"
    ];
    echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit();
}

// Clean phone number
$number = preg_replace('/[^0-9+]/', '', $number);

// Carrybee API URL
$url = "https://api-merchant.carrybee.com/api/v2/merchant/register";

// Request Headers
$headers = [
    "Content-Type: application/json",
    "Accept: application/json",
    "User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Origin: https://merchant.carrybee.com",
    "Referer: https://merchant.carrybee.com/"
];

// Request Payload
$payload = [
    "name" => $sms,
    "phone_number" => $number,
    "business_name" => $business
];

// Initialize cURL
$ch = curl_init($url);

// Set cURL options
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => json_encode($payload),
    CURLOPT_HTTPHEADER => $headers,
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_TIMEOUT => 30
]);

// Execute request
$api_response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

// Check for cURL errors
if ($curl_error) {
    $response = [
        "success" => false,
        "owner" => $owner,
        "reason" => "Network error: " . $curl_error
    ];
    echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit();
}

// Process API response
if ($http_code == 200) {
    $result = json_decode($api_response, true);
    
    if (!$result['error']) {
        $otp_data = $result['data'];
        $otp_prefix = $otp_data['otp_prefix'];
        
        // SMS Message Format
        $sms_message = "[Carrybee] Hi {$sms}, your code is {$otp_prefix} to join by-{$owner}";
        
        $response = [
            "success" => false,
            "owner" => $owner,
            "reason" => "Merchant registered successfully",
            "sms_message" => $sms_message,
            "otp_details" => [
                "otp_prefix" => $otp_prefix,
                "otp_expires_at" => $otp_data['otp_expires_at'],
                "full_message" => $sms_message
            ],
            "input" => [
                "name" => $sms,
                "phone" => $number,
                "business" => $business
            ]
        ];
    } else {
        $response = [
            "success" => false,
            "owner" => $owner,
            "reason" => $result['message'] ?? 'Registration failed'
        ];
    }
} else {
    $response = [
        "success" => false,
        "owner" => $owner,
        "reason" => "API Error: HTTP " . $http_code,
        "details" => $api_response
    ];
}

// Return JSON response
echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>