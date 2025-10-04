from django.db import models
from datetime import timedelta
import os
import re
import unicodedata

CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

def normalize_text_for_db(s: str) -> str:
    """Тот же алгоритм, что и раньше — возвращаем lower, транслитерированный и очищенный текст."""
    if s is None:
        return ""
    s = str(s).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    out_chars = []
    for ch in s:
        if ch in CYR_TO_LAT:
            out_chars.append(CYR_TO_LAT[ch])
        else:
            out_chars.append(ch)
    s = "".join(out_chars)
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

class Category(models.Model):
    title = models.CharField(max_length=100)
    range_update = models.DurationField(default=timedelta(hours=24))
    last_update = models.DateTimeField(auto_now_add=True)
    discount = models.FloatField(default=1.0)

class Brand(models.Model):
    title = models.CharField(max_length=100)

class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.PositiveIntegerField(default=0)
    discount = models.FloatField(default=0)
    desc = models.JSONField(blank=True,null=True)
    count = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True)
    last_buy = models.DateTimeField(auto_now_add=True)
    cover = models.ImageField()
    normalized_text = models.TextField(blank=True, editable=False)

    def save(self, *args, **kwargs):
        full_text = f"{self.title} {self.desc or ''}"
        self.normalized_text = normalize_text_for_db(full_text)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    


class Gallery(models.Model):
    file = models.ImageField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="gallery_product")

    def save(self, *args, **kwargs):
        try:
            old_file = Gallery.objects.get(pk=self.pk).file
        except Gallery.DoesNotExist:
            old_file = None

        super().save(*args, **kwargs)

        if old_file and old_file != self.file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)



