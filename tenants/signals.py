from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command
from tenants.models import Client

# @receiver(post_save, sender=Client)
# def run_tenant_migrations(sender, instance, created, **kwargs):
#     if created:
#         # Automatically apply all migrations to this tenant
#         call_command("migrate_schemas", schema_name=instance.schema_name)