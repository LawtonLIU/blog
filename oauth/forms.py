from django import forms

class RequireEmailForm(forms.Form):
    '''
    邮箱 必填
    oauthid 隐藏 不必填
    '''
    email=forms.EmailField(label='电子邮箱',required=True)
    oauthid=forms.IntegerField(widget=forms.HiddenInput,required=False)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['email'].widget=forms.widgets.EmailInput(
            attrs={'placeholder':'email','class':'form-control'})