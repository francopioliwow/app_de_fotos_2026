# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('subir/', views.upload_photo, name='upload_photo'),
    path('carrusel/', views.carousel_view, name='carousel'),
    path('api/photos/', views.api_get_photos, name='api_photos'),

# Rutas para el anfitrión
    path('panel/', views.host_panel, name='host_panel'),
    path('panel/descargar/', views.download_all_photos, name='download_zip'),

    path('panel/eliminar/<int:photo_id>/', views.delete_photo, name='delete_photo'),
]