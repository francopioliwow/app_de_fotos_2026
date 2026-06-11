import os
import zipfile
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify

from PIL import Image, UnidentifiedImageError

from .models import EventPhoto, EventSetting


MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


def get_event_name():
    setting = EventSetting.objects.first()
    return setting.event_name if setting else "Nuestro Evento"


def validate_uploaded_image(image):
    if image.size > MAX_IMAGE_SIZE:
        return False, "La imagen es demasiado pesada. Máximo permitido: 10 MB."

    if not image.content_type.startswith("image/"):
        return False, "El archivo seleccionado no parece ser una imagen válida."

    try:
        img = Image.open(image)
        img.verify()
        image.seek(0)
    except UnidentifiedImageError:
        return False, "La imagen no es válida o está dañada."
    except Exception:
        return False, "No se pudo procesar la imagen."

    return True, ""


def upload_photo(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        guest_name = request.POST.get('guest_name', '').strip()
        table_number = request.POST.get('table_number', '').strip()

        if not image:
            messages.error(request, 'Tenés que seleccionar una foto.')
            return redirect('upload_photo')

        is_valid, error_message = validate_uploaded_image(image)

        if not is_valid:
            messages.error(request, error_message)
            return redirect('upload_photo')

        EventPhoto.objects.create(
            image=image,
            guest_name=guest_name,
            table_number=table_number
        )

        messages.success(request, '¡Tu foto se envió a la pantalla grande!')
        return redirect('upload_photo')

    return render(request, 'core/upload.html', {
        'event_name': get_event_name()
    })


def carousel_view(request):
    return render(request, 'core/carousel.html', {
        'event_name': get_event_name()
    })


def api_get_photos(request):
    photos = EventPhoto.objects.filter(
        is_approved=True
    ).order_by('-uploaded_at')[:50]

    data = []

    for photo in photos:
        if not photo.image:
            continue

        data.append({
            'id': photo.id,
            'url': photo.image.url,
            'guest_name': photo.guest_name if photo.guest_name else "Invitado",
            'table_number': photo.table_number if photo.table_number else "-"
        })

    return JsonResponse({'photos': data})


@staff_member_required
def host_panel(request):
    photos = EventPhoto.objects.all().order_by('-uploaded_at')

    return render(request, 'core/host_panel.html', {
        'photos': photos,
        'event_name': get_event_name()
    })


@staff_member_required
def download_all_photos(request):
    event_slug = slugify(get_event_name()) or "evento"
    zip_filename = f"fotos_{event_slug}.zip"

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for photo in EventPhoto.objects.all():
            if photo.image and os.path.exists(photo.image.path):
                original_name = os.path.basename(photo.image.name)
                arcname = f"foto_{photo.id}_{original_name}"
                zip_file.write(photo.image.path, arcname=arcname)

    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

    return response


@staff_member_required
def delete_photo(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(EventPhoto, id=photo_id)

        if photo.image:
            photo.image.delete(save=False)

        photo.delete()

        messages.success(request, 'La foto fue eliminada correctamente.')

    return redirect('host_panel')