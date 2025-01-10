from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import SMSMessage, Contact, ContactList

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
class SMSMessageForm(forms.Form):
    sender_id = forms.CharField(
        label='Sender ID',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sender ID'}),
    )
    
    TYPE_CHOICES = [
        ('group', 'Group'),
        ('individual', 'Individual'),
    ]
    type_recipients = forms.ChoiceField(
        label='Type Recipients',
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    recipients = forms.CharField(
        label='Recipients',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type recipients separated by commas or one per line'}),
    )
    
    PHONE_BOOK_CHOICES = [
        ('group1', 'Group 1'),
        ('group2', 'Group 2'),
        ('group3', 'Group 3'),
        ('group4', 'Group 4'),
        ('group5', 'Group 5'),
    ]
    phone_book = forms.ChoiceField(
        label='Phone Book',
        choices=PHONE_BOOK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Type your message here'}),
    )
    
    SEND_OPTIONS = [
        ('now', 'Now'),
        ('later', 'Later'),
    ]
    send_option = forms.ChoiceField(
        label='Send',
        choices=SEND_OPTIONS,
        widget=forms.RadioSelect,
        initial='now'
    )
    
    schedule_time = forms.CharField(
        label='Schedule Time',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Day-month-year@time', 'disabled': True}),
    )
    
    # This method will help enable/disable the schedule_time field based on the radio choice
    def clean(self):
        cleaned_data = super().clean()
        send_option = cleaned_data.get('send_option')

        # If 'sendLater' is selected, schedule_time should not be empty
        if send_option == 'later' and not cleaned_data.get('schedule_time'):
            self.add_error('schedule_time', 'Please specify a schedule time.')
        
        return cleaned_data

# personalized messages
class PersonalizeMessageForm(forms.Form):
    sender_id = forms.CharField(
        max_length=255, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Sender ID'})
    )
    
    # For uploading XLS file
    upload_xls = forms.FileField(
        required=False,  # File is optional
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xls'})
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 5, 
            'placeholder': 'Enter your message here...'
        }),
        help_text=(
            "Replace Recipient name with <code>@@name@@</code> and Amount value with <code>@@amount@@</code>."
            "<br>Example: If our recipient is Ronald and he has a balance of 35,000,<br>"
            "Message will be: Hello <code>@@name@@</code>, you have a balance of <code>@@amount@@</code>.<br>"
            "Other parameters include: <code>@@var1@@</code>, <code>@@var2@@</code>, <code>@@var3@@</code>, etc."
        ),
    )
    
    # Schedule option (Send now or Later)
    SCHEDULE_CHOICES = [
        ('now', 'Send Now'),
        ('later', 'Later'),
    ]
    
    schedule_option = forms.ChoiceField(
        choices=SCHEDULE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='now'
    )
    
    # Schedule time (only enabled if "Later" is selected)
    schedule_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control mt-2', 'type': 'datetime-local'}),
        disabled=True
    )

    def clean(self):
        cleaned_data = super().clean()
        schedule_option = cleaned_data.get('schedule_option')
        schedule_time = cleaned_data.get('schedule_time')

        # If 'Later' is selected, schedule_time should not be None
        if schedule_option == 'later' and not schedule_time:
            self.add_error('schedule_time', 'Schedule time is required when scheduling for later.')

        return cleaned_data

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
class ContactListForm(forms.ModelForm):
    class Meta:
        model = ContactList
        fields = ['name', 'is_private', 'contacts']
        widgets = {
            'contacts': forms.CheckboxSelectMultiple(),  # Allow selecting multiple contacts
        }

    # Custom validation for list name to ensure uniqueness
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if ContactList.objects.filter(name=name).exists():
            raise forms.ValidationError("A list with this name already exists.")
        return name

# Form for filtering contacts (pagination / search functionality can be added)
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
