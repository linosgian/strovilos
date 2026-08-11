from django.contrib.auth.models import User
from django.db import models
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from tinymce.models import HTMLField
from bs4 import BeautifulSoup
from PIL import Image
import html, datetime, logging

logger = logging.getLogger('main')

class UpImages(models.Model):
    image = models.ImageField(blank=False, upload_to='images/%Y/%m/%d/', max_length=250)
    uploaded_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    image_title = models.CharField(blank=True, max_length=255, verbose_name='Τίτλος')
    upload_date = models.DateTimeField('Ημερομηνία Ανάρτησης', default=datetime.datetime.now)


    def thumbnail(self):
        return format_html('<img src="{}" style="max-width:150px; height:auto; max-height:150px;" />', self.image.url)
    thumbnail.short_description = 'Εικόνα'
    
    def __str__(self):
        return self.image_title
    
    def save(self, *args, **kwargs):
        # Setting image title and reducing image quality.
        self.image_title = (self.image.path).split('/')[-1].split('.')[0]
        super(UpImages, self).save(*args, **kwargs)
        imagepath = self.image.path
        image = Image.open(imagepath)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        image.save(imagepath, "JPEG", quality=30)
    
    
    class Meta:
        verbose_name = "Εικόνα"
        verbose_name_plural = "Εικόνες"
        ordering = ['-upload_date']

class Category(models.Model):
    name = models.CharField('Όνομα Κατηγορίας', max_length=100, blank=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Κατηγορία"
        verbose_name_plural =  "Κατηγορίες"

class Posts(models.Model):
    STATUS_CHOICES = (
        ('p', 'Δημοσιευμένο'),
        ('d', 'Πρόχειρο'),
    )
    text = HTMLField("Κείμενο", blank=False)
    pub_date = models.DateField('Ημερομηνία Ανάρτησης', default=datetime.date.today, null=True, blank=True)
    image = models.ForeignKey(UpImages, on_delete=models.SET_NULL,null=True, blank=True, verbose_name='Εικόνα')
    title = models.CharField('Τίτλος' ,max_length=255, null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Αρθρογράφος', null=True, blank=True)
    category = models.ForeignKey(Category,default=0, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Κατηγορία')
    status = models.CharField('Κατάσταση', max_length=1, choices=STATUS_CHOICES, default='d')
    viewcount = models.IntegerField('Αριθμός Προβολών', default=0)
    
    
    def thumbnail(self):
        if self.image:
            return format_html('<img src="{}" id="thumb" style="max-width:150px; height:auto; max-height:150px;" />', self.image.image.url)
        return "Δεν υπάρχει φωτογραφία"
    thumbnail.short_description = 'Εικόνα Κειμένου'

    def show_link(self):
        return format_html('<a href="{}"> Προβολή Άρθρου </a>', self.get_absolute_url())
    show_link.short_description = "-"
    
    def __str__(self):
        if self.title:
            return self.title
        return "Δεν υπάρχει τίτλος"

    def get_absolute_url(self):
        return reverse('main:articles', args=(self.id,))
    class Meta:
        verbose_name_plural = "Δημοσιεύσεις"
        verbose_name = "Δημοσίευση"
        ordering = ['-pub_date']


class BodyText(models.Model):
    text = models.TextField('Κείμενο', blank=False)
    author = models.CharField('Ποίος Το Είπε', blank=False, max_length=255)
    active = models.BooleanField(verbose_name='Ενεργό', default=False)
    pub_date = models.DateTimeField('Ημερομηνία Αρχικής Δημοσίευσης', default=datetime.datetime.now)


    def activate(self):
        return format_html("<a href='/activate?q={}' class='grp-add-link grp-state-focus'> Ενεργοποίηση </a>", self.id)
    activate.short_description = "Ενεργοίηση Παραφοράς"

    def save(self, *args, **kwargs):
        if self.active == True:
            try:
                current_active = BodyText.objects.get(active=True)
                if self != current_active:
                    current_active.active = False;
                    current_active.save()
            except BodyText.DoesNotExist:
                pass
        super(BodyText, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Παραφορές"
        verbose_name = "Παραφορά"

# Avoid circular imports
from .utils import truncate

class Bios(models.Model):
    def get_number():
        num = Bios.objects.count()
        if num:
            return num + 1
        # Case : no objects are present in the db.
        # Then return 1.
        return 1
    author_name = models.CharField(max_length=50, blank=False, verbose_name="Όνομα")
    author_cv   = models.TextField(blank=False, verbose_name="Βιογραφικό")
    position    = models.IntegerField(verbose_name="Αριθμός Θέσης", default=get_number) 
    minified_cv = models.CharField(max_length=255, blank=True, verbose_name="Βιογραφικό")
    
    def __str__(self):
        return self.author_name
    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                curr_bios = Bios.objects.get(position=self.position)
                curr_bios.position = Bios.get_number()
                curr_bios.save()
            except ObjectDoesNotExist:
                pass
        self.minified_cv = truncate(self.author_cv)
        super(Bios, self).save(*args, **kwargs)
    class Meta:
        ordering = ["position",]
        verbose_name = "Βιογραφικό"
        verbose_name_plural = "Βιογραφικά"

# Overring User's str method
def user_str_patch(self):
    return self.first_name

User.__str__ = user_str_patch