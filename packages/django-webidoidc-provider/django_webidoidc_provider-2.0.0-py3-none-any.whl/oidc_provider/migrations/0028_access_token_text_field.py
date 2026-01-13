from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_provider', '0027_token_token_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='access_token',
            field=models.TextField(unique=True, verbose_name='Access Token'),
        ),
    ]
