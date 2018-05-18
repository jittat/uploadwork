from django.contrib import admin

from submissions.models import Submission

class SubmissionAdmin(admin.ModelAdmin):
    exclude = ('user',)
    
    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'user'):
            obj.user = request.user
        super().save_model(request, obj, form, change)

        
admin.site.register(Submission, SubmissionAdmin)
