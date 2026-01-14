# ZeroJS Example

A demo application showcasing ZeroJS features.

## Run

```bash
cd example
python main.py
```

Visit http://localhost:3000

## Structure

```
example/
├── main.py                 # App entry point
├── settings.py             # Cache and PyScript configuration
├── pages/
│   ├── index.html          # Home page (/)
│   ├── about.html          # About page (/about)
│   ├── counter.html        # PyScript counter demo (/counter)
│   └── users/
│       ├── [id].html       # User profile (/users/{id})
│       └── _id.py          # User handlers (GET, POST)
├── components/
│   ├── base.html           # Base template
│   ├── header.html         # Navigation header
│   ├── footer.html         # Page footer
│   ├── user_card.html      # User info card
│   ├── user_form.html      # Edit form with HTMX
│   └── badge.shadow.html   # Shadow DOM component (encapsulated)
├── static/
│   ├── css/style.css       # Styles
│   ├── js/main.js          # JavaScript
│   └── py/counter.py       # Client-side Python (PyScript)
└── errors/
    ├── 404.html            # Not found page
    └── 500.html            # Server error page
```

## Features Demonstrated

- **File-based routing** - `pages/` structure maps to URLs
- **Dynamic routes** - `[id].html` captures URL parameters
- **Handlers** - `_id.py` with `get()` and `post()` functions
- **Form validation** - Pydantic model with custom error messages
- **HTMX forms** - Partial updates without page reload
- **Template inheritance** - `{% extends 'base.html' %}`
- **Components** - Reusable templates with `{% include %}`
- **Static files** - CSS and JS served from `/static/`
- **Error pages** - Custom 404 and 500 pages
- **Caching** - Per-route HTML response caching with TTL and incremental (ISR) strategies via `settings.py`
- **PyScript** - Client-side Python with MicroPython running in the browser
- **Shadow Components** - Encapsulated components with `.shadow.html` using Declarative Shadow DOM
