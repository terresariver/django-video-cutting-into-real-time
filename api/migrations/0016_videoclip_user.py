from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_clipexportjob'),
    ]

    operations = [
        migrations.AddField(
            model_name='videoclip',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='clips', to='api.user'),
            preserve_default=False,
        ),
    ]
