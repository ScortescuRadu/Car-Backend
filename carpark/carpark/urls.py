"""
URL configuration for carpark project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),

    # User
    path('account/', include('account.urls')),

    # User relations 
    path('user/', include('user_park.urls')),
    path('user-profile/', include('user_profile.urls')),

    # Navigation
    path('map/', include('map_markers.urls')),

    # News
    path('article/', include('article.urls')),
    path('comment/', include('article_comment.urls')),

    # Parking Lot
    path('parking/', include('parking_lot.urls')),
    path('time/', include('operating_time.urls')),
    # path('entrance/', include('entrance.urls')),
    path('parking/', include('park_entrance.urls')),
    path('income/', include('income_metrics.urls')),
    path('ocupancy/', include('ocupancy_metrics.urls')),
    path('tile/', include('parking_map.urls')),
    path('parking-spot/', include('parking_spot.urls')),

    # City
    path('city/', include('city.urls')),

    # Stripe
    path('payment/', include('payments.urls')),
    path('user-stripe/', include('user_stripe.urls')),
    path('parking-invoice/', include('parking_invoice.urls')),

    # Profile
    path('profile-picture/', include('profile_picture.urls')),

    # Documentation
    path('api-auth/', include('rest_framework.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Spot Detection
    path('spot-detection/', include('spot_detection.urls')),
    path('image-dataset/', include('image_dataset.urls')),
    path('image-task/', include('image_task.urls')),
    path('entrance/', include('entrance_license.urls')),
    path('exit/', include('exit_license.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

