from django.dispatch import Signal, receiver
from .utils import send_campaign_to_subscribers
import logging

# Define a custom signal for campaign dispatch
# providing_args=["campaign", "subscribers"]
dispatch_campaign = Signal()

@receiver(dispatch_campaign)
def handle_campaign_dispatch(sender, campaign, subscribers, **kwargs):
    """
    Signal receiver that triggers the parallel email dispatch.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Signal received: Dispatching campaign '{campaign.subject}' to {subscribers.count()} subscribers.")
    
    send_campaign_to_subscribers(campaign, subscribers)
