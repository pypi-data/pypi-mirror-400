from __future__ import annotations

from NEMO.constants import (
    CHAR_FIELD_LARGE_LENGTH,
    CHAR_FIELD_MEDIUM_LENGTH,
    CHAR_FIELD_SMALL_LENGTH,
)
from NEMO.models import BaseModel, Chemical, ChemicalHazard, User
from NEMO.utilities import get_chemical_document_filename, update_media_file_on_model_update
from django.db import models
from django.dispatch import receiver


class ChemicalRequest(BaseModel):
    class Approval(object):
        PENDING = 0
        APPROVED = 1
        DENIED = 2
        Choices = ((PENDING, "Pending"), (APPROVED, "Approved"), (DENIED, "Denied"))

    requester = models.ForeignKey(
        User, blank=True, null=True, related_name="chemical_requester", on_delete=models.SET_NULL
    )
    approver = models.ForeignKey(
        User, blank=True, null=True, related_name="chemical_approver", on_delete=models.SET_NULL
    )
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=CHAR_FIELD_MEDIUM_LENGTH)
    cas = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH)
    container = models.CharField(max_length=CHAR_FIELD_SMALL_LENGTH)
    sds = models.FileField(null=True, blank=True, upload_to=get_chemical_document_filename, max_length=500)
    hazards = models.ManyToManyField(ChemicalHazard, blank=True, help_text="Select the hazards for this chemical.")
    stability = models.CharField(max_length=CHAR_FIELD_LARGE_LENGTH)
    incompatibilities = models.CharField(max_length=CHAR_FIELD_LARGE_LENGTH)
    exposure_routes = models.CharField(max_length=CHAR_FIELD_LARGE_LENGTH)
    exposure_controls = models.CharField(max_length=CHAR_FIELD_LARGE_LENGTH)
    procedure = models.TextField()
    hazardous_waste = models.BooleanField()
    waste_disposal = models.TextField()
    approved = models.IntegerField(choices=Approval.Choices, default=Approval.PENDING)
    approval_comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Chemical Requests"

    def __str__(self):
        return str(self.id)


@receiver(models.signals.post_delete, sender=ChemicalRequest)
def auto_delete_file_on_chemical_delete(sender, instance: ChemicalRequest, **kwargs):
    """Deletes file from filesystem when corresponding `Chemical` object is deleted."""
    if instance.sds:
        instance.sds.delete(False)


@receiver(models.signals.pre_save, sender=ChemicalRequest)
def auto_update_file_on_chemical_change(sender, instance: ChemicalRequest, **kwargs):
    """Updates old file from filesystem when corresponding `Chemical` object is updated with new file."""
    return update_media_file_on_model_update(instance, "sds")


class ChemicalLocation(BaseModel):
    name = models.CharField(
        max_length=CHAR_FIELD_MEDIUM_LENGTH, help_text="The name for this chemical storage location"
    )

    class Meta:
        verbose_name_plural = "Chemical Storage Location"
        ordering = ["name"]

    def __str__(self):
        return str(self.name)


class UserChemical(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    label_id = models.PositiveIntegerField(unique=True)
    chemical = models.ForeignKey(Chemical, blank=True, null=True, on_delete=models.PROTECT)
    request = models.ForeignKey(ChemicalRequest, blank=True, null=True, on_delete=models.SET_NULL)
    in_date = models.DateField()
    expiration = models.DateField()
    location = models.ForeignKey(ChemicalLocation, blank=True, null=True, on_delete=models.SET_NULL)
    history = models.TextField(default="", blank=True)

    class Meta:
        ordering = ["-expiration"]

    def __str__(self):
        return str(self.chemical.name) if self.chemical else "User Chemical"
