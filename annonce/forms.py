from django.contrib.auth.forms import UserCreationForm
from django import forms
from localflavor.tn.tn_governorates import GOVERNORATE_CHOICES
from annonce.models import User, Offer


class UserForm(UserCreationForm):
    position = forms.ChoiceField(choices=(('0', 'Employer'), ('1', 'Job Seekers')))

    def save(self, commit=True):
        super(UserForm, self).save(commit)
        position = self.cleaned_data['position']
        if position == '0':
            self.instance.is_employer = True
        else:
            self.instance.is_job_seekers = True
        self.instance.save()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'category', 'lieu')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'category', 'lieu')


class OfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OfferForm, self).__init__(*args, **kwargs)
        for field in self.Meta.fields:
            self.fields[field].required = True

    class Meta:
        model = Offer
        fields = ('job_title', 'description', 'sector_activity', 'sector_activity_other', 'lieu', 'expired_at',
                  'company_picture_file', 'company_name', 'company_address', 'company_url')


class CVForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('cv',)


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['job_title'].required = True
        self.fields['expired_at'].widget.attrs['placeholder'] = 'YYYY-MM-DD'

    class Meta:
        model = Offer
        fields = ['job_title', 'description', 'sector_activity', 'state', 'expired_at',
                  'company_name', 'company_address', 'company_url', 'company_mail']


class SearchForm(forms.Form):
    search = forms.CharField(max_length=255, required=False)
    region = forms.ChoiceField(choices=GOVERNORATE_CHOICES, required=False)
