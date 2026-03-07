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

  Objective: Implement full authentication system with email/password,
  Google OAuth, and SAML SSO to enable secure user access.

  Context: Current app has no auth. Users need secure login before
  beta launch. Enterprise customers require SSO.

  Scope:
    Included: Login, registration, OAuth, SSO, password reset
    Not Included: User profile management, admin panel, 2FA (Phase 2)

  Success Criteria:
    - All auth flows functional end-to-end
    - Rate limiting active on login endpoints
    - SSO tested with at least one IdP

  Risks & Dependencies:
    - Email service (SendGrid/SES) for password reset
    - Google OAuth app credentials
    - SAML identity provider configuration

  Source: [Notion link]

  ---

  **Story 1:** Email/Password Authentication
    User Story: As a user, when I visit the login page, I want to
      register and sign in with email/password so that I can access
      the application securely.
    Context: Core auth flow — must be implemented first as other
      auth methods depend on the user account model.
    Acceptance Criteria:
    - Users can register with email and password
    - Users can log in with valid credentials
    - Failed logins are rate-limited (5 attempts / 15 min)
    - Passwords hashed with bcrypt
    Other Information:
    - Inputs: Email, password from registration/login form
    - Outputs: JWT access token, refresh token
    - Dependencies: None (standalone)

  **Story 2:** Google OAuth Integration
    User Story: As a user, when I'm on the login page, I want to
      sign in with my Google account so that I can access the app
      without creating a separate password.
    Context: Secondary auth method — requires user model from Story 1.
    Acceptance Criteria:
    - Users can sign in with Google account
    - New users auto-registered on first Google sign-in
    - Existing users can link Google account
    Other Information:
    - Inputs: Google OAuth callback
    - Outputs: Linked user account, JWT tokens
    - Dependencies: Story 1 (user account model), Google OAuth credentials

  **Story 3:** SAML SSO for Enterprise
    User Story: As an enterprise admin, when I configure my identity
      provider, I want SAML-based SSO so that my team can use
      existing corporate credentials.
    Context: Enterprise feature — can be developed in parallel with Story 2.
    Acceptance Criteria:
    - Admin can configure SAML identity provider
    - Users redirected to IdP for authentication
    - SAML assertions validated and mapped to user accounts
    Other Information:
    - Inputs: SAML assertion from IdP
    - Outputs: Authenticated user session
    - Dependencies: Story 1, SAML IdP configuration

  **Story 4:** Password Reset Flow
    User Story: As a user, when I forget my password, I want to
      reset it via email so that I can regain access to my account.
    Context: Recovery flow — depends on email service integration.
    Acceptance Criteria:
    - Users can request password reset via email
    - Reset tokens expire after 1 hour
    - Users can set new password via reset link
    Other Information:
    - Inputs: User email address
    - Outputs: Reset email sent, password updated
    - Dependencies: Story 1, Email service (SendGrid/SES)

  **Story 5:** Session Management
    User Story: As a user, when I'm authenticated, I want my session
      to persist securely so that I don't have to log in repeatedly.
    Context: Cross-cutting concern — all auth methods produce sessions.
    Acceptance Criteria:
    - Access tokens issued on login (15 min expiry)
    - Refresh tokens for silent re-authentication (7 day expiry)
    - Users can sign out (invalidate tokens)
    Other Information:
    - Inputs: Authenticated user from any auth method
    - Outputs: JWT access + refresh tokens
    - Dependencies: Story 1

  **Task 1:** Set up Notion-to-Jira spec parsing pipeline
    Summary: Read specifications from Notion via MCP, extract
      requirements, and create structured tickets in Jira with
      a two-checkpoint approval process.
    Context: Core infrastructure task — enables the entire
      spec-to-tickets workflow. Standalone, no Kioku dependency for v1.
    Acceptance Criteria:
    - Correctly parses spec into logical stories with clear titles
      and descriptions
    - Detects and flags overlap with existing Jira tickets
    - Two-checkpoint approval: proposed structure + before creation
    - Created tickets have proper epic links and labels
    - All created tickets indexed in Kioku with spec relationship
    Other Information:
    - Inputs: Notion page URL or ID, target Jira project key
    - Outputs: Created Jira epic + stories, confirmation summary
    - Dependencies: Standalone — can start immediately
    - Spec: [Notion Spec link]

  **Bug 1:** Dashboard sync delayed by hours, shows stale screenshots
    Impact: Sync delay and manual sync issues cause outdated screenshots
      and status updates, leading to inaccurate productivity reporting
      and onboarding evaluation.
    Expected Behaviour: Automatic sync every 10–15 minutes. Manual sync
      immediately captures fresh screenshot and updates status/activity bar.
    Actual Behaviour: Sync delayed by hours or does not update even when
      manually triggered. Dashboard shows stale data.
    Steps to Reproduce:
    1. Use the Ajira desktop app/agent (logged in as affected user)
    2. Observe dashboard for time tracking with periodic screenshots
    3. Notice activity sheet/timeline does not sync automatically
    4. Trigger manual sync via the sync button
    5. Check if same screenshot and status appear without new updates
    6. Wait 30–60+ minutes or restart app to confirm persistence
    Environment: Ajira desktop app/agent
    Workarounds: N/A
    Other Information:
    - Affected time slots show repeated identical titles
    - Multiple 10-minute blocks display identical screen captures
    - Activity percentages vary but visual content does not refresh
    - Issue occurs intermittently

Create these tickets? Any changes needed?
```
