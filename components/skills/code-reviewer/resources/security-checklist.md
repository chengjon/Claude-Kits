# Security Review Checklist

Comprehensive security guidelines for code review. Use this checklist to perform thorough security audits.

## OWASP Top 10 Coverage

### 1. Injection Attacks

#### SQL Injection
**What to Look For**:
- String concatenation in SQL queries
- User input directly in queries
- Dynamic query construction

**Bad**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
query = "SELECT * FROM users WHERE name = '" + user_name + "'"
```

**Good**:
```python
# Parameterized queries
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))

# ORM (preferred)
User.objects.filter(id=user_id)
```

#### Command Injection
**What to Look For**:
- `os.system()`, `subprocess.call()` with user input
- Shell=True with user-controlled strings
- Unvalidated file paths

**Bad**:
```python
os.system(f"ping {user_input}")
subprocess.run(f"ls {directory}", shell=True)
```

**Good**:
```python
# Use argument list, not shell
subprocess.run(["ping", validated_host], shell=False)

# Validate and sanitize
import shlex
safe_input = shlex.quote(user_input)
```

#### LDAP/NoSQL Injection
Check for:
- Unescaped LDAP filters
- MongoDB $where operator with user input
- Elasticsearch query string injection

### 2. Broken Authentication

**Critical Checks**:
- [ ] Passwords hashed with strong algorithm (bcrypt, Argon2)
- [ ] No plaintext passwords in database
- [ ] Session tokens are cryptographically random
- [ ] Session timeout implemented
- [ ] Multi-factor authentication available
- [ ] Password reset tokens are single-use
- [ ] Account lockout after failed attempts
- [ ] No default credentials

**Examples**:
```python
# Bad: Weak hashing
password_hash = hashlib.md5(password.encode()).hexdigest()

# Good: Strong hashing
from bcrypt import hashpw, gensalt
password_hash = hashpw(password.encode(), gensalt(rounds=12))
```

### 3. Sensitive Data Exposure

**What to Check**:
- [ ] HTTPS everywhere (no HTTP)
- [ ] Sensitive data encrypted at rest
- [ ] No sensitive data in logs
- [ ] No sensitive data in URLs
- [ ] Database connections encrypted (TLS)
- [ ] API keys not in source code
- [ ] Environment variables for secrets
- [ ] Secure key management (e.g., AWS KMS)

**Common Mistakes**:
```python
# Bad
API_KEY = "sk_live_abc123..."  # In source code
logger.info(f"User password: {password}")  # In logs
url = f"/reset?token={reset_token}"  # In URL

# Good
API_KEY = os.environ['API_KEY']  # From environment
logger.info(f"User logged in: {user.id}")  # No sensitive data
# Send token in POST body or Authorization header
```

### 4. XML External Entities (XXE)

**Check**:
- [ ] XML parsing with safe configuration
- [ ] DTD processing disabled
- [ ] External entity resolution disabled

```python
# Bad
import xml.etree.ElementTree as ET
tree = ET.parse(user_file)  # Vulnerable

# Good
import defusedxml.ElementTree as ET
tree = ET.parse(user_file)  # Protected
```

### 5. Broken Access Control

**Verification Points**:
- [ ] Authorization checked on every sensitive operation
- [ ] IDOR vulnerabilities prevented
- [ ] Horizontal privilege escalation prevented
- [ ] Vertical privilege escalation prevented
- [ ] API rate limiting implemented

**IDOR Example**:
```python
# Bad: No ownership check
@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    return User.get(user_id).to_json()

# Good: Verify ownership
@app.route('/user/<user_id>/profile')
@login_required
def get_profile(user_id):
    if current_user.id != int(user_id) and not current_user.is_admin:
        abort(403)
    return User.get(user_id).to_json()
```

### 6. Security Misconfiguration

**Review**:
- [ ] No default passwords
- [ ] Debug mode disabled in production
- [ ] Error messages don't leak info
- [ ] Security headers configured
- [ ] Unnecessary features disabled
- [ ] Software up to date

**Security Headers**:
```python
# Add these headers
response.headers['X-Content-Type-Options'] = 'nosniff'
response.headers['X-Frame-Options'] = 'DENY'
response.headers['X-XSS-Protection'] = '1; mode=block'
response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
response.headers['Content-Security-Policy'] = "default-src 'self'"
```

### 7. Cross-Site Scripting (XSS)

**Types to Check**:
1. **Reflected XSS**: User input immediately returned
2. **Stored XSS**: User input saved and displayed
3. **DOM-based XSS**: Client-side JS vulnerability

**Prevention**:
```python
# Bad: No escaping
html = f"<div>Welcome {user_name}</div>"

# Good: Use template engine with auto-escaping
from jinja2 import Template
template = Template("<div>Welcome {{ user_name }}</div>")
html = template.render(user_name=user_name)

# JavaScript
// Bad
element.innerHTML = user_input;

