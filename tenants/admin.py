from django.contrib import admin
from django.core.management import call_command
import psycopg2


# Register your models here.
from django_tenants.admin import TenantAdminMixin

from tenants.models import Client, Domain

@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'created_on')

    def save_model(self, request, obj, form, change):
        is_new = obj._state.adding
        super().save_model(request, obj, form, change)

        if is_new:     
            # try:
            #     obj.create_schema()
            # except psycopg2.ProgrammingError:
            #     print(f"Schema {obj.schema_name} already exists.")
            call_command('migrate_schemas', schema_name=obj.schema_name)



@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("tenant", "is_primary")