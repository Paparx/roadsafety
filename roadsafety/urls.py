from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()


router.register(r'users', UserViewSet, basename='user')

router.register(r'accidents', RoadAccidentViewSet, basename='accident')


urlpatterns = [

    path('', home_view, name='home'),
    path('map/', accident_hotspot_view, name='accident_hotspot'),
    path('report/', report_view, name='report'),
    path('profile/', profile_view, name='profile'),

    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    path('privacy/', legal_view, name='privacy'),  
    path('terms/', legal_view, name='terms'),    

    path('api/', include(router.urls)),
    path('api/map-data/', accident_data, name='map_data'),

    path('delete/<str:accident_id>/', delete_report, name='delete_report'),
    path('update/<str:accident_id>/', update_status, name='update_status'),
]


