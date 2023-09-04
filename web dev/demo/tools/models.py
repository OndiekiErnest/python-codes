from django.db import models


class Upload(models.Model):

    description = models.CharField(max_length=255, blank=False)
    image = models.ImageField(upload_to='uploads')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.image.name

    def save(self, *args, **kwargs):
        """ override save functionality """
        super().save(*args, **kwargs)


class Thumbnail(models.Model):
    """ edited model """
    original_image = models.ForeignKey(Upload, on_delete=models.CASCADE)
    edited_image = models.ImageField(upload_to='edits')
