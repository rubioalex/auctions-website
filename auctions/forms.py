from django import forms

from .models import Listing, Comment

class NewListingForm(forms.ModelForm):
    
    class Meta:
        model = Listing
        fields = ("object_name", "category", "description", "image", "starting_bid")
        
        widgets = {
            'category': forms.Select(attrs={
                'class': 'newlisting-field'
            }),
            
            'object_name': forms.TextInput(attrs={
                'class': 'newlisting-field'
            }),
            
            'description': forms.Textarea(attrs={
                'class': 'newlisting-field',
                'id': 'description-field'
            }),
            
            'starting_bid': forms.TextInput(attrs={
                'class': 'newlisting-field'
            }),
        }
        
        
class NewComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_body']
        widgets = {
            'comment_body': forms.Textarea(attrs={
                'rows': 3,
                'class': 'comment-body'
            })
        }