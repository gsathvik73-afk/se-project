# Security review

Bandit scans smartexpense with no blanket excluded tests. B105 flags the literal assigned to the password validation-error field as a possible hardcoded password. That literal is the public message `Use at least 8 characters and no more than 72 UTF-8 bytes.`, not a credential. A single `nosec B105` annotation documents that reviewed false positive; all other checks stay enabled. Passwords remain salted bcrypt hashes. Do not describe the scan as a complete penetration test.

Executable checks cover cross-user records and categories, parameterized query behavior, inert stored text, CSRF, logout replay, password limits, persistent lockout, failure rollback and CSV formula safety. Source and test details remain inspectable. Public HTTPS and host-file encryption are separate deployment responsibilities.
