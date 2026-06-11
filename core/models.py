from django.db import models


class EventSetting(models.Model):
    """Configuración global del evento actual"""
    event_name = models.CharField(
        max_length=100,
        default="Mi Gran Evento",
        verbose_name="Nombre del Evento"
    )

    class Meta:
        verbose_name = "Configuración del evento"
        verbose_name_plural = "Configuración del evento"

    def save(self, *args, **kwargs):
        # Evita que se creen muchas configuraciones.
        if not self.pk and EventSetting.objects.exists():
            self.pk = EventSetting.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return self.event_name


class EventPhoto(models.Model):
    image = models.ImageField(upload_to='event_photos/')
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nombre del Invitado"
    )
    table_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Mesa"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, verbose_name="Aprobada")

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Foto del evento"
        verbose_name_plural = "Fotos del evento"

    def __str__(self):
        invitado = self.guest_name if self.guest_name else "Anónimo"
        mesa = self.table_number if self.table_number else "-"
        return f"Foto {self.id} - {invitado} - Mesa {mesa}"