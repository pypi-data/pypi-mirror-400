from django.apps import AppConfig


class DjangoldpTemsConfig(AppConfig):
    name = "djangoldp_tems"
    verbose_name = "TEMS - Shared Objects"

    def ready(self):
        from django.contrib.auth.models import Group
        from django.db.models.signals import post_save

        from djangoldp_tems.models.__base_object import baseTEMSObject

        def create_owners_group(instance, **kwargs):
            if hasattr(type(instance), "owners") and not instance.owners:
                instance.owners, x = Group.objects.get_or_create(
                    name=f"owners_{type(instance).__name__.lower()}_{instance.id}"
                )
                instance.save()

        post_save.connect(create_owners_group, baseTEMSObject)

        def connect_subclasses(base_class):
            for subclass in base_class.__subclasses__():
                post_save.connect(create_owners_group, subclass)
                connect_subclasses(subclass)

        connect_subclasses(baseTEMSObject)
