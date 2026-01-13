from netbox.api.routers import NetBoxRouter
from . import views

router = NetBoxRouter()

router.register('configuration-item', views.ConfigurationItemViewSet)
router.register('service', views.ItilServiceViewSet)
router.register('application', views.ApplicationViewSet)
router.register('relation', views.RelationViewSet)
router.register('pentest', views.PenTestViewSet)

urlpatterns = router.urls
app_name = 'nb_itsm-api'
