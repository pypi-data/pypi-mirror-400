from NEMO.decorators import customization
from NEMO.utilities import render_email_template
from NEMO.views.customization import CustomizationBase, get_media_file_contents
from django.core.validators import validate_email


@customization("chemicals", "User Chemicals")
class ChemicalsCustomization(CustomizationBase):
    variables = {"chemical_request_email_addresses": ""}
    files = [("chemical_request_email", ".html"), ("chemical_request_update_email", ".html")]

    def validate(self, name, value):
        if name == "chemical_request_email_addresses":
            recipients = tuple([e for e in value.split(",") if e])
            for email in recipients:
                validate_email(email)

    @staticmethod
    def render_template(template_name, dictionary: dict, request=None):
        template = get_media_file_contents(template_name)
        return render_email_template(template, dictionary, request=request)
