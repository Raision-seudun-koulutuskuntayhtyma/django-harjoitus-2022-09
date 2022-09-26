import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Tapahtuma(models.Model):
    """
    Varattava tapahtuma.

    Varaus tapahtuu lisäämällä käyttäjä "osallistujat"-listaan.
    
    Osallistujien maksimimäärä on määritelty "paikkoja"-kentällä.
    """
    otsikko = models.CharField(max_length=200)
    kuvaus = models.TextField(blank=True)
    alku = models.DateTimeField()
    loppu = models.DateTimeField(null=True, blank=True)
    osallistujat = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )
    paikkoja = models.IntegerField()
    nakyvissa = models.BooleanField(
        default=False,
        verbose_name=_("Visible"),
    )

    def __str__(self):
        alku = timezone.localtime(self.alku)
        # Ternary operator - kolmiosainen operaattori:
        # A if EHTO else B
        #   - Jos EHTO on tosi, niin tulos on A
        #   - Jos EHTO on epätosi, niin tulos on B
        loppu = timezone.localtime(self.loppu) if self.loppu else None
        loppu_teksti = f"{loppu:%d.%m.%Y %H:%M}" if loppu else ""
        return f"{self.otsikko} ({alku:%d.%m.%Y %H:%M} -- {loppu_teksti})"

    def kesto(self) -> datetime.timedelta:
        return self.loppu - self.alku

    def kesto_tuntia(self):
        kesto = self.kesto()
        return kesto.total_seconds() / 3600

    def varaa(self, user):
        """
        Varaa tämä tapahtuma annetulle käyttäjälle.

        Palauttaa True, jos tapahtuma saatiin varattua annetulle
        käyttäjälle tai jos tapahtuma oli jo varattu annetulle
        käyttäjälle.  Jos tapahtuma oli jo täynnä, eikä varaus siis
        onnistunut, niin palauttaa False.
        """
        if user in self.osallistujat.all():
            return True
        osallistujia = self.osallistujat.all().count()
        if osallistujia + 1 > self.paikkoja:
            return False
        self.osallistujat.add(user)
        return True

    def onko_varattu(self, user):
        return (user in self.osallistujat.all())
