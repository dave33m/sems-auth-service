# Sems Auth Service (SAS)

Sems Auth Service (SAS) is a multi-tenant authentication and authorization service designed to be used across multiple products, platforms, and programming languages.

It provides:

* OAuth-style **Client Credentials** flow for systems
* Secure **User Authentication** with JWT sessions
* **OTP-based flows** for login and password reset
* Multi-tenant user isolation (same email can exist across different clients)
* Refresh tokens
* Centralized identity for all your apps

SAS is built with Django + Django REST Framework and is intended to act as your **single source of truth for identity**.

---

## Core Concepts

### 1. Clients (Systems)

Every consuming system (e.g. `FlavourAtlas`, `SemsTunez`) is registered as a **Client**.

Each client has:

* `client_id`
* `client_secret`

Clients authenticate using:

```json
POST /auth/oauth/token

{
  "client_id": "FlavourAtlas_API",
  "client_secret": "xxxxx",
  "grant_type": "client_credentials"
}
```

This returns a **Client Bearer Token**.

This token is used to:

* Register users
* Initiate login
* Trigger OTP flows

---

### 2. Users (Per Client)

Users belong to a specific client.
The same email can exist across multiple clients:

```
bill@yopmail.com @ FlavourAtlas
bill@yopmail.com @ SemsTunez
```

There is no conflict because identity is scoped by:

```
(email, client)
```

---

### 3. Two-Step Login (2FA)

Login is OTP-based:

1. Client calls `/auth/login` with user credentials
2. SAS sends an OTP to the user
3. Client calls `/auth/verify-otp`
4. SAS returns a **User Bearer Token**

This token is used for all authenticated user actions.

---

## Using SAS with Postman

Swagger UI is provided for discovery, but **Postman is the recommended tool** for real usage and testing.

### Import the API

1. Open Postman
2. Click **Import**
3. Choose **Link** or **File**
4. Use the OpenAPI schema from production:

   ```
   https://<your-domain>/swagger.json
   ```

   or download and import it as a file.

Postman will generate a full collection.

### Suggested Postman Environment

Create an environment with:

| Variable       | Value                                      |
| -------------- | ------------------------------------------ |
| `base_url`     | `https://sems-auth-service.up.railway.app` |
| `client_token` | (set after OAuth)                          |
| `user_token`   | (set after login)                          |

Use in headers:

```
Authorization: Bearer {{client_token}}
```

or

```
Authorization: Bearer {{user_token}}
```

This mirrors real production usage.

---

## Typical Flow

1. Create a Client (admin-only)
2. Obtain Client Token via `/auth/oauth/token`
3. Register User
4. Login User → OTP sent
5. Verify OTP → User Token issued
6. Use User Token for protected endpoints
7. Forgot Password → OTP → Reset Password

---

## Environment Setup

SAS uses a single environment variable for DB configuration:

```
DATABASE_URL=postgres://user:pass@host:port/dbname
```

Locally and in production, the same configuration is used.

---

## Why SAS?

* Centralized identity across all your products
* Language-agnostic (HTTP + JWT)
* Secure by default
* Multi-tenant
* Production-ready

SAS is infrastructure, not a demo app.
