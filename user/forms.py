
from django import forms
from django.forms import fields, models
from django.forms.widgets import PasswordInput
from .models import User, UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=PasswordInput(attrs={
        'placeholder':'Enter password',
        
    }))
    confirm_password = forms.CharField(widget=PasswordInput(attrs={
        'placeholder':'Confirm password',
        
    }))
    class Meta:
        model = User
        fields = ['first_name','last_name','email','phone_number','password']
    def __init__(self,*args,**kwags):
        super(RegistrationForm,self).__init__(*args,**kwags)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter Fist Name'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']

        if password !=confirm_password:
            raise forms.ValidationError(
                'Password does not match!'
            )

class ProfileForm(forms.ModelForm):
    profile_pic = forms.ImageField(required=False,error_messages={'Invalid':("Image files only")},widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['profile_pic','address_line1','address_line2','region','city']

    def __init__(self,*args,**kwags):
        super(ProfileForm,self).__init__(*args,**kwags)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number']
    
    def __init__(self,*args,**kwags):
        super(UserForm,self).__init__(*args,**kwags)    
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
        



        
