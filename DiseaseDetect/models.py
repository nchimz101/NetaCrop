from django.db import models
 
class PlantDetect(models.Model):
    userimage = models.ImageField(upload_to='images/')
    disease_name = models.CharField(max_length=300)

    def __str__(self) :
        import os
        a = os.path.basename(self.userimage.name)
        # print(os.path.basename(self.userimage.name))
        return a

    


    