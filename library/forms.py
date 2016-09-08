from django import forms
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from nocaptcha_recaptcha.fields import NoReCaptchaField


class RegisterForm(forms.Form):
    firstName = forms.CharField(label=_('Given Name'), max_length=100)
    familyName = forms.CharField(label=_('Family Name'), max_length=100)
    #email = forms.EmailField(label=_('Email'), max_length=100)
    user = forms.EmailField(label=_('Username'), max_length=100)
    pw = forms.CharField(widget=forms.PasswordInput(),
                         label=_('Password'), max_length=100)
    captcha = NoReCaptchaField()


class IngestMetsUrlForm(forms.Form):
    url = forms.URLField(label='METS XML file URL')


class CollectionForm(forms.Form):
    collection_name = forms.CharField(
        label=_('Collection Name'), max_length=100)


class MetsFileForm(forms.Form):
    mets_file = forms.FileField()


class LanguageForm(forms.Form):
    language = forms.ChoiceField(
        label=_('Language'), choices=settings.LANGUAGES)
