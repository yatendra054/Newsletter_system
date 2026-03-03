from django.contrib import admin, messages
from .models import Subscriber, Campaign
from .signals import dispatch_campaign



@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'is_active')
    search_fields = ('email', 'first_name')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'published_date')
    search_fields = ('subject',)
    actions = ['send_selected_campaigns']

    @admin.action(description="Send selected campaigns to all active subscribers")
    def send_selected_campaigns(self, request, queryset):
        active_subscribers = Subscriber.objects.filter(is_active=True)
        if not active_subscribers.exists():
            self.message_user(request, "No active subscribers found. No emails sent.", messages.WARNING)
            return

        sent_count = 0
        for campaign in queryset:
            dispatch_campaign.send(sender=self.__class__, campaign=campaign, subscribers=active_subscribers)
            sent_count += 1

        
        self.message_user(request, f"Successfully sent {sent_count} campaign(s) to active subscribers.", messages.SUCCESS)

