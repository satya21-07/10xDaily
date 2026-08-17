import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
from app.models.feedback import Feedback

logger = logging.getLogger(__name__)

def _get_badge_colors(feedback_type: str):
    feedback_type = (feedback_type or "").lower()
    if "bug" in feedback_type:
        return {"bg": "#fee2e2", "text": "#991b1b", "border": "#fca5a5", "label": "🐛 Bug Report"}
    elif "feature" in feedback_type:
        return {"bg": "#ede9fe", "text": "#5b21b6", "border": "#c4b5fd", "label": "💡 Feature Request"}
    elif "content" in feedback_type:
        return {"bg": "#fef3c7", "text": "#92400e", "border": "#fcd34d", "label": "📚 Content Issue"}
    else:
        return {"bg": "#e0f2fe", "text": "#075985", "border": "#bae6fd", "label": "💬 General Feedback"}

def _generate_feedback_html(feedback: Feedback) -> str:
    badge = _get_badge_colors(feedback.feedback_type)
    rating_stars = ""
    if feedback.rating:
        stars_filled = "★" * feedback.rating
        stars_empty = "☆" * (5 - feedback.rating)
        rating_stars = f"""
        <tr>
            <td style="padding: 8px 0; color: #64748b; font-size: 14px;"><strong>Rating:</strong></td>
            <td style="padding: 8px 0; color: #f59e0b; font-size: 16px; font-weight: bold;">{stars_filled}<span style="color: #cbd5e1;">{stars_empty}</span> ({feedback.rating}/5)</td>
        </tr>
        """

    device_row = ""
    if feedback.device_info:
        device_row = f"""
        <tr>
            <td style="padding: 8px 0; color: #64748b; font-size: 14px;"><strong>Client Info:</strong></td>
            <td style="padding: 8px 0; color: #475569; font-size: 13px; font-family: monospace;">{feedback.device_info}</td>
        </tr>
        """

    created_at_str = feedback.created_at.strftime("%B %d, %Y at %I:%M %p UTC") if feedback.created_at else "Just now"

    # Convert newlines to breaks for safe rendering
    escaped_message = (feedback.message or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>New User Feedback - 10xDaily</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b;">
  <div style="max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
    
    <!-- Header -->
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%); padding: 28px 32px; color: #ffffff;">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
          <h1 style="margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">10xDaily • User Feedback</h1>
          <p style="margin: 6px 0 0 0; color: #c7d2fe; font-size: 14px;">A new customer feedback / issue report has been submitted</p>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div style="padding: 32px;">
      
      <!-- Type Badge -->
      <div style="margin-bottom: 20px;">
        <span style="display: inline-block; background-color: {badge['bg']}; color: {badge['text']}; border: 1px solid {badge['border']}; padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 600;">
          {badge['label']}
        </span>
        <span style="display: inline-block; background-color: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 9999px; font-size: 13px; font-weight: 500; margin-left: 8px;">
          Category: {feedback.category or 'General'}
        </span>
      </div>

      <!-- Subject -->
      <h2 style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #0f172a;">
        {feedback.subject}
      </h2>

      <!-- Details Card -->
      <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; margin-bottom: 24px;">
        <table style="width: 100%; border-collapse: collapse;">
          <tr>
            <td style="padding: 8px 0; color: #64748b; font-size: 14px; width: 120px;"><strong>From:</strong></td>
            <td style="padding: 8px 0; color: #0f172a; font-size: 14px;">{feedback.user_name or 'Anonymous User'} (&lt;<a href="mailto:{feedback.user_email}" style="color: #4f46e5; text-decoration: none;">{feedback.user_email}</a>&gt;)</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; font-size: 14px;"><strong>Submitted:</strong></td>
            <td style="padding: 8px 0; color: #475569; font-size: 14px;">{created_at_str}</td>
          </tr>
          {rating_stars}
          {device_row}
        </table>
      </div>

      <!-- Message Content -->
      <div style="margin-bottom: 24px;">
        <h3 style="margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; color: #64748b;">Feedback Description:</h3>
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #4f46e5; border-radius: 8px; padding: 18px; font-size: 15px; line-height: 1.6; color: #1e293b;">
          {escaped_message}
        </div>
      </div>

      <!-- Quick Reply Action -->
      <div style="text-align: center; margin-top: 30px;">
        <a href="mailto:{feedback.user_email}?subject=Re: [10xDaily Feedback] {feedback.subject}" 
           style="display: inline-block; background-color: #4f46e5; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 10px; font-size: 14px; font-weight: 600; box-shadow: 0 2px 4px rgba(79, 70, 229, 0.2);">
          Reply to User directly
        </a>
      </div>

    </div>

    <!-- Footer -->
    <div style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 16px 32px; text-align: center; font-size: 12px; color: #94a3b8;">
      Feedback ID: #{feedback.id} • 10xDaily User Feedback System • Automatically dispatched
    </div>
  </div>
