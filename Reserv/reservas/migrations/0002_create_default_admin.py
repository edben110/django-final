from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        },
    )
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.password = make_password('admin')
    user.save(update_fields=['password', 'is_staff', 'is_superuser', 'is_active'])


def remove_default_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('reservas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
