from django.db import models

class LogQuery(models.Model):
    name = models.CharField(max_length=100)
    query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class JenkinsJob(models.Model):
    name = models.CharField(max_length=100)
    job_url = models.URLField()
    last_build_number = models.IntegerField(default=0)
    last_build_status = models.CharField(max_length=50, blank=True)
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
