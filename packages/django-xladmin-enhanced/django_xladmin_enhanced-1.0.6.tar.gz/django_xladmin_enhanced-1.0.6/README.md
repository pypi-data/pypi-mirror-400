# Enhanced Django xAdmin

Enhanced Django xAdmin is a modern, responsive, and feature-rich admin interface for Django, serving as a drop-in replacement for the default Django admin. It provides a more user-friendly experience with advanced filtering, customizable dashboards, and integrated plugins.

## Features

- **Modern UI**: Based on Bootstrap, offering a clean and responsive design.
- **Drop-in Replacement**: Fully compatible with Django's default admin interface.
- **Dashboard**: customizable dashboard with widgets.
- **Theming**: Built-in support for multiple themes.
- **Plugins**: Includes support for export, revision, and more.
- **Enhanced Filters**: Advanced filtering capabilities for models.
- **Chart Support**: Easily create charts for your data.

## Installation

Install using pip:

```bash
pip install django-xladmin-enhanced
```

## Configuration

1. Add `xladmin` and dependencies to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'xladmin',
    'crispy_forms',
    'crispy_bootstrap3',
    'reversion',
    # ...
]
```

2. Configure the template pack for crispy forms:

```python
CRISPY_TEMPLATE_PACK = 'bootstrap3'
```

3. Add `xladmin` URLs to your project's `urls.py`:

```python
import xladmin
xladmin.autodiscover()

from xladmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    path('xladmin/', xladmin.site.urls),
    # ...
]
```

4. Run migrations:

```bash
python manage.py migrate
```

## Requirements

- Django >= 3.2
- django-crispy-forms
- crispy-bootstrap3
- django-import-export
- django-reversion
- Pillow
- future
- six
- xlsxwriter
- xlwt
- httplib2

## License

BSD-3-Clause
