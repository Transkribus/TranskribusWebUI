from django import forms

class RegisterForm(forms.Form):
    given_name = forms.CharField(label='Given Name', max_length=100)
    family_name = forms.CharField(label='Family Name', max_length=100)
    email = forms.EmailField(label='Email', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), label='Password', max_length=100)

class IngestMetsUrlForm(forms.Form):
    url = forms.URLField(label='METS XML file URL')

class CollectionForm(forms.Form):
    collection_name = forms.CharField(label='Collection Name', max_length=100)

class MetsFileForm(forms.Form):
    mets_file = forms.FileField()
