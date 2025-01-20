from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Message, Contact, Group, Template
import re

# registration
class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
	first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
	last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))


	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
	
	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("This email address is already registered.")
		return email


	def __init__(self, *args, **kwargs):
		super(SignUpForm, self).__init__(*args, **kwargs)

		self.fields['username'].widget.attrs['class'] = 'form-control'
		self.fields['username'].widget.attrs['placeholder'] = 'User Name'
		self.fields['username'].label = ''
		# self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

		self.fields['password1'].widget.attrs['class'] = 'form-control'
		self.fields['password1'].widget.attrs['placeholder'] = 'Password'
		self.fields['password1'].label = ''
		# self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

		self.fields['password2'].widget.attrs['class'] = 'form-control'
		self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
		self.fields['password2'].label = ''
		# self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'	


# compose sms

from django import forms
import re

class MessageForm(forms.ModelForm):
    send_now = forms.ChoiceField(
        choices=[('now', 'Now'), ('later', 'Later')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'id': 'sendOptions',
        }),
        label="Send",
    )
    send_later_time = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control ms-2',
            'placeholder': '14-01-2025@01:51pm',
            'id': 'sendLaterTime',
        }),
        label="",
    )
    recipients_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Recipients (Groups)",
    )

    class Meta:
        model = Message
        fields = [
            'sender_id', 'recipients', 'message', 'send_now', 
            'send_later_time', 'recipients_group'
        ]
        widgets = {
            'sender_id': forms.TextInput(attrs={'class': 'form-control'}),
            'recipients': forms.Textarea(attrs={'class': 'form-control mt-2', 'rows': 3}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_recipients(self):
        recipients = self.cleaned_data.get('recipients', '')

        # Split the recipients by commas
        recipients_list = [r.strip() for r in recipients.split(',') if r.strip()]

        # Regular expression to validate phone numbers (e.g., +254711XXXYYY)
        phone_number_regex = re.compile(r'^\+?[1-9]\d{1,14}$')

        # Validate each phone number
        invalid_numbers = [
            number for number in recipients_list if not phone_number_regex.match(number)
        ]

        if invalid_numbers:
            raise forms.ValidationError(
                f"The following phone numbers are invalid: {', '.join(invalid_numbers)}"
            )

        # Return the cleaned recipients as a comma-separated string
        return ','.join(recipients_list)

# personalized messages
class PersonalizeMessageForm(forms.Form):
    sender_id = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sender ID'})
    )

    # For uploading XLS or CSV file
    upload_file = forms.FileField(
        required=True,  # File is mandatory for personalized SMS
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xls,.csv'}),
        help_text="Upload an Excel or CSV file with recipient details."
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your message here...'
        }),
        help_text=(
            "Use placeholders for personalization:<br>"
            "<code>@@name@@</code> for recipient name."
        ),
    )

    schedule_option = forms.ChoiceField(
        choices=[('now', 'Send Now'), ('later', 'Later')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='now'
    )

    schedule_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control mt-2', 'type': 'datetime-local'}),
        disabled=True
    )

    def clean(self):
        cleaned_data = super().clean()
        schedule_option = cleaned_data.get('schedule_option')
        schedule_time = cleaned_data.get('schedule_time')

        if schedule_option == 'later' and not schedule_time:
            self.add_error('schedule_time', 'Schedule time is required for later scheduling.')

        return cleaned_data

from django import forms
from .models import Template

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter template title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter template content'}),
        }
        labels = {
            'title': 'Template title',
            'content': 'content',
        }


# Form for creating/editing a contact
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ['date_created']  # Exclude non-editable fields like 'date_created'

    # Custom validation for phone number
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) < 10:
            raise forms.ValidationError("Phone number must be at least 10 digits.")
        return phone_number


# Form for creating/editing a contact list
class ContactFilterForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False, label='Search')
    contact_type = forms.ChoiceField(choices=[('PRIVATE', 'Private'), ('SHARED', 'Shared')], required=False, label='Type')
    page_size = forms.ChoiceField(choices=[('10', '10 rows'), ('20', '20 rows'), ('50', '50 rows')], required=False, initial='10', label='Rows per page')

# sent messages
class SentMessagesFilterForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Keyword'
        })
    )
    type = forms.ChoiceField(
        choices=[('any', 'Any Type')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Date From'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'Date To'
        })
    )



# class TopUpForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ["amount", "phone_number"]
#         widgets = {
#             "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount"}),
#             "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
#         }
