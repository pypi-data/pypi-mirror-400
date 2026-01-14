import requests
import sys
from datetime import datetime
from .auth import AuthUtils

class MailUtils:
    """Utilities for accessing mail resources via MS Graph API"""

    @staticmethod
    def send_mail(to_recipients, subject, body, is_html=False):
        """
        Send an email using Microsoft Graph API.
        
        Args:
            to_recipients (list): List of email addresses to send to
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): Whether the body content is HTML format
            
        Returns:
            dict: Dictionary containing status and response data
        """
        print("Sending email via Graph API...")
        
        # Ensure user is authenticated
        access_token = AuthUtils.login()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"        }
        # Create the email payload - always use HTML format to ensure proper styling
        content_type = "html"
        
        # Add PM Studio signature to the email body
        signature_html = '<br><br><div style="color: #666; font-size: 12px; font-family: Arial, sans-serif; margin-top: 20px;">Sent via <a href="https://pmstudio-aac5g7cxenedc0ex.westcentralus-01.azurewebsites.net/" style="color: #0078d4; text-decoration: none; font-weight: normal;">PM Studio</a></div>'
        
        # Convert plain text to HTML if needed
        if not is_html:
            # Convert line breaks to HTML breaks
            body_html = body.replace('\n', '<br>')
        else:
            body_html = body
            
        # Append signature to body
        body_with_signature = body_html + signature_html
        
        # Format recipients
        formatted_recipients = []
        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]
            
        for recipient in to_recipients:
            formatted_recipients.append({
                "emailAddress": {
                    "address": recipient
                }
            })

        payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": content_type,
                    "content": body_with_signature
                },
                "toRecipients": formatted_recipients
            }
        }
        
        # Send the email
        endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
        
        try:
            response = requests.post(url=endpoint, headers=headers, json=payload)
            print(f"Response status code: {response.status_code}")
            
            # Handle the response
            if response.status_code == 202:  # 202 Accepted is the success response for sendMail
                print("Email sent successfully.")
                return {
                    "status": "success",
                    "message": "Email sent successfully."
                }
            else:
                error_message = response.text
                print(f"Error sending email: {error_message}")
                return {
                    "status": "error",
                    "message": f"Error sending email: {error_message}"
                }
                
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            print(f"Exception when sending email: {error_message}")
            return {
                "status": "error",
                "message": f"Exception when sending email: {error_message}"
            }
