from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get dict item by key: {{ mydict|get_item:key }}"""
    return dictionary.get(key)


@register.filter
def percentage(value, total):
    """Calculate percentage: {{ score|percentage:total }}"""
    try:
        return round(float(value) / float(total) * 100, 1)
    except (TypeError, ZeroDivisionError):
        return 0


@register.filter
def multiply(value, arg):
    """Multiply: {{ value|multiply:2 }}"""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0


@register.filter
def subtract(value, arg):
    """Subtract: {{ value|subtract:arg }}"""
    try:
        return float(value) - float(arg)
    except (TypeError, ValueError):
        return 0


@register.filter
def to_json(value):
    """Convert Python object to JSON string for JS"""
    return mark_safe(json.dumps(value))


@register.filter
def split(value, sep=','):
    """Split string: {{ tags|split:',' }}"""
    return [s.strip() for s in value.split(sep) if s.strip()]


@register.filter
def currency(value):
    """Format as INR currency"""
    try:
        return f'₹{float(value):,.2f}'
    except (TypeError, ValueError):
        return '₹0.00'


@register.filter
def stars(value):
    """Convert rating to stars: {{ 4.2|stars }}"""
    full  = int(float(value))
    half  = 1 if (float(value) - full) >= 0.5 else 0
    empty = 5 - full - half
    html  = ('★' * full) + ('½' * half) + ('☆' * empty)
    return mark_safe(f'<span style="color:#ffd700">{html}</span>')


@register.filter
def duration_fmt(minutes):
    """Format minutes as Xh Ym"""
    try:
        m = int(minutes)
        if m >= 60:
            h, rem = divmod(m, 60)
            return f'{h}h {rem}m' if rem else f'{h}h'
        return f'{m}m'
    except (TypeError, ValueError):
        return '0m'


@register.filter
def file_size_fmt(size_bytes):
    """Format bytes as human-readable file size"""
    try:
        b = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if b < 1024:
                return f'{b:.1f} {unit}'
            b /= 1024
        return f'{b:.1f} TB'
    except (TypeError, ValueError):
        return '0 B'


@register.simple_tag
def progress_color(pct):
    """Return a CSS color based on percentage"""
    pct = float(pct)
    if pct >= 80:
        return '#00e676'
    elif pct >= 50:
        return '#ffd700'
    else:
        return '#ff6584'


@register.simple_tag
def score_label(pct):
    """Return label based on percentage"""
    pct = float(pct)
    if pct >= 90: return 'Outstanding'
    if pct >= 75: return 'Excellent'
    if pct >= 60: return 'Good'
    if pct >= 40: return 'Average'
    return 'Needs Work'


@register.inclusion_tag('partials/progress_bar.html')
def progress_bar(value, color='purple', height=8):
    return {'value': value, 'color': color, 'height': height}


@register.filter
def ordinal(n):
    """Convert integer to ordinal: 1 → 1st"""
    try:
        n = int(n)
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        suffix = suffixes.get(n % 10 if n % 100 not in [11, 12, 13] else 0, 'th')
        return f'{n}{suffix}'
    except (TypeError, ValueError):
        return str(n)


@register.filter
def truncate_middle(value, max_len=40):
    """Truncate from middle: abcdef...xyz"""
    s = str(value)
    if len(s) <= max_len:
        return s
    half = (max_len - 3) // 2
    return s[:half] + '…' + s[-half:]
