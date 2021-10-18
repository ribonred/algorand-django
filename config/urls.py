from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView









urlpatterns = [
    path('admin/', admin.site.urls),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('jet/', include('jet.urls', 'jet')),
    path('webadmin/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    
]
