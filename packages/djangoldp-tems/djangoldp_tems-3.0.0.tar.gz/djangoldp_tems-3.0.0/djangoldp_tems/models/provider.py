from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from djangoldp.models import DynamicNestedField
from djangoldp_account.models import LDPUser

from djangoldp_tems.models.__base_named_model import baseTEMSNamedModel
from djangoldp_tems.models.image import TEMSImage
from djangoldp_tems.models.provider_category import TEMSProviderCategory


class TEMSProvider(baseTEMSNamedModel):
    description = models.TextField(blank=True, null=True, default="")
    contact_url = models.CharField(max_length=2000, blank=True, null=True, default="")
    image = models.ForeignKey(
        TEMSImage, blank=True, null=True, on_delete=models.SET_NULL
    )
    categories = models.ManyToManyField(TEMSProviderCategory, blank=True)

    @property
    def catalogs(self):
        """
        List of catalogs associated with a provider.

        The list is computed by inspecting the fields of the model that start
        with "catalog_".

        Each item of the list is a dictionary with two keys:

        - "container": the name of the field (e.g. "catalog_tems1")
        - "@type": the rdf_type of the model associated with the field

        :return: a list of dictionaries
        """
        return [
            {
                "@id": f"{self.urlid}{field}/",
                "container": field,
                "@type": getattr(self, field).model._meta.rdf_type,
            }
            for field in (
                f.name for f in self._meta.get_fields() if f.name.startswith("catalog_")
            )
        ]

    class Meta(baseTEMSNamedModel.Meta):
        container_path = "/providers/"
        verbose_name = _("TEMS Provider")
        verbose_name_plural = _("TEMS Providers")

        serializer_fields = baseTEMSNamedModel.Meta.serializer_fields + [
            "description",
            "image",
            "contact_url",
            "categories",
            "catalogs",
            "services",
            "data_offers",
        ]
        nested_fields = [
            "image",
            "categories",
        ]
        rdf_type = "tems:Provider"


def register_catalog(catalog, model, object_catalog=True):
    """
    Registers a new catalog for the TEMSProvider model.

    :param str catalog: the name of the catalog field to register
    :param baseTEMSObject model: the model that will be attached
    """

    # Adds the "catalog_" + catalog to the provider model
    TEMSProvider._meta.serializer_fields += ["catalog_" + catalog]
    TEMSProvider._meta.nested_fields += ["catalog_" + catalog]

    if object_catalog:
        # Adds the "owned_" + catalog to the group model
        Group._meta.inherit_permissions += ["owned_" + catalog]
        Group._meta.serializer_fields += ["owned_" + catalog]

        # Adds the "owned_" + catalog to the user model
        LDPUser._meta.serializer_fields.append("owned_" + catalog)
        setattr(
            LDPUser,
            "owned_" + catalog + "Container",
            lambda self: {"@id": f'{self.urlid}{"owned_" + catalog}/'},
        )
        LDPUser._meta.nested_fields.append("owned_" + catalog)
        setattr(
            LDPUser,
            "owned_" + catalog,
            lambda self: model.objects.filter(owners__user=self),
        )
        # Adds a dynamic nested field to the user model
        getattr(LDPUser, "owned_" + catalog).field = DynamicNestedField(
            model, "owned_" + catalog
        )
        # Register an rdf_type for this container
        getattr(LDPUser, "owned_" + catalog).rdf_type = model._meta.rdf_type


# List of objects catalogs associated with an user.
LDPUser._meta.serializer_fields += ["owned_objects"]
LDPUser.owned_objects = lambda self: [
    {
        "@id": f"{self.urlid}{field}/",
        "container": field,
        "@type": getattr(type(self), field).rdf_type,
    }
    for field in type(self)._meta.serializer_fields
    if field.startswith("owned_") and hasattr(getattr(type(self), field), "rdf_type")
]
