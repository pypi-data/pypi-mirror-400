from NEMO.serializers import ModelSerializer
from NEMO.views.api import ModelViewSet, boolean_filters, datetime_filters, key_filters, number_filters, string_filters
from drf_excel.mixins import XLSXFileMixin
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework.serializers import DateTimeField
from rest_framework.viewsets import ReadOnlyModelViewSet

from NEMO_sensors.models import (
    Sensor,
    SensorAlertEmail,
    SensorAlertLog,
    SensorCard,
    SensorCardCategory,
    SensorCategory,
    SensorData,
)


class SensorCardCategorySerializer(ModelSerializer):
    class Meta:
        model = SensorCardCategory
        fields = "__all__"


class SensorCardSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = SensorCard
        fields = "__all__"
        expandable_fields = {
            "category": "NEMO_sensors.api.SensorCardCategorySerializer",
        }


class SensorCategorySerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = SensorCategory
        fields = "__all__"
        expandable_fields = {
            "parent": "NEMO_sensors.api.SensorCategorySerializer",
        }


class SensorSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = Sensor
        fields = "__all__"
        expandable_fields = {
            "interlock_card": "NEMO.serializers.InterlockCardSerializer",
            "sensor_card": "NEMO_sensors.api.SensorCardSerializer",
            "sensor_category": "NEMO_sensors.api.SensorCategorySerializer",
        }


class SensorDataSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    created_date = DateTimeField()

    class Meta:
        model = SensorData
        fields = "__all__"
        expandable_fields = {
            "sensor": "NEMO_sensors.api.SensorSerializer",
        }


class SensorAlertEmailSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = SensorAlertEmail
        fields = "__all__"
        expandable_fields = {
            "sensor": "NEMO_sensors.api.SensorSerializer",
        }


class SensorAlertLogSerializer(FlexFieldsSerializerMixin, ModelSerializer):
    class Meta:
        model = SensorAlertLog
        fields = "__all__"
        expandable_fields = {
            "sensor": "NEMO_sensors.api.SensorSerializer",
        }


class SensorCardCategoryViewSet(ModelViewSet):
    filename = "sensor_card_categories"
    queryset = SensorCardCategory.objects.all()
    serializer_class = SensorCardCategorySerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "key": string_filters,
    }


class SensorCardViewSet(ModelViewSet):
    filename = "sensor_cards"
    queryset = SensorCard.objects.all()
    serializer_class = SensorCardSerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "server": string_filters,
        "port": number_filters,
        "category": key_filters,
        "username": string_filters,
        "extra_args": string_filters,
        "enabled": boolean_filters,
    }


class SensorCategoryViewSet(ModelViewSet):
    filename = "sensor_categories"
    queryset = SensorCategory.objects.all()
    serializer_class = SensorCategorySerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "parent": key_filters,
    }


class SensorViewSet(ModelViewSet):
    filename = "sensors"
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    filterset_fields = {
        "id": key_filters,
        "name": string_filters,
        "visible": boolean_filters,
        "sensor_card": key_filters,
        "interlock_card": key_filters,
        "sensor_category": key_filters,
        "data_label": string_filters,
        "data_prefix": string_filters,
        "data_suffix": string_filters,
        "unit_id": number_filters,
        "read_address": number_filters,
        "number_of_values": number_filters,
        "formula": string_filters,
        "read_frequency": number_filters,
        "last_read": datetime_filters,
        "last_value": number_filters,
    }


class SensorDataViewSet(ModelViewSet):
    filename = "sensor_data"
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    filterset_fields = {
        "id": key_filters,
        "sensor": key_filters,
        "created_date": datetime_filters,
        "value": number_filters,
    }


class SensorAlertEmailViewSet(ModelViewSet):
    filename = "sensor_alert_emails"
    queryset = SensorAlertEmail.objects.all()
    serializer_class = SensorAlertEmailSerializer
    filterset_fields = {
        "id": key_filters,
        "enabled": boolean_filters,
        "sensor": key_filters,
        "trigger_no_data": boolean_filters,
        "trigger_condition": string_filters,
        "triggered_on": datetime_filters,
        "additional_emails": string_filters,
    }


class SensorAlertLogViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    filename = "sensor_alert_logs"
    queryset = SensorAlertLog.objects.all()
    serializer_class = SensorAlertLogSerializer
    filterset_fields = {
        "id": key_filters,
        "sensor": key_filters,
        "time": datetime_filters,
        "value": number_filters,
        "reset": boolean_filters,
        "condition": string_filters,
        "no_data": boolean_filters,
    }
