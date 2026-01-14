# Service Users and External Authentication

## Service Users (Software Only)
Dremio Software allows creating "Service Users" (identityType: `SERVICE_USER`) which do not require a password and are typically used for automation via Personal Access Tokens (PATs).

### Creating a Service User
```bash
dremio user create --username svc_pipeline --type SERVICE
```

You can then log in as an admin (or user with privileges) to generate a PAT for this user via the API or UI.

### Creating a Local User (Default)
```bash
dremio user create --username john --password secret --name "John Doe" --email john@example.com
```

## External JWT Authentication (Cloud & Software)
For environments integrating with external Identity Providers (IdP) like Okta or Microsoft Entra ID, you can configure your profile to use an **External JWT**. The CLI will automatically exchange this token for a Dremio Access Token via the `/oauth/token` endpoint (Token Exchange).

### 1. Get your External JWT
Obtain a valid JWT from your Identity Provider. This token must be valid and trusted by your Dremio instance.

### 2. Configure Profile
Use the `external_jwt` auth type and provide your IdP token.

```bash
dremio profile create --name my-idp-profile \
  --type cloud \
  --base-url https://api.dremio.cloud \
  --project-id <PROJECT_ID> \
  --auth-type external_jwt \
  --token <YOUR_IDP_JWT>
```

### 3. Usage
The CLI will exchange the provided External JWT for a temporary Dremio Access Token for each session or command.
> [!NOTE]
> The CLI does not refresh the *External* JWT. If your IdP token expires, you must update the profile with a new one using `dremio profile update`.
