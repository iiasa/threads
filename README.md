**Making first public tenant**
```
tenant = Client(name="Main", schema_name="public")
Domain.objects.create(
    domain="admin.localhost",
    tenant=tenant,
    is_primary=True
)
```

**Make tenant superuser**
```
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model

User = get_user_model()

with schema_context('tenant1'):
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
```