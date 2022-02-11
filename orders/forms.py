
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','email','phone_number','address_line_1','address_line_2','region','city','order_note']
    def __init__(self,*args,**kwags):
        super(OrderForm,self).__init__(*args,**kwags)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter Fist Name'
        self.fields['last_name'].widget.attrs['placeholder']  = 'Enter Last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['address_line_1'].widget.attrs['placeholder'] = 'Enter Address line 1'
        self.fields['address_line_2'].widget.attrs['placeholder'] = 'Enter Address line 1'
        self.fields['region'].widget.attrs['placeholder'] = 'Enter Region'
        self.fields['city'].widget.attrs['placeholder'] = 'Enter City'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
 


        



        
