from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .models import DigitalDownload


@login_required
def digital_download(request, token):
    dl = get_object_or_404(
        DigitalDownload.objects.select_related("order", "product"),
        token=token
    )

    # ownership check
    if getattr(dl.order, "user", None) != request.user:
        raise Http404("Not found")

    # handle expiry (if you use it)
    if getattr(dl, "expires_at", None) and dl.expires_at <= timezone.now():
        raise Http404("Link expired")

    # handle max_downloads (0 or None => unlimited)
    max_downloads = getattr(dl, "max_downloads", None)
    if max_downloads not in (None, 0):
        updated = DigitalDownload.objects.filter(
            pk=dl.pk,
            download_count__lt=F("max_downloads"),
        ).update(download_count=F("download_count") + 1)
        if updated == 0:
            raise Http404("Download limit reached")
    else:
        DigitalDownload.objects.filter(pk=dl.pk).update(download_count=F("download_count") + 1)

    product = dl.product

    if getattr(product, "digital_file", None):
        f = product.digital_file.open("rb")
        filename = product.digital_file.name.split("/")[-1]
        return FileResponse(f, as_attachment=True, filename=filename)

    if getattr(product, "digital_url", None):
        return redirect(product.digital_url)

    raise Http404("File missing")
