from django.db import models


class TimeStamp(models.Model):
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(blank=True, null=True)
    date_end = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class Contract(TimeStamp):
    amount = models.FloatField()
    signature_date = models.DateField(blank=True, null=True)
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE)

    def __str__(self):
        return f"Contract id: {self.pk}"


class Event(TimeStamp):
    event_place = models.TextField()
    notes = models.TextField(blank=True, null=True)
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE)

    def __str__(self):
        return f"Event id: {self.pk}"


class Association(TimeStamp):
    employee = models.ForeignKey("users.Employee", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class ClientAssociation(Association):
    client = models.ForeignKey("users.Client", on_delete=models.CASCADE)


class ContractAssociation(Association):
    contract = models.ForeignKey("Contract", on_delete=models.CASCADE)


class EventAssociation(Association):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
