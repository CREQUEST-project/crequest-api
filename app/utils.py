from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import random
import smtplib
from core.config import settings

from email import encoders


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def send_email_attach_file_stream(
    receiver_email: list[str],
    subject: str,
    body: str,
    sender_email: str,
    file_stream: io.BytesIO,
):
    """
    Send email with attachment in the background.
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    # Attach excel file
    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_stream.getvalue())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename= search_results.xlsx",
    )
    message.attach(part)

    # Send email
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())


def send_simple_email(
    receiver_email: list[str],
    subject: str,
    body: str,
    sender_email: str,
):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_email)
    message["Subject"] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    # Send email
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.sendmail(sender_email, receiver_email, message.as_string())


def random_password():
    return "".join(
        random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
        for i in range(12)
    )
