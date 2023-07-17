from django.contrib import admin
from django.urls import path, include




urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', include('professors.urls')),
    path('', include('students.urls')),
    path('', include('meetings.urls')),
    path('', include('payments.urls')),
    path('', include('students.urls')),
    path('swagger/', include('swagger_doc.urls')),
    # path('api/', include('professors.urls')),
    # path('api/', include('meetings.urls')),
    # path('api/', include('payments.urls')),
    path('admin/', admin.site.urls),
]
