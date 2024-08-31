# forms.py

from django import forms

class ContactForm(forms.Form):
    Name = forms.CharField(max_length=100)
    Email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
