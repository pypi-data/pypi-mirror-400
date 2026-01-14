# django-omnitenant

django-omnitenant is a Django app that enables multi-tenancy with DB-level isolation and schema-level isolation.

Detailed documentation is in the "docs" directory.

## Quick start

1. Add "django_omnitenant" to your `INSTALLED_APPS` setting like this:

```python
INSTALLED_APPS = [
    ...,
    "django_omnitenant",
]

**Note:** Place django_omnitenant at the last in installed apps so that it will reregister all the default only apps to show on default db
**Note:** Make sure `DEFAULT_TENANT_NAME` is postgre schema name complaint
**Note:** Need to set the `DEFAULT_HOST`


### Test
For tests's tenant setup you can override _setup_tenant method to setup tenant but make sure to assign it to the class variable cls.tenant

