from django.db import models


class StudyProgress(models.Model):
    user_id = models.CharField(max_length=255, help_text="Identifier for the user (e.g., email, session ID)")
    topic = models.CharField(max_length=255, help_text="The topic that was studied")
    hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Hours spent studying the topic")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="The exact time when the progress was recorded")

    class Meta:
        verbose_name_plural = "Study Progress Entries"

    def __str__(self):
        return f"{self.user_id} - {self.topic} - {self.hours}h on {self.timestamp.date()}"
