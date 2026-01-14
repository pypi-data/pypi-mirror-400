GAM OAuth Integration
=====================

The GAM (GeneXus Access Manager) module provides OAuth 2.0 authentication functionality for integrating with GeneXus applications. It enables user authentication, token management, and access to user information.

This section covers:

* Generating OAuth signin URLs
* Obtaining access tokens
* Refreshing tokens
* Retrieving user information

For each operation, you have implementation options using the Low-Level Service Layer.

Overview
--------

OAuth 2.0 Flow with GAM:

1. **Generate Signin URL**: Create URL for user authentication
2. **User Authorization**: User authenticates via browser
3. **Get Access Token**: Exchange credentials/code for access token
4. **Access Resources**: Use token to access protected resources
5. **Refresh Token**: Obtain new access token when expired

Generate Signin URL
-------------------

Creates an OAuth 2.0 authorization URL for browser-based authentication flows.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.gam.clients import GAMClient
    import secrets

    client = GAMClient()
    
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    signin_url = client.generate_signing_url(
        client_id="your-app-client-id",
        redirect_uri="https://yourapp.com/callback",
        scope="gam_user_data",
        state=state
    )
    
    print(f"Redirect user to: {signin_url}")
    # Store state for validation when user returns

**Parameters:**

* ``client_id``: (Required) Your application's client ID
* ``redirect_uri``: (Required) Callback URL registered in your app
* ``scope``: OAuth scope (default: "gam_user_data")
* ``state``: (Required) Random string for CSRF protection
* ``response_type``: Response type (default: "code")

**Returns:**
String containing the complete authorization URL.

**Scopes:**

* ``gam_user_data``: Basic user information
* ``gam_user_roles``: User roles and permissions
* Combine with ``+``: ``"gam_user_data+gam_user_roles"``


Get Access Token
----------------

Obtains an access token using the Resource Owner Password Credentials grant.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.gam.clients import GAMClient

    client = GAMClient()
    
    token_response = client.get_access_token(
        client_id="your-app-client-id",
        client_secret="your-app-client-secret",
        username="user@example.com",
        password="user-password",
        scope="gam_user_data+gam_user_roles"
    )
    
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    expires_in = token_response['expires_in']
    
    print(f"Access token: {access_token}")
    print(f"Expires in: {expires_in} seconds")

**Parameters:**

* ``client_id``: (Required) Application client ID
* ``client_secret``: (Required) Application client secret
* ``username``: (Required) User's username/email
* ``password``: (Required) User's password
* ``grant_type``: Grant type (default: "password")
* ``scope``: OAuth scope (default: "gam_user_data")
* ``authentication_type_name``: Auth type (default: "local")
* ``repository``: Repository ID for multitenant setups
* ``initial_properties``: Custom user properties array
* ``request_token_type``: Token type: "OAuth" or "Web" (default: "OAuth")

**Returns:**
Dictionary containing:

* ``access_token``: The access token
* ``token_type``: Token type (usually "Bearer")
* ``expires_in``: Token lifetime in seconds
* ``refresh_token``: Token for refreshing access
* ``scope``: Granted scopes
* ``user_guid``: User's unique identifier


Refresh Access Token
---------------------

Obtains a new access token using a refresh token.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.gam.clients import GAMClient

    client = GAMClient()
    
    new_token = client.refresh_access_token(
        client_id="your-app-client-id",
        client_secret="your-app-client-secret",
        refresh_token="existing-refresh-token"
    )
    
    access_token = new_token['access_token']
    print(f"New access token: {access_token}")

**Parameters:**

* ``client_id``: (Required) Application client ID
* ``client_secret``: (Required) Application client secret
* ``refresh_token``: (Required) Refresh token from previous response
* ``grant_type``: Must be "refresh_token" (default)

**Returns:**
Dictionary with new access token and refresh token.


Get User Information
--------------------

Retrieves authenticated user's information.

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.gam.clients import GAMClient

    client = GAMClient()
    
    user_info = client.get_user_info(
        access_token="user-access-token"
    )
    
    print(f"User GUID: {user_info['guid']}")
    print(f"Username: {user_info['username']}")
    print(f"Email: {user_info['email']}")

**Parameters:**

* ``access_token``: (Required) Valid access token

**Returns:**
Dictionary containing user details based on granted scopes.


Complete OAuth Flow Example
----------------------------

