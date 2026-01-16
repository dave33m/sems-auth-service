from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_reset_email(email: str, otp: str):
    subject = "Password Reset OTP"
    html = f"""
    <p>Your password reset code is:</p>
    <h2>{otp}</h2>
    <p>This code expires in 10 minutes.</p>
    """

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=subject,
        html_content=html,
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)

def send_login_otp(email: str, otp: str):
    subject = "Login Verification Code"
    html = f"""
    <p>Your login verification code is:</p>
    <h2>{otp}</h2>
    <p>This code expires in 5 minutes.</p>
    """

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject=subject,
        html_content=html,
    )

    sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    sg.send(message)