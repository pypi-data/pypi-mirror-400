from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ParticipantRegistrationForm
from .models import RegisterParticipant
from django.utils.functional import lazy
from django.conf import settings

def prefixed_reverse_lazy(viewname, *args, **kwargs):
    lazy_reverse = reverse_lazy(viewname, *args, **kwargs)
    return lazy(lambda url: getattr(settings, "ONBOARDING_PREFIX", "") + url, str)(lazy_reverse)

class OrganisationCreateView(CreateView):
    model = RegisterParticipant
    form_class = ParticipantRegistrationForm
    template_name = "onboarding_form.html"
    success_url = prefixed_reverse_lazy("onboarding-success")

    def form_valid(self, form):
      response = super().form_valid(form)
      response.status_code = 303
      return response