.. code-block:: python

    from pygeai.gam.clients import GAMClient
    import time

    client = GAMClient()

    # Step 1: Obtain access token
    token_response = client.get_access_token(
        client_id="app-client-id",
        client_secret="app-secret",
        username="user@example.com",
        password="password",
        scope="gam_user_data+gam_user_roles"
    )
    
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    expires_in = token_response['expires_in']
    
    print(f"Obtained access token (expires in {expires_in}s)")

    # Step 2: Get user information
    user_info = client.get_user_info(access_token=access_token)
    
    print(f"\nUser Information:")
    print(f"  GUID: {user_info['guid']}")
    print(f"  Username: {user_info['username']}")
    print(f"  Email: {user_info.get('email', 'N/A')}")

    # Step 3: Simulate token expiration and refresh
    print(f"\nWaiting for token to expire...")
    time.sleep(expires_in + 1)

    # Step 4: Refresh the access token
    new_token = client.refresh_access_token(
        client_id="app-client-id",
        client_secret="app-secret",
        refresh_token=refresh_token
    )
    
    access_token = new_token['access_token']
    print(f"Refreshed access token")


Best Practices
--------------

Token Security
~~~~~~~~~~~~~~

* Store tokens securely (encrypted storage, environment variables)
* Never log or expose tokens in code
* Use HTTPS for all OAuth communications
* Implement token rotation
* Clear tokens from memory after use

State Parameter
~~~~~~~~~~~~~~~

* Generate cryptographically random state values
* Store state in session for validation
* Validate state when user returns from authentication
* Prevents CSRF attacks

Token Lifecycle
~~~~~~~~~~~~~~~

* Monitor token expiration
* Refresh tokens proactively before expiration
* Implement token refresh logic in error handlers
* Handle refresh token expiration gracefully

Scopes
~~~~~~

* Request minimal required scopes
* Document why each scope is needed
* Handle scope changes gracefully
* Validate granted vs requested scopes


Security Considerations
-----------------------

CSRF Protection
~~~~~~~~~~~~~~~

Always use and validate the ``state`` parameter:

.. code-block:: python

    import secrets
    
    # Generate state
    state = secrets.token_urlsafe(32)
    # Store in session: session['oauth_state'] = state
    
    signin_url = client.generate_signing_url(
        client_id="...",
        redirect_uri="...",
        state=state
    )
    
    # On callback, validate:
    # if request.args.get('state') != session.get('oauth_state'):
    #     raise SecurityError("Invalid state parameter")

Password Grant Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Use password grant only for trusted applications
* Prefer authorization code flow for web applications
* Implement rate limiting on token requests
* Use strong password policies
* Consider multi-factor authentication

Token Storage
~~~~~~~~~~~~~

* Never store tokens in:
  
  * Client-side JavaScript
  * URL parameters
  * Logs
  * Version control

* Secure storage options:
  
  * Server-side session storage
  * Encrypted database fields
  * Secure key management systems


Error Handling
--------------

.. code-block:: python

    from pygeai.gam.clients import GAMClient
    from pygeai.core.common.exceptions import MissingRequirementException, APIError

    client = GAMClient()

    # Handle missing parameters
    try:
        url = client.generate_signing_url(
            client_id="id",
            # Missing redirect_uri and state
        )
    except MissingRequirementException as e:
        print(f"Missing required parameters: {e}")

    # Handle invalid credentials
    try:
        token = client.get_access_token(
            client_id="app-id",
            client_secret="secret",
            username="user",
            password="wrong-password"
        )
    except APIError as e:
        print(f"Authentication failed: {e}")

    # Handle expired refresh token
    try:
        new_token = client.refresh_access_token(
            client_id="app-id",
            client_secret="secret",
            refresh_token="expired-token"
        )
    except APIError as e:
        print("Refresh token expired, user must re-authenticate")


Integration with GEAI
---------------------

Using GAM tokens with GEAI services:

.. code-block:: python

    from pygeai.gam.clients import GAMClient
    from pygeai.assistant.managers import AssistantManager

    # Authenticate via GAM
    gam_client = GAMClient()
    token_response = gam_client.get_access_token(
        client_id="app-id",
        client_secret="secret",
        username="user@example.com",
        password="password"
    )
    
    access_token = token_response['access_token']
    
    # Use token with GEAI services
    # (Specific integration depends on service configuration)
    # Some services may accept GAM tokens for authentication


Notes
-----

* GAM OAuth follows the OAuth 2.0 specification
* Password grant is suitable for trusted applications only
* Refresh tokens have longer lifetimes than access tokens
* Token response may vary based on ``request_token_type``
* Multitenant deployments require ``repository`` parameter
* Custom user properties can be set via ``initial_properties``
