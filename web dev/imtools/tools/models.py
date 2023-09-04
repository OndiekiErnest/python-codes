from django.db import models

# Create your models here.


class Uploads(models.Model):
    """ images model """

    image = models.ImageField(upload_to="uploads")
