from datetime import datetime

from NEMO.models import Chemical
from django.forms import CharField, ModelChoiceField, ModelForm, ModelMultipleChoiceField, Textarea
from django.utils import timezone

from NEMO_user_chemicals.models import ChemicalHazard, ChemicalLocation, ChemicalRequest, UserChemical


class ChemicalRequestApprovalForm(ModelForm):

    class Meta:
        model = ChemicalRequest
        fields = ["approved", "approval_comments"]

    def __init__(self, user, *args, **kwargs):
        super(ChemicalRequestApprovalForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super(ChemicalRequestApprovalForm, self).save(commit=False)
        instance.approver = self.user
        return super(ChemicalRequestApprovalForm, self).save(commit=commit)


class ChemicalRequestForm(ModelForm):

    hazards = ModelMultipleChoiceField(queryset=ChemicalHazard.objects.all(), required=False, label="hazards")

    class Meta:
        model = ChemicalRequest
        fields = [
            "requester",
            "name",
            "cas",
            "container",
            "stability",
            "incompatibilities",
            "hazards",
            "exposure_routes",
            "exposure_controls",
            "procedure",
            "hazardous_waste",
            "waste_disposal",
            "sds",
        ]

    def __init__(self, user, *args, **kwargs):
        super(ChemicalRequestForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        # 1. Create instance but don't save to DB yet (so M2M isn't saved yet either)
        instance = super(ChemicalRequestForm, self).save(commit=False)

        # 2. Set the requester
        instance.requester = self.user

        if commit:
            # 3. Save the instance to the DB to generate an ID
            instance.save()
            # 4. Manually save the Many-to-Many data (hazards)
            self.save_m2m()

        return instance


class ChemicalForm(ModelForm):

    hazards = ModelMultipleChoiceField(queryset=ChemicalHazard.objects.all(), required=False, label="hazards")

    class Meta:
        model = Chemical
        fields = [
            "name",
            "keywords",
            "hazards",
            "document",
            "url",
        ]


class UserChemicalForm(ModelForm):

    # Explicitly define the location field to ensure the queryset is correctly populated
    location = ModelChoiceField(queryset=ChemicalLocation.objects.all(), required=True, label="Location")
    comments = CharField(required=False, widget=Textarea(attrs={"rows": 3, "class": "form-control"}), label="Comments")

    class Meta:
        model = UserChemical
        # Added "request" to fields so it can be saved from the hidden input
        fields = ["owner", "label_id", "in_date", "expiration", "chemical", "location", "request"]

    def clean_in_date(self):
        in_date = self.cleaned_data["in_date"]
        return timezone.make_aware(
            datetime(year=in_date.year, month=in_date.month, day=in_date.day), timezone.get_current_timezone()
        )

    def clean_expiration(self):
        expiration = self.cleaned_data["expiration"]
        return timezone.make_aware(
            datetime(year=expiration.year, month=expiration.month, day=expiration.day), timezone.get_current_timezone()
        )
