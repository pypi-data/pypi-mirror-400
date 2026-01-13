from NEMO.urls import router, sort_urls
from django.urls import path, re_path

from NEMO_sensors import api, views

# Rest API URLs
router.register(r"sensors/sensor_card_categories", api.SensorCardCategoryViewSet)
router.register(r"sensors/sensor_cards", api.SensorCardViewSet)
router.register(r"sensors/sensor_categories", api.SensorCategoryViewSet)
router.register(r"sensors/sensors", api.SensorViewSet)
router.register(r"sensors/sensor_data", api.SensorDataViewSet)
router.register(r"sensors/sensor_alert_emails", api.SensorAlertEmailViewSet)
router.register(r"sensors/sensor_alert_logs", api.SensorAlertLogViewSet)
router.registry.sort(key=sort_urls)


urlpatterns = [
    path("sensors/", views.sensors, name="sensors"),
    path("sensors/<int:category_id>/", views.sensors, name="sensors"),
    path("sensor_details/<int:sensor_id>/", views.sensor_details, name="sensor_details"),
    re_path(
        r"sensor_details/(?P<sensor_id>\d+)/(?P<tab>chart|data|alert)/$", views.sensor_details, name="sensor_details"
    ),
    path("sensor_chart_data/<int:sensor_id>/", views.sensor_chart_data, name="sensor_chart_data"),
    path("sensor_alert_log/<int:sensor_id>/", views.sensor_alert_log, name="sensor_alert_log"),
    path("export_sensor_data/<int:sensor_id>/", views.export_sensor_data, name="export_sensor_data"),
    path("manage_sensor_data/", views.manage_sensor_data, name="manage_sensor_data"),
]
