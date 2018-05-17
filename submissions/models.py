from django.db import models
from django.contrib.auth.models import User

def uploaded_file_path(instance, filename):
    import time
    date_data = time.strftime('%Y/%m/%d')
    
    return 'user{0}/{1}/{2}'.format(instance.user.id, date_data, filename)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_file = models.FileField(upload_to=uploaded_file_path)

    is_inqueue = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.is_inqueue:
            status = 'inqueue'
        else:
            status = 'done'
        return 'Submission by {0} at {1} ({2})'.format(self.user, self.created_at, status)
    
