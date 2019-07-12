# Generated by Django 2.2.2 on 2019-07-10 05:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='BindHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='IDC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_type', models.SmallIntegerField(choices=[(0, 'ssh-password'), (1, 'ssh-key')], default=0)),
                ('username', models.CharField(max_length=64)),
                ('password', models.CharField(blank=True, max_length=128, null=True)),
            ],
            options={
                'unique_together': {('auth_type', 'username', 'password')},
            },
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('bind_hosts', models.ManyToManyField(blank=True, null=True, to='lady.BindHost')),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=64)),
                ('ip_addr', models.GenericIPAddressField(unique=True)),
                ('port', models.PositiveIntegerField(default=22)),
                ('enabled', models.BooleanField(default=True)),
                ('idc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lady.IDC')),
            ],
        ),
        migrations.AddField(
            model_name='bindhost',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lady.Host'),
        ),
        migrations.AddField(
            model_name='bindhost',
            name='host_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lady.HostUser'),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, null=True, unique=True, verbose_name='email address')),
                ('password', models.CharField(help_text='<a href="password">修改密码</a>', max_length=128, verbose_name='password')),
                ('name', models.CharField(max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('bind_hosts', models.ManyToManyField(blank=True, to='lady.BindHost')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('host_groups', models.ManyToManyField(blank=True, to='lady.HostGroup')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='bindhost',
            unique_together={('host', 'host_user')},
        ),
    ]
