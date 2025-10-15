from django import forms


class CompanyEditForm(forms.Form):
    """
    Form for editing company profile information.
    Allows updating basic details including name, manager, location, contact,
    address, and optional logo upload.
    """

    name = forms.CharField(
        label='نام شرکت',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام رسمی شرکت را وارد کنید'
        })
    )

    manager_name = forms.CharField(
        label='نام مدیرعامل',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام و نام خانوادگی مدیرعامل'
        })
    )

    city = forms.CharField(
        label='شهر',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'مثلاً: تهران، بندرعباس'
        })
    )

    phone = forms.CharField(
        label='شماره تلفن',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+98 21 XXXX XXXX یا 09XX XXX XXXX'
        })
    )

    address = forms.CharField(
        label='آدرس',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'آدرس کامل شرکت شامل خیابان، پلاک، واحد'
        })
    )

    logo = forms.ImageField(
        label='لوگو شرکت',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
        })
    )

    def clean_phone(self):
        """
        Validate phone number format.
        Checks for minimum length after removing non-digit characters.
        """
        phone = self.cleaned_data.get('phone')
        if phone:
            cleaned_number = ''.join(filter(str.isdigit, phone))
            if len(cleaned_number) < 10:
                raise forms.ValidationError('شماره تلفن باید حداقل 10 رقم داشته باشد.')
        return phone

    def clean_name(self):
        """
        Strip extra whitespace from company name.
        """
        name = self.cleaned_data.get('name')
        return name.strip() if name else name