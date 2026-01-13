from django.apps import AppConfig


class SensorsConfig(AppConfig):
    name = "NEMO_sensors"
    label = "sensors"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies

        """
        This code will be run when Django starts.
        """
        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
