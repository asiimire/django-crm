from __future__ import print_function
import africastalking

from dcrm.settings import AFRICAS_TALKING_API_KEY, AFRICAS_TALKING_USERNAME

class SMS:
    def __init__(self):
        # Set your app credentials
        self.username = AFRICAS_TALKING_USERNAME
        self.api_key = AFRICAS_TALKING_API_KEY

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    def send(self, message, recipients, sender=None):
        """
        Send SMS messages to recipients.
        Args:
            message (str): The message to send.
            recipients (list): List of recipient phone numbers.
            sender (str): Shortcode or sender ID (optional).
        Returns:
            dict: Response from the Africa's Talking API.
        """
        try:
            response = self.sms.send(message, recipients, sender)
            print(response)
            return response
        except Exception as e:
            print(f"Encountered an error while sending: {e}")
            return None

# an instance of the SMS class called sms_service
sms_service = SMS()