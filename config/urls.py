from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)



urlpatterns = [
    path("admin/", admin.site.urls),
   
    
    # Authentication endpoints
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    path('api/assessment/', include('assessment.urls')),
    path('api/academics/', include('academics.urls')),
    path('api/announcement/', include('announcement.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/events/', include('events.urls')),
    
    #documentations
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),

]



    