from django.db import models

class Wilaya(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Wilaya Code (e.g., "58")
    name = models.CharField(max_length=255, unique=True)  # Wilaya Name (e.g., "El Menia")

    def __str__(self):
        return self.name

class Commune(models.Model):
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE, related_name="communes")
    name = models.CharField(max_length=255)  # Commune Name (e.g., "Hassi Fehal")

    class Meta:
        unique_together = ('wilaya', 'name')
        
    def __str__(self):
        return f"{self.name}, {self.wilaya.name}"
