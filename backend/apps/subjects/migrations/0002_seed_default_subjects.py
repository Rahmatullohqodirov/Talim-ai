from django.db import migrations


def seed_default_subjects(apps, schema_editor):
    Subject = apps.get_model("subjects", "Subject")
    db = schema_editor.connection.alias

    subjects = [
        {"code": "english", "name": "English", "kind": "language", "is_active_in_mvp": True},
        {"code": "german", "name": "German", "kind": "language", "is_active_in_mvp": False},
        {"code": "math", "name": "Mathematics", "kind": "math", "is_active_in_mvp": True},
        {"code": "russian", "name": "Russian", "kind": "language", "is_active_in_mvp": False},
        {"code": "turkish", "name": "Turkish", "kind": "language", "is_active_in_mvp": False},
    ]

    for item in subjects:
        Subject.objects.using(db).update_or_create(
            code=item["code"],
            defaults={
                "name": item["name"],
                "kind": item["kind"],
                "is_active_in_mvp": item["is_active_in_mvp"],
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("subjects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            seed_default_subjects,
            reverse_code=migrations.RunPython.noop,
        ),
    ]