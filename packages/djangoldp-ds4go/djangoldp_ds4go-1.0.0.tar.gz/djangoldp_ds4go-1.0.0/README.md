# DjangoLDP DS4GO

This is a Django project for DS4GO ecosystem.

See [DS4GO](https://dsif.eu/).

## Server settings

```yaml
  USE_I18N: True
  # Your application default language, will be served if no header are provided
  LANGUAGE_CODE: fr
  # Your application fallback language, will be served when a translation is not available
  MODELTRANSLATION_DEFAULT_LANGUAGE: fr
  # A list of all supported languages, you **must** make a migration afterwise
  LANGUAGES:
    - ['fr', 'Français']
    - ['en', 'English']
    - ['es', 'Español']
```
