from django.contrib import admin
from django.urls import path, include
from api.jwt import (
    CustomTokenObtainPairView as TokenObtainView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('api/v1/', include('api.urls'))
]
