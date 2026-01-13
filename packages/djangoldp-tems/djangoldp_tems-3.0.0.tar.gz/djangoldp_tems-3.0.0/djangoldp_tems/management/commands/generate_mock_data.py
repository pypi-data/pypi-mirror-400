import random

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import (BooleanField, CharField, DateField,
                              DateTimeField, DecimalField, ForeignKey,
                              IntegerField, TextField)
from faker import Faker


class Command(BaseCommand):
    help = "Generates mock data for all models in the project"

    def handle(self, *args, **options):
        fake = Faker()
        all_models = apps.get_models()

        for model in all_models:
            if model._meta.app_label in [
                "djangoldp_mediaobject",
                "djangoldp_civilsociety",
                "djangoldp_factchecking",
                "djangoldp_interactiveinfographic",
                "djangoldp_story",
                "djangoldp_object3d",
                "djangoldp_sentiment",
                "djangoldp_tems",
            ]:
                try:
                    # Create a new instance of the model
                    instance = model()

                    # Populate the fields with fake data
                    for field in model._meta.fields:
                        if field.name not in [
                            "pk",
                            "urlid",
                            "id",
                            "is_backlink",
                            "allow_create_backlink",
                            "creation_date",
                            "created",
                            "modified",
                            "user_id",
                            "owners",
                        ]:
                            if field.name == "title":
                                setattr(
                                    instance,
                                    field.name,
                                    " ".join(fake.words(random.randint(2, 5))),
                                )
                            elif field.name == "name":
                                setattr(instance, field.name, " ".join(fake.words(2)))
                            elif field.name == "description":
                                setattr(instance, field.name, fake.text())
                            elif field.name == "url":
                                setattr(
                                    instance,
                                    field.name,
                                    "https://placehold.co/420x500?text=" + fake.word(),
                                )
                            elif isinstance(field, ForeignKey):
                                # Handle related fields
                                related_model = field.related_model
                                # Always create a new related instance
                                related_instance = related_model()
                                for related_field in related_model._meta.fields:
                                    if related_field.name not in [
                                        "pk",
                                        "urlid",
                                        "id",
                                        "is_backlink",
                                        "allow_create_backlink",
                                        "creation_date",
                                        "created",
                                        "modified",
                                        "user_id",
                                        "owners",
                                    ]:
                                        if isinstance(
                                            related_field, (CharField, TextField)
                                        ):
                                            if related_field.name == "title":
                                                setattr(
                                                    related_instance,
                                                    related_field.name,
                                                    " ".join(
                                                        fake.words(random.randint(2, 5))
                                                    ),
                                                )
                                            elif related_field.name == "name":
                                                setattr(
                                                    related_instance,
                                                    related_field.name,
                                                    " ".join(fake.words(2)),
                                                )
                                            elif related_field.name == "description":
                                                setattr(
                                                    related_instance,
                                                    related_field.name,
                                                    fake.text(),
                                                )
                                            elif related_field.name == "url" or related_field.name == "iframe":
                                                setattr(
                                                    related_instance,
                                                    related_field.name,
                                                    "https://placehold.co/420x500?text="
                                                    + fake.word(),
                                                )
                                            else:
                                                setattr(
                                                    related_instance,
                                                    related_field.name,
                                                    fake.text(),
                                                )
                                        elif isinstance(related_field, DateField):
                                            setattr(
                                                related_instance,
                                                related_field.name,
                                                fake.date_object(),
                                            )
                                        elif isinstance(related_field, DateTimeField):
                                            setattr(
                                                related_instance,
                                                related_field.name,
                                                fake.date_time_this_century(),
                                            )
                                        elif isinstance(related_field, BooleanField):
                                            setattr(
                                                related_instance,
                                                related_field.name,
                                                fake.boolean(),
                                            )
                                        elif isinstance(related_field, DecimalField):
                                            setattr(
                                                related_instance,
                                                related_field.name,
                                                fake.pydecimal(
                                                    left_digits=3,
                                                    right_digits=7,
                                                    positive=True,
                                                ),
                                            )
                                        elif isinstance(related_field, IntegerField):
                                            setattr(
                                                related_instance,
                                                related_field.name,
                                                fake.pyint(),
                                            )
                                    related_instance.save()
                                    setattr(instance, field.name, related_instance)
                            elif isinstance(field, DateField):
                                setattr(instance, field.name, fake.date_object())
                            elif isinstance(field, DateTimeField):
                                setattr(
                                    instance,
                                    field.name,
                                    fake.date_time_this_century(),
                                )
                            elif isinstance(field, BooleanField):
                                setattr(instance, field.name, fake.boolean())
                            elif isinstance(field, DecimalField):
                                setattr(
                                    instance,
                                    field.name,
                                    fake.pydecimal(
                                        left_digits=3, right_digits=7, positive=True
                                    ),
                                )
                            elif isinstance(field, IntegerField):
                                setattr(instance, field.name, fake.pyint())
                            else:
                                try:
                                    setattr(instance, field.name, fake.word())
                                except Exception as e:
                                    pass  # Ignore fields that can't be populated with a word

                    # Save the instance
                    instance.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully generated mock data for {model._meta.model_name}"
                        )
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Could not generate mock data for {model._meta.model_name}: {e}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS("Successfully generated mock data for all models")
        )
