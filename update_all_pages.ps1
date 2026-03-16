# PowerShell script to update all HTML pages with auth integration

$pages = @("voice.html", "community.html", "permits.html")

foreach ($page in $pages) {
    $filePath = "frontend/app/$page"
    
    Write-Host "Updating $page..."
    
    # Read file content
    $content = Get-Content $filePath -Raw
    
    # Add Google client ID meta tag if not present
    if ($content -notmatch 'google-signin-client_id') {
        $content = $content -replace '(<title>.*?</title>)', "`$1`n    <meta name=`"google-signin-client_id`" content=`"YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com`">"
    }
    
    # Add Google Sign-In initialization script if not present
    if ($content -notmatch 'google.accounts.id.initialize') {
        $initScript = @"
    <script>
        // Initialize Google Sign-In button
        window.onload = function() {
            if (typeof google !== 'undefined') {
                google.accounts.id.initialize({
                    client_id: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
                    callback: handleCredentialResponse
                });
                google.accounts.id.renderButton(
                    document.getElementById('loginBtn'),
                    { theme: 'filled_blue', size: 'large', text: 'signin_with', shape: 'pill' }
                );
            }
        };
    </script>
"@
        $content = $content -replace '(</head>)', "$initScript`n`$1"
    }
    
    # Update nav-actions to include user profile and login button
    $navActionsOld = @"
            <div class="nav-actions">
                <button class="notification-btn" id="notificationBtn">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge">5</span>
                </button>
            </div>
"@
    
    $navActionsNew = @"
            <div class="nav-actions">
                <button class="notification-btn" id="notificationBtn">
                    <i class="fas fa-bell"></i>
                    <span class="notification-badge">5</span>
                </button>
                <div id="userProfile" style="display: none; align-items: center; margin-left: 1rem;"></div>
                <div id="loginBtn" style="margin-left: 1rem;"></div>
            </div>
"@
    
    $content = $content -replace [regex]::Escape($navActionsOld), $navActionsNew
    
    # Add Google Sign-In script before closing body tag if not present
    if ($content -notmatch 'accounts.google.com/gsi/client') {
        $content = $content -replace '(<script src="js/config.js"></script>)', "    <!-- Google Sign-In -->`n    <script src=`"https://accounts.google.com/gsi/client`" async defer></script>`n    `$1"
    }
    
    # Add auth.js script if not present
    if ($content -notmatch 'auth.js') {
        $content = $content -replace '(<script src="js/api.js"></script>)', "`$1`n    <script src=`"js/auth.js`"></script>"
    }
    
    # Write updated content back to file
    Set-Content $filePath -Value $content -NoNewline
    
    Write-Host "✓ Updated $page"
}

Write-Host "`nAll pages updated successfully!"
