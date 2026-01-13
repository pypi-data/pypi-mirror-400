from django.urls import path
from django.views.generic import TemplateView

from .views import OrganisationCreateView

urlpatterns = [
    path("registration/", OrganisationCreateView.as_view(), name="organisation-register"),
    path(
        "registration/success/",
        TemplateView.as_view(template_name="onboarding_submit-success.html"),
        name="onboarding-success",
    ),
]
