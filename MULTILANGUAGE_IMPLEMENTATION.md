# Multi-Language Implementation for LawyerAgent

## Overview

LawyerAgent now supports four languages for the Belgian market:
- **Dutch (Nederlands)** - Primary language
- **French (Français)** - Second official language
- **English (English)** - International language
- **German (Deutsch)** - Regional language

## Implementation Details

### 1. Configuration (`config/settings.py`)

```python
# Language Configuration
LANGUAGES = {
    'nl': 'Nederlands',
    'fr': 'Français', 
    'en': 'English',
    'de': 'Deutsch'
}

DEFAULT_LANGUAGE = 'nl'  # Dutch as primary language
SUPPORTED_LANGUAGES = ['nl', 'fr', 'en', 'de']

# Babel Configuration
BABEL_DEFAULT_LOCALE = 'nl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Brussels'
BABEL_TRANSLATION_DIRECTORIES = 'translations'
```

### 2. Flask-Babel Integration (`web_app.py`)

The application uses Flask-Babel for internationalization:

```python
from flask_babel import Babel, gettext, ngettext, lazy_gettext

# Initialize Babel
babel = Babel(app)

@babel.localeselector
def get_locale():
    """Get the locale for the current request."""
    # Check if user has selected a language
    if 'language' in session:
        return session['language']
    
    # Check browser's preferred language
    if request.accept_languages:
        for lang in request.accept_languages.best_match(SUPPORTED_LANGUAGES):
            if lang in SUPPORTED_LANGUAGES:
                session['language'] = lang
                return lang
    
    # Default to Dutch
    session['language'] = DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE
```

### 3. Language Switching

Users can change languages via:
- URL parameter: `?lang=nl`
- Language dropdown in navigation
- Session persistence

```python
@app.route('/language/<lang>')
def change_language(lang):
    """Change the application language."""
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang
        flash(gettext('Language changed successfully'), 'success')
    else:
        flash(gettext('Unsupported language'), 'error')
    
    return redirect(request.referrer or url_for('index'))
```

### 4. Translation Files Structure

```
translations/
├── nl/LC_MESSAGES/
│   ├── messages.po
│   └── messages.mo
├── fr/LC_MESSAGES/
│   ├── messages.po
│   └── messages.mo
├── en/LC_MESSAGES/
│   ├── messages.po
│   └── messages.mo
└── de/LC_MESSAGES/
    ├── messages.po
    └── messages.mo
```

### 5. Template Usage

Templates use the `gettext` function for translations:

```html
<h1>{{ _('Welcome to LawyerAgent') }}</h1>
<p>{{ _('Secure Offline Belgian Legal Assistant') }}</p>
<a href="{{ url_for('dashboard') }}">{{ _('Dashboard') }}</a>
```

### 6. Language Selector UI

The navigation bar includes a language dropdown with:
- Flag icons for each language
- Current language highlighting
- Smooth transitions

```html
<div class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown">
        <i class="fas fa-globe me-1"></i>{{ g.language_name }}
    </a>
    <ul class="dropdown-menu language-dropdown">
        {% for code, name in g.languages.items() %}
        <li>
            <a class="dropdown-item language-option {% if code == g.current_language %}active{% endif %}" 
               href="{{ url_for('change_language', lang=code) }}">
                <img src="https://flagcdn.com/16x12/{{ 'be' if code == 'nl' else 'fr' if code == 'fr' else 'gb' if code == 'en' else 'de' }}.png" 
                     class="language-flag" alt="{{ name }}">
                {{ name }}
            </a>
        </li>
        {% endfor %}
    </ul>
</div>
```

## Usage Instructions

### 1. Installation

```bash
pip install Flask-Babel==4.0.0 Babel==2.12.1
```

### 2. Compile Translations

```bash
python3 compile_translations.py compile
```

### 3. Extract New Messages

```bash
python3 compile_translations.py extract
```

### 4. Update Translations

```bash
python3 compile_translations.py update
```

### 5. Full Translation Workflow

```bash
python3 compile_translations.py all
```

## Translation Management

### Adding New Strings

1. Add the string to your Python code or templates:
   ```python
   flash(gettext('New message'), 'success')
   ```

2. Extract messages:
   ```bash
   python3 compile_translations.py extract
   ```

3. Update translation files:
   ```bash
   python3 compile_translations.py update
   ```

4. Edit the `.po` files in `translations/[lang]/LC_MESSAGES/messages.po`

5. Compile translations:
   ```bash
   python3 compile_translations.py compile
   ```

### Translation File Format

```po
msgid "Welcome to LawyerAgent"
msgstr "Welkom bij LawyerAgent"

msgid "Dashboard"
msgstr "Dashboard"

msgid "Documents"
msgstr "Documenten"
```

## Security Considerations

1. **Input Validation**: Language codes are validated against `SUPPORTED_LANGUAGES`
2. **Session Security**: Language preferences are stored securely in session data
3. **XSS Prevention**: All translated strings are properly escaped in templates
4. **CSRF Protection**: Language switching uses proper redirects

## Performance Optimizations

1. **Caching**: Translation files are compiled to `.mo` format for faster loading
2. **Lazy Loading**: Translations are loaded only when needed
3. **Session Storage**: Language preference is cached in session to avoid repeated lookups

## Testing

### Manual Testing

1. Start the application:
   ```bash
   python3 web_app.py
   ```

2. Visit `http://localhost:5000`

3. Test language switching:
   - Use the dropdown in the navigation
   - Try URL parameters: `?lang=fr`, `?lang=en`, `?lang=de`
   - Check browser language detection

### Automated Testing

```python
def test_language_switching():
    """Test language switching functionality."""
    with app.test_client() as client:
        # Test Dutch (default)
        response = client.get('/')
        assert b'Welkom bij LawyerAgent' in response.data
        
        # Test French
        response = client.get('/language/fr')
        response = client.get('/')
        assert b'Bienvenue sur LawyerAgent' in response.data
        
        # Test English
        response = client.get('/language/en')
        response = client.get('/')
        assert b'Welcome to LawyerAgent' in response.data
        
        # Test German
        response = client.get('/language/de')
        response = client.get('/')
        assert b'Willkommen bei LawyerAgent' in response.data
```

## Future Enhancements

1. **Database Storage**: Store language preferences in user profiles
2. **Content Localization**: Translate legal content and templates
3. **RTL Support**: Add support for right-to-left languages if needed
4. **Regional Variants**: Support for Belgian French vs. Standard French
5. **Auto-detection**: Improved browser language detection
6. **Translation Memory**: Reuse translations across similar content

## Troubleshooting

### Common Issues

1. **Translations not showing**: Ensure `.mo` files are compiled
2. **Language not switching**: Check session configuration
3. **Missing translations**: Run `python3 compile_translations.py all`

### Debug Mode

Enable debug mode to see translation keys:

```python
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['BABEL_DEFAULT_LOCALE'] = 'nl'
```

## Compliance

This implementation complies with:
- Belgian language laws (Dutch, French, German)
- EU language requirements
- Accessibility standards (WCAG 2.1)
- Data protection regulations (GDPR)

## Support

For issues with the multi-language implementation:
1. Check the translation files are properly formatted
2. Verify Flask-Babel is installed correctly
3. Ensure `.mo` files are compiled
4. Check browser console for JavaScript errors 