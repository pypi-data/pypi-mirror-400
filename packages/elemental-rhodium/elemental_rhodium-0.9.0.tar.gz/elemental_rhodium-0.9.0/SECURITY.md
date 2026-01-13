# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.9.x   | :white_check_mark: |
| < 0.9   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in Rhodium, please report it privately:

**Email:** marco.z.difraia@gmail.com

**Subject:** `[SECURITY] Rhodium - <brief description>`

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to expect

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 7 days
- **Fix timeline:** Depends on severity (critical issues within 14 days)
- **Public disclosure:** After fix is released and users have had time to upgrade

### What qualifies as a security issue?

For Rhodium (a mathematical library), security issues include:

1. **Input validation bypass:**
   - Crafted NaN/Infinity inputs that bypass validation
   - Inputs that cause crashes or hangs

2. **Numerical stability issues:**
   - Inputs that produce incorrect results due to floating-point errors
   - Inputs that cause infinite loops or excessive computation

3. **Denial of Service (DoS):**
   - Inputs that cause excessive memory allocation
   - Algorithmic complexity attacks

4. **Dependency vulnerabilities:**
   - Security issues in test/build dependencies (though Rhodium has zero runtime dependencies)

### What is NOT a security issue?

- Feature requests
- Bugs that don't have security implications
- Mathematical precision limits (documented limitation)
- Performance issues without DoS implications

## Security Best Practices for Users

When using Rhodium in security-sensitive applications:

1. **Validate inputs:** Always validate user-provided coordinates before passing to Rhodium
2. **Handle exceptions:** Catch and handle `RhodiumError` and its subclasses
3. **Rate limiting:** If processing user-provided coordinates, implement rate limiting
4. **Resource limits:** Set timeouts and memory limits for bulk processing
5. **Audit usage:** Log when invalid inputs are rejected

## Known Limitations

Rhodium is a mathematical library with these documented limitations:

- **Floating-point precision:** Subject to standard IEEE 754 floating-point limitations
- **No cryptographic guarantees:** Not designed for cryptographic applications
- **No sandboxing:** Runs in the same process as your application

## Security Update Policy

- Critical security fixes: Released immediately as patch versions
- High severity: Released within 14 days
- Medium/Low severity: Batched into next minor/patch release
- Security fixes will be backported to supported versions only
