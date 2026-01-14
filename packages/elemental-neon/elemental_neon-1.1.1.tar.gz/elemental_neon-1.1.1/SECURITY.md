# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in elemental-neon, please report it by emailing:

**marco.z.difraia@gmail.com**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to expect

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix timeline**: Depends on severity
  - Critical: Within 7 days
  - High: Within 14 days
  - Medium: Within 30 days
  - Low: Next minor release

### Disclosure Policy

- Please allow us time to fix the issue before public disclosure
- We will credit you in the release notes unless you prefer to remain anonymous
- We will coordinate the disclosure timeline with you

## Security Considerations

Neon is a mathematical library for floating-point arithmetic. Key security considerations:

1. **Input Validation**: All inputs are validated for NaN and infinity
2. **No External Dependencies**: Zero-dependency design reduces attack surface
3. **Pure Functions**: No state means no state-based vulnerabilities
4. **Type Safety**: Strict type checking with mypy

### Known Limitations

- Neon uses Python's standard `float` (IEEE 754 double precision)
- Not suitable for cryptographic operations
- Not suitable for applications requiring guaranteed decimal precision (use `decimal.Decimal`)

## Security Best Practices

When using neon:
- Validate user inputs before passing to neon functions
- Use appropriate tolerances for your use case
- Consider catastrophic cancellation for financial calculations
- Test edge cases in your application

Thank you for helping keep neon secure!
