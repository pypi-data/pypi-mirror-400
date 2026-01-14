# DjangoLDP DS4GO

This is a Django package for the DS4GO ecosystem, providing models and tools for fact-checking applications.

See [DSIF](https://dsif.eu/).

## Configuration

Add `djangoldp_ds4go` to your `INSTALLED_APPS` and configure internationalization settings:

```yaml
dependencies:
  - djangoldp-account
  - django-webidoidc-provider
  - djangoldp-i18n
  - djangoldp-ds4go
  # ...

ldppackages:
  - rest_framework
  - oidc_provider
  - djangoldp_account
  - djangoldp_i18n
  - djangoldp_ds4go
  # ...

# [...]

server:
  # [...] # See djangoldp configuration for other settings

  USE_I18N: True
  # Your application default language, will be served if no header are provided
  LANGUAGE_CODE: fr
  # Your application fallback language, will be served when a requested language is not available
  MODELTRANSLATION_DEFAULT_LANGUAGE: fr
  # Priority order. Ensure that every language is listed here to avoid empty translations
  MODELTRANSLATION_FALLBACK_LANGUAGES:
    - fr
    - en
    - es
  # A list of all supported languages, you **must** make a migration afterwise
  LANGUAGES:
    - ['fr', 'Français']
    - ['en', 'English']
    - ['es', 'Español']
```

Run `python manage.py makemigrations` and `python manage.py migrate` after updating language settings.

## Importing RSS Data

Import fact-check data from RSS feeds using the management command:

```bash
python manage.py import_rss --rss_file="path/to/rss.xml"
```

This command parses RSS XML to create or update facts, handling translations based on the feed language, creating category hierarchies, and importing media metadata.
