from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def discount_active(end_date):
    """Return True if end_date is present and >= today (localdate).

    `end_date` is expected to be a `date` (DateField) or None.
    """
    if not end_date:
        return False
    try:
        today = timezone.localdate()
    except Exception:
        # Fallback to timezone.now().date() if localdate not available
        today = timezone.now().date()
    return end_date >= today
