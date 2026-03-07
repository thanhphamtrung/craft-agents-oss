# Example Outputs

## Checkpoint 1 — Spec Review

```
## Spec Review

**Title:** User Authentication & SSO Integration
**Features/Requirements:**
1. Email/password login with rate limiting
2. Google OAuth integration
3. SAML SSO for enterprise customers
4. Password reset via email
5. Session management with JWT + refresh tokens

**Scope:**
- Included: Login, registration, OAuth, SSO, password reset
- Excluded: User profile management, admin panel, 2FA (Phase 2)

**Ambiguities:**
- No acceptance criteria for session timeout duration
- SAML provider list not specified
- Rate limiting thresholds undefined

**Dependencies:**
- Email service (SendGrid/SES) for password reset
- Google OAuth app credentials
- SAML identity provider configuration

Is this interpretation correct? Anything to add, remove, or clarify?
```

## Checkpoint 2 — Ticket Proposal

```
## Ticket Proposal

**Epic:** User Authentication & SSO Integration
  Description: Implement full authentication system including email/password,
  Google OAuth, and SAML SSO. Source: [Notion link]

  **Story 1:** Email/Password Authentication
    Description: Implement email/password login and registration
    Acceptance Criteria:
    - Users can register with email and password
    - Users can log in with valid credentials
    - Failed logins are rate-limited (5 attempts / 15 min)
    - Passwords hashed with bcrypt

  **Story 2:** Google OAuth Integration
    Description: Add Google sign-in as authentication option
    Acceptance Criteria:
    - Users can sign in with Google account
    - New users auto-registered on first Google sign-in
    - Existing users can link Google account

  **Story 3:** SAML SSO for Enterprise
    Description: Implement SAML-based SSO for enterprise customers
    Acceptance Criteria:
    - Admin can configure SAML identity provider
    - Users redirected to IdP for authentication
    - SAML assertions validated and mapped to user accounts

  **Story 4:** Password Reset Flow
    Description: Email-based password reset functionality
    Acceptance Criteria:
    - Users can request password reset via email
    - Reset tokens expire after 1 hour
    - Users can set new password via reset link

  **Story 5:** Session Management
    Description: JWT-based session management with refresh tokens
    Acceptance Criteria:
    - Access tokens issued on login (15 min expiry)
    - Refresh tokens for silent re-authentication (7 day expiry)
    - Users can sign out (invalidate tokens)

Create these tickets? Any changes needed?
```
