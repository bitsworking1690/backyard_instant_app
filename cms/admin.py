from django.contrib import admin
from .models import YourModelName  # Replace with your actual model name

class YourModelAdmin(admin.ModelAdmin):
    list_display = ('field1', 'field2')  # Replace with your actual fields
    search_fields = ('field1',)  # Replace with your actual fields

admin.site.register(YourModelName, YourModelAdmin)  # Replace with your actual model name