from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from .models import Conversation, Message

@admin.register(Message)
class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}

class MessageInline(admin.TabularInline):
    model = Message
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0

@admin.register(Conversation)
class ConversationAdmin(DjangoLDPAdmin):
    inlines = [MessageInline]