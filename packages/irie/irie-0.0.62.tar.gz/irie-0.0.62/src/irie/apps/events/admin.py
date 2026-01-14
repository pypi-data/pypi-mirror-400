#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from django.contrib import admin
from .models import HazardEvent, EventRecord
from django import forms

# admin.site.register(EventRecord)
@admin.register(EventRecord)
class EventRecordAdmin(admin.ModelAdmin):
    class form(forms.ModelForm):
        class Meta:
            model = EventRecord
            fields = '__all__'
    search_fields = ['cesmd', 'anssid', 'record_identifier']
    list_display = ['id', 'cesmd', 'anssid', '__str__', 'event_file']
    # filter_horizontal = ['benchmarks']