// Good
element.textContent = user_input;  // Auto-escaped
// Or use DOMPurify for HTML
element.innerHTML = DOMPurify.sanitize(user_input);
```

### 8. Insecure Deserialization

**Red Flags**:
- Pickle, marshal, YAML load with untrusted data
- Java serialization of user input
- eval() with user data

```python
# Bad: Unsafe deserialization
import pickle
data = pickle.loads(request.data)  # Dangerous!

# Good: Use safe formats
import json
data = json.loads(request.data)  # Safe

# If you must use YAML
import yaml
data = yaml.safe_load(request.data)  # Use safe_load!
```

### 9. Using Components with Known Vulnerabilities

**Checks**:
- [ ] Dependencies listed and versioned
- [ ] Regular dependency updates
- [ ] Vulnerability scanning (npm audit, pip-audit, Snyk)
- [ ] No deprecated packages
- [ ] Minimal dependencies

**Tools**:
```bash
# Python
pip-audit
safety check

# Node.js
npm audit
yarn audit

# General
snyk test
```

### 10. Insufficient Logging & Monitoring

**Must Log**:
- [ ] Authentication attempts (success/failure)
- [ ] Authorization failures
- [ ] Input validation failures
- [ ] Security-relevant configuration changes
- [ ] Suspicious activity patterns

**Don't Log**:
- ❌ Passwords (even hashed)
- ❌ Session tokens
- ❌ Credit card numbers
- ❌ API keys
- ❌ PII without consent

```python
# Good logging
logger.info(f"Login attempt for user: {username}")
logger.warning(f"Failed login for user: {username}, IP: {ip}")
logger.error(f"Authorization failed: {user_id} tried to access {resource}")

# Bad logging
logger.info(f"Login: {username}:{password}")  # NO!
```

## Additional Security Checks

### Cryptography
- [ ] Use TLS 1.2 or higher
- [ ] Use strong cipher suites only
- [ ] Random number generation is cryptographically secure
- [ ] Don't implement your own crypto
- [ ] Use established libraries (libsodium, cryptography.io)

```python
# Bad: Not cryptographically secure
import random
token = random.randint(1000, 9999)

# Good: Cryptographically secure
import secrets
token = secrets.token_urlsafe(32)
```

### File Upload Security
- [ ] File type validation (magic numbers, not extensions)
- [ ] File size limits
- [ ] Files stored outside webroot
- [ ] Virus scanning for uploads
- [ ] Generate new filenames (don't trust user input)

```python
# Bad
filename = request.files['upload'].filename
path = f"/var/www/uploads/{filename}"  # Path traversal risk!

# Good
import uuid
from werkzeug.utils import secure_filename

file = request.files['upload']
# Validate content type
if file.content_type not in ['image/jpeg', 'image/png']:
    abort(400)

# Generate safe filename
ext = secure_filename(file.filename).rsplit('.', 1)[1]
filename = f"{uuid.uuid4()}.{ext}"
path = os.path.join(UPLOAD_FOLDER, filename)
```

### API Security
- [ ] Rate limiting per user/IP
- [ ] API authentication required
- [ ] API versioning
- [ ] Input validation
- [ ] CORS properly configured
- [ ] No CSRF for state-changing operations

### Session Management
- [ ] Secure flag on cookies
- [ ] HttpOnly flag on session cookies
- [ ] SameSite attribute set
- [ ] Session regeneration after login
- [ ] Logout invalidates session

```python
response.set_cookie(
    'session_id',
    session_token,
    secure=True,      # HTTPS only
    httponly=True,    # Not accessible to JavaScript
    samesite='Strict' # CSRF protection
)
```

## Security Testing Checklist

Before approving code:
- [ ] Run static analysis (bandit, semgrep)
- [ ] Dependency vulnerability scan
- [ ] Manual code review focusing on security
- [ ] Penetration testing for critical features
- [ ] Security headers verified
- [ ] Authentication/authorization tested
- [ ] Input validation tested with malicious inputs

## Quick Reference: Secure Coding Patterns

### Input Validation
```python
def validate_email(email):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Invalid email")
    return email.lower()
```

### Output Encoding
```python
from html import escape
safe_html = escape(user_input)
```

### Safe File Operations
```python
from pathlib import Path

def safe_path(base_dir, user_path):
    base = Path(base_dir).resolve()
    target = (base / user_path).resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Path traversal detected")
    return target
```

### Secure Password Reset
```python
import secrets
from datetime import datetime, timedelta

reset_token = secrets.token_urlsafe(32)
expiry = datetime.utcnow() + timedelta(hours=1)

# Store hashed token
store_reset_token(user.id, hash(reset_token), expiry)

# Send token once via email
send_email(user.email, f"Reset: {reset_token}")

# On use: invalidate token immediately
```

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- CWE Top 25: https://cwe.mitre.org/top25/
- NIST Guidelines: https://csrc.nist.gov/publications/
