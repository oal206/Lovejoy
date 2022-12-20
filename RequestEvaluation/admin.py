from django.contrib import admin

from .models import EvaluateRequest


# Register your models here.
# Register your models here.
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'contact_via')


admin.site.register(EvaluateRequest, EvaluationAdmin)