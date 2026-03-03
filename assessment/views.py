import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Subscriber, Campaign
from .utils import send_email_to_client
from .signals import dispatch_campaign


logger = logging.getLogger(__name__)

def subscribe(request):
    """
    Handles both subscription and unsubscription from the home page form.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name', 'Subscriber')
        action = request.POST.get('action')
        
        if not email:
            return HttpResponse("Email is required.")
            
        if action == 'subscribe':
            subscriber, created = Subscriber.objects.get_or_create(email=email)
            subscriber.first_name = name
            subscriber.is_active = True
            subscriber.save()
            
            if created:
                logger.info(f"New subscriber created: {email}")
            
            send_email_to_client(email, name)
            logger.info(f"Welcome email sent to {email}")
            return render(request, 'assessment/success.html', {'message': f"Welcome {name}! Check your email."})
            
        elif action == 'unsubscribe':
            subscriber = get_object_or_404(Subscriber, email=email)
            subscriber.is_active = False
            subscriber.save()
            logger.info(f"User {email} has unsubscribed via form.")
            return render(request, 'assessment/success.html', {'message': "You have been unsubscribed."})
            
    campaigns = Campaign.objects.all().order_by('-published_date')
    return render(request, 'assessment/index.html', {'campaigns': campaigns})


def unsubscribe(request, email):
    """
    Handles direct unsubscription via URL (e.g. from email link).
    """
    subscriber = get_object_or_404(Subscriber, email=email)
    subscriber.is_active = False
    subscriber.save()
    logger.info(f"User {email} has unsubscribed via URL.")
    return render(request, 'assessment/success.html', {'message': "You have been unsubscribed."})

def send_campaign(request, campaign_id=None):
    """
    Triggers sending a campaign to all active subscribers.
    """
    if campaign_id:
        campaign = get_object_or_404(Campaign, id=campaign_id)
    else:
        campaign = Campaign.objects.last()
        
    if not campaign:
        logger.warning("No campaigns found to send.")
        return HttpResponse("No campaigns found to send. Please create one in the Admin panel.")
        
    subscribers = Subscriber.objects.filter(is_active=True)
    if not subscribers.exists():
        logger.warning(f"No active subscribers found for campaign: {campaign.subject}")
        return HttpResponse("No active subscribers found. Please subscribe someone first.")
        
    # Trigger the Pub-Sub signal for parallel dispatch
    dispatch_campaign.send(sender=request.user.__class__, campaign=campaign, subscribers=subscribers)
    logger.info(f"Dispatch signal sent for campaign '{campaign.subject}' to {subscribers.count()} subscribers.")

    
    return render(request, 'assessment/success.html', {'message': f"Campaign '{campaign.subject}' sent successfully to {subscribers.count()} subscribers!"})

def campaign_detail(request, campaign_id):
    """
    Renders a preview of the campaign content.
    """
    campaign = get_object_or_404(Campaign, id=campaign_id)
    return render(request, 'assessment/campaign_email.html', {
        'subject': campaign.subject,
        'preview_text': campaign.preview_text,
        'article_url': campaign.article_url,
        'html_content': campaign.html_content,
        'published_date': campaign.published_date,
        'unsubscribe_url': '#',  
    })
