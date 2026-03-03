from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from concurrent.futures import ThreadPoolExecutor
import logging

def send_email_to_client(email, username):
    subject = "Welcome to Trader Market Insights"
    messages = (
        f"Hello {username},\n\n"
        f"Thank you for joining Trader Market Insights! We're excited to have you with us.\n\n"
        f"You will now receive our latest newsletters, market updates, and exclusive articles directly in your inbox. "
        f"Stay tuned for high-quality insights and data-driven analysis.\n\n"
        f"If you ever wish to stop receiving these emails, you can find an unsubscribe link at the bottom of our newsletters.\n\n"
        f"Best regards,\n"
        f"The Trader Market Insights Team"
    )
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, messages, from_email, recipient_list)


def send_campaign_to_single_subscriber(campaign, subscriber, from_email):
    """
    Sends a campaign to a single subscriber.
    """
    try:
        # Construct unsubscribe URL
        unsubscribe_url = f"{settings.SITE_URL}{reverse('unsubscribe', args=[subscriber.email])}"
        
        context = {
            'subject': campaign.subject,
            'preview_text': campaign.preview_text,
            'article_url': campaign.article_url,
            'html_content': campaign.html_content,
            'published_date': campaign.published_date,
            'unsubscribe_url': unsubscribe_url,
        }
        
        html_message = render_to_string('assessment/campaign_email.html', context)
        
        # Use provided plain text content or fallback to stripping HTML tags
        plain_message = campaign.plain_text_content if campaign.plain_text_content else strip_tags(html_message)
        
        send_mail(
            subject=campaign.subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[subscriber.email],
            html_message=html_message
        )
        return True
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send email to {subscriber.email}: {e}")
        return False

def send_campaign_to_subscribers(campaign, subscribers):
    """
    Sends a campaign email to a list of subscribers using parallel threads.
    """
    from_email = settings.EMAIL_HOST_USER
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for subscriber in subscribers:
            executor.submit(send_campaign_to_single_subscriber, campaign, subscriber, from_email)