</body>
</html>
"""
    return html

class EmailService:
    @staticmethod
    def send_feedback_email(feedback: Feedback) -> bool:
        # Dynamically read latest settings/env in case server was running when .env was edited
        import os
        smtp_host = os.getenv("SMTP_HOST", settings.SMTP_HOST)
        smtp_port = int(os.getenv("SMTP_PORT", settings.SMTP_PORT or 587))
        smtp_user = os.getenv("SMTP_USER", settings.SMTP_USER)
        smtp_password = os.getenv("SMTP_PASSWORD", settings.SMTP_PASSWORD)
        recipient = os.getenv("FEEDBACK_RECIPIENT_EMAIL", settings.FEEDBACK_RECIPIENT_EMAIL) or smtp_user
        sender = os.getenv("EMAILS_FROM_EMAIL", settings.EMAILS_FROM_EMAIL) or smtp_user or "onexDaily@gmail.com"
        sender_name = os.getenv("EMAILS_FROM_NAME", settings.EMAILS_FROM_NAME) or "10xDaily Support"

        subject = f"[10xDaily Feedback] [{feedback.feedback_type.upper()}] {feedback.subject}"
        
        print(f"[Feedback Notification] Processing ID #{feedback.id} for recipient: {recipient}")

        if not smtp_host or not recipient or not smtp_password:
            print(
                f"[EMAIL NOTICE] Missing SMTP credentials (host={smtp_host}, user={smtp_user}, password_set={bool(smtp_password)}). "
                f"Feedback #{feedback.id} saved to DB."
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{sender_name} <{sender}>"
            msg["To"] = recipient
            msg["Reply-To"] = feedback.user_email

            # Plain text fallback
            text_body = (
                f"New 10xDaily Feedback Received\n\n"
                f"Type: {feedback.feedback_type}\n"
                f"Category: {feedback.category}\n"
                f"From: {feedback.user_name} ({feedback.user_email})\n"
                f"Rating: {feedback.rating or 'N/A'}\n\n"
                f"Subject: {feedback.subject}\n"
                f"Message:\n{feedback.message}\n\n"
                f"Device: {feedback.device_info or 'N/A'}\n"
            )
            part1 = MIMEText(text_body, "plain", "utf-8")
            part2 = MIMEText(_generate_feedback_html(feedback), "html", "utf-8")

            msg.attach(part1)
            msg.attach(part2)

            password = smtp_password.replace(" ", "").strip()
            clean_user = smtp_user.strip() if smtp_user else ""

            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20)
                server.ehlo()
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
                server.ehlo()
                server.starttls()
                server.ehlo()

            if clean_user and password:
                server.login(clean_user, password)

            server.sendmail(sender, [recipient], msg.as_string())
            server.quit()

            print(f"[EMAIL SUCCESS] Feedback email #{feedback.id} successfully sent to {recipient}!")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email via SMTP: {e}")
            logger.error(f"Failed to dispatch feedback email #{feedback.id}: {str(e)}", exc_info=True)
            return False

