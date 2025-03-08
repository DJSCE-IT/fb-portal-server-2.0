from flask import render_template
from flask_mail import Message
from app import mail
import os

def send_email(to, subject, template, **kwargs):
    """Send an email to the recipients using the specified template"""
    msg = Message(subject, recipients=[to] if isinstance(to, str) else to)
    msg.html = render_template(template, **kwargs)
    mail.send(msg)

def send_otp_email(email, otp):
    """Send OTP email to the user"""
    return send_email(
        email,
        "OTP Verification - Feedback Portal",
        "email/otp_email.html",
        otp=otp,
        dj_logo=os.environ.get("DJ_LOGO"),
        mail=os.environ.get("EMAIL_HOST_USER")
    )

def send_reset_password_email(email, token):
    """Send reset password email to the user"""
    return send_email(
        email,
        "Reset Password - Feedback Portal",
        "email/reset_password_email.html",
        token=token,
        url=f"{os.environ.get('FRONT_END_LINK')}/resetPassword/{email}/{token}",
        dj_logo=os.environ.get("DJ_LOGO"),
        mail=os.environ.get("EMAIL_HOST_USER")
    )

def send_feedback_reminder(emails, form):
    """Send reminder email to students who haven't filled the feedback form"""
    if not emails:
        return
    
    subject_type = "Theory" if form.is_theory else "Practical"
    
    return send_email(
        emails,
        "REMINDER: Fill the feedback form - Feedback Portal",
        "email/reminder_email.html",
        dj_logo=os.environ.get("DJ_LOGO"),
        subject_name=form.subject.subject_name,
        teacher_name=form.teacher.myuser.name,
        subject_type=subject_type,
        url=f"{os.environ.get('FRONT_END_LINK')}/feedBackForm/{form.id}",
        mail=os.environ.get("EMAIL_HOST_USER")
    ) 