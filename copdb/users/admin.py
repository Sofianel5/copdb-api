from django.contrib import admin

from django.apps import apps
models = apps.get_models()
admin.site.site_header = "CopDB"
admin.site.site_title = "CopDB"
admin.site.index_title = "CopDB"
for model in models:
    if "users" in str(model) or "geolocation" in str(model) or "cops" in str(model):
        try:
            admin.site.register(model)
        except admin.sites.AlreadyRegistered:
            pass