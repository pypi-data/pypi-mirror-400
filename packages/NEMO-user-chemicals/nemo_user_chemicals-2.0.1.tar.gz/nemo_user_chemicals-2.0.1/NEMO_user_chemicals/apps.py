from django.apps import AppConfig


class NemoUserChemicalsConfig(AppConfig):
    name = "NEMO_user_chemicals"
    verbose_name = "NEMO User Chemicals"

    def ready(self):
        """
        This code will be run when Django starts.
        """
        pass
