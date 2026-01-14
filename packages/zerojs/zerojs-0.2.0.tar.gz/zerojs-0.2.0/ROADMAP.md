# ZeroJS Roadmap

Technical roadmap for ZeroJS framework development.

## Phase 1: Security Essentials

**Goal:** Make ZeroJS safe for production use.

- [x] **CSRF Protection**
  - CSRF token generation and validation
  - Auto-inject tokens in `render_form()`
  - `{% csrf_token %}` template tag
  - Configurable exempt routes

- [x] **Security Headers Middleware**
  - Content-Security-Policy
  - X-Frame-Options
  - X-Content-Type-Options
  - Strict-Transport-Security
  - Configurable per-route

- [x] **Rate Limiting**
  - Request throttling middleware
  - Configurable limits per route/IP
  - Custom rate limit exceeded response

- [x] **Input Validation**
  - URL parameter validation via type hints
  - Query parameter validation
  - Path traversal protection (security by default, `UnsafeStr`/`UnsafePath` opt-out)

## Phase 2: Authentication & Authorization

**Goal:** Provide built-in auth primitives.

- [ ] **Session Management**
  - Secure cookie-based sessions
  - Session storage backends (memory, file, Redis)
  - Session expiration and renewal

- [ ] **Authentication Middleware**
  - `@login_required` decorator
  - `current_user` context variable
  - Login/logout helpers

- [ ] **Authorization**
  - Role-based access control
  - `@requires_role("admin")` decorator
  - Permission checking in templates

## Phase 3: Production Readiness

**Goal:** Enable reliable production deployments.

- [ ] **Structured Logging**
  - JSON log format
  - Request ID tracking
  - Configurable log levels
  - Request/response logging

- [ ] **Health Checks**
  - `GET /health` endpoint
  - `GET /ready` endpoint
  - Custom health check functions

- [ ] **Metrics & Observability**
  - Prometheus metrics endpoint
  - Request duration histograms
  - Error rate counters
  - OpenTelemetry integration

- [ ] **Graceful Shutdown**
  - Shutdown hooks
  - Connection draining
  - Background task completion

- [ ] **Environment Configuration**
  - Environment variable support
  - `.env` file loading
  - Profile-based config (dev/staging/prod)

## Phase 4: Developer Experience

**Goal:** Improve development workflow.

- [ ] **CLI Tool**
  - `zerojs new <project>` - scaffolding
  - `zerojs dev` - development server
  - `zerojs routes` - list all routes
  - `zerojs check` - validate project structure

- [ ] **Debug Mode**
  - Detailed error pages with stack traces
  - Request/response inspector
  - Template debugging

- [ ] **Testing Utilities**
  - `ZeroJSTestClient` with helpers
  - Form submission helpers
  - HTMX request simulation

- [ ] **Type Checking Support**
  - Add `py.typed` marker
  - Type stubs for public API

## Phase 5: Extended Features

**Goal:** Add commonly needed functionality.

- [ ] **File Uploads**
  - Multipart file handling
  - File validation (size, type)
  - Storage backends (local, S3)

- [ ] **WebSocket Support**
  - WebSocket routes
  - HTMX WebSocket extension integration
  - Broadcast helpers

- [ ] **Background Tasks**
  - Task queue integration
  - Scheduled tasks
  - Task status tracking

- [ ] **Internationalization (i18n)**
  - Translation loading
  - `{% trans %}` template tag
  - Locale detection
  - Date/number formatting

- [ ] **Database Helpers**
  - SQLAlchemy integration guide
  - Migration patterns
  - Connection lifecycle management

## Phase 6: Performance & Scale

**Goal:** Optimize for high-traffic applications.

- [ ] **Advanced Caching**
  - Redis cache backend
  - Cache tags for invalidation
  - Fragment caching

- [ ] **Asset Pipeline**
  - CSS/JS bundling
  - Minification
  - Cache busting

- [ ] **Response Compression**
  - Gzip/Brotli middleware
  - Configurable thresholds

---

## Current Status

### Implemented
- File-based routing with dynamic parameters
- Jinja2 templating with inheritance
- HTMX integration with `hx-boost`
- Partial rendering via `HX-Target`
- Pydantic form validation
- `render_form()` automatic form generation
- Shadow DOM components (`.shadow.html`)
- HTML caching (none/ttl/incremental)
- PyScript support
- Custom error pages
- Hot reload development server
- 97+ tests

### Version Targets

| Version | Phase | Focus |
|---------|-------|-------|
| 0.2.0 | 1 | Security Essentials |
| 0.3.0 | 2 | Authentication |
| 0.4.0 | 3 | Production Readiness |
| 0.5.0 | 4 | Developer Experience |
| 1.0.0 | 5-6 | Feature Complete |

---

## Contributing

Contributions are welcome! Pick an item from the roadmap and open a PR.

Priority items are marked in Phase 1 (Security) - these are blocking production use.
