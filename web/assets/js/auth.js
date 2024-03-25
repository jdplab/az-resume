// Function to parse JWT token
// Function to parse JWT token
function parseJwt(token) {
    console.log('Parsing JWT token:', token);
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error('Error parsing JWT token:', error);
        return null;
    }
}

function storeCurrentPageURL() {
    sessionStorage.setItem('redirectFrom', window.location.href);
}

// Function to store token in sessionStorage
function storeToken(token) {
    console.log('Storing token in sessionStorage:', token);
    sessionStorage.setItem('id_token', token);
}

// Function to clear token from sessionStorage
function clearToken() {
    console.log('Clearing token from sessionStorage');
    sessionStorage.removeItem('id_token');
    sessionStorage.removeItem('tokenClaims');
}

function generateNonce(length) {
    var result = '';
    var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for (var i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

// Function to handle login
function login() {
    console.log('Handling login');
    const existingIdToken = sessionStorage.getItem('id_token');
    if (existingIdToken) {
        console.log('Valid token already exists, skipping authentication');
        displayModal('You are already signed in.');
        return;
    }
    var nonce = generateNonce(32);
    sessionStorage.setItem('nonce', nonce);
    // Store the current page URL before redirecting
    storeCurrentPageURL();
    // Redirect user to Azure AD B2C for authentication
    window.location.href = 'https://azresume.b2clogin.com/azresume.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_SignUpSignIn&client_id=8437bac7-4641-445c-83f2-20a4105108b5&nonce=' + nonce + '&redirect_uri=https%3A%2F%2Fjon-polansky.com%2F.auth%2Flogin%2Faadb2c%2Fcallback&scope=openid&response_type=id_token&prompt=login&state=' + encodeURIComponent(window.location.href);
}

// Function to handle logout
function logout() {
    clearToken();
    window.location.href = '/logoff.html';
}

// Function to handle the authentication callback
function handleAuthenticationCallback() {
    // Remove the '#' character from the start of the URL fragment
    const fragment = window.location.hash.substring(1);
    // Parse fragment parameters from URL
    const urlParams = new URLSearchParams(fragment);
    const idToken = urlParams.get('id_token');
    const error = urlParams.get('error');
    const redirectFrom = urlParams.get('state');

    // If an ID token is present, parse its claims and store them
    if (idToken) {
        const tokenClaims = parseJwt(idToken);
        if (tokenClaims) {
            // Retrieve the nonce from session storage
            const storedNonce = sessionStorage.getItem('nonce');
            if (tokenClaims.nonce !== storedNonce) {
                // Nonce does not match, handle error
                console.error('Nonce mismatch error');
                displayModal('Authentication failed. Please try again.');
                window.location.href = '/';
                return;
            }
            sessionStorage.setItem('id_token', idToken);
            sessionStorage.setItem('tokenClaims', JSON.stringify(tokenClaims));
        }
    }

    window.location.replace(decodeURIComponent(redirectFrom) || '/');
    if (error) {
        // Authentication failed, handle the error (e.g., display error message)
        console.error('Authentication error:', error);
        displayModal('Authentication failed. Please try again.');
        // Redirect user to the home page or another appropriate page
        window.location.href = '/';
    }
}

window.addEventListener('load', function() {
    // Get the login/logout button
    var loginButton = document.getElementById('loginButton');

    // Check if the user is logged in
    if (sessionStorage.getItem('id_token')) {
        // If the user is logged in, change the button text to "Logout"
        // and set the onclick function to logout()
        loginButton.textContent = 'Logout';
        loginButton.onclick = function() { logout(); };

        // Call the Azure Function to check if the user is an admin
        fetch('https://jpolanskyresume-functionapp.azurewebsites.net/api/verifytoken', {
            headers: {
                'Authorization': 'Bearer ' + sessionStorage.getItem('id_token')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.admin) {
                // The user is an admin
                // Show the admin section
                const blogposts = document.getElementById('blogposts');
                const adminSection = document.getElementById('adminSection');
                if (adminSection) {
                    adminSection.style.opacity = '1';
                    adminSection.style.visibility = 'visible';
                    adminSection.style.display = 'block';
                }
                if (blogposts) {
                    blogposts.style.marginTop = '4em';
                    blogposts.style.borderTop = 'solid 2px #efefef';
                    blogposts.style.paddingTop = '4em';
                }
            }
        });
    } else {
        // If the user is not logged in, change the button text to "Login"
        // and set the onclick function to login()
        loginButton.textContent = 'Login';
        loginButton.onclick = function() { login(); };
    }
})

setInterval(refreshToken, 3300000);
function refreshToken() {
    console.log('Refreshing token');
    var nonce = generateNonce(32);
    sessionStorage.setItem('nonce', nonce);
    window.location.href = 'https://azresume.b2clogin.com/azresume.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_SignUpSignIn&client_id=8437bac7-4641-445c-83f2-20a4105108b5&nonce=' + nonce + '&redirect_uri=https%3A%2F%2Fjon-polansky.com%2F.auth%2Flogin%2Faadb2c%2Fcallback&scope=openid&response_type=id_token&prompt=none&state=' + encodeURIComponent(window.location.href);
}