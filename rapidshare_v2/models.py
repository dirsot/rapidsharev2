# -*-coding:utf-8-*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Team(models.Model):
    name = models.CharField(max_length=255, verbose_name='Imie')
    surname = models.CharField(max_length=255, verbose_name='Nazwisko')
    year = models.IntegerField(verbose_name='Rok wstapienia do organizacji', max_length=4)
    speciality = models.CharField(max_length=255, verbose_name='Specjalnosc')
    functions = models.CharField(max_length=255, verbose_name='Sprawowane funkcje')
    position = models.CharField(max_length=255, verbose_name='Obecne stanowisko', blank=True)
    projects = models.TextField(verbose_name="Realizowane projekty ", blank=True)
    about = models.TextField(verbose_name="Cos o sobie", blank=True)
    photo = models.ImageField(upload_to='photos', verbose_name='Zdjecie')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='Slug')

        
    class Meta:
        verbose_name = "Zesp�l i inni"
        verbose_name_plural = "Zesp�l i inni"
        ordering = ('surname',)
  
    def __str__(self):
        return self.surname
    def __unicode__(self):
        return self.surname
    def get_absolute_url(self):
        return ('Neolution.views.index' [self.id])

class UserGroup(models.Model):

    description = models.CharField(max_length=255, verbose_name='opis')
    name = models.CharField(max_length=255, verbose_name='nazwa grupy')
    owner = models.ForeignKey(User, blank=True, null=True,verbose_name='właściciel grupy')

    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name
    
class UserGroupAssignation(models.Model):
    owner = models.ForeignKey(User, blank=False, null=False,verbose_name='użytkownik')
    group = models.ForeignKey(UserGroup, blank=False, null=False,verbose_name='grupa')
    
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name
    
class File(models.Model):
    description = "Tabela dla plików"
    
    name = models.CharField(max_length=255, verbose_name='nazwa')
    code = models.CharField(max_length=255, verbose_name='kod', unique=True)
    despription = models.CharField(max_length=255, verbose_name='opis')
    file = models.FileField(upload_to='user_content', verbose_name='plik')
    date_uploaded = models.DateTimeField(_('date uploaded'), default=datetime.datetime.now)
    owner = models.ForeignKey(User, blank=True, null=True)
    ip = models.IPAddressField(null=True, blank=True, default=None)
    visibility = models.IntegerField(null=True, blank=True, default=0)
    
    class Meta:
        verbose_name = "Plik"
        verbose_name_plural = "Pliki"
        ordering = ('name',)
        permissions = (
            ("private_file", "Plik prywatny"),
            ("group_file", "Plik dla grupy"),
            ("link_file", "Plik dla linku"),
            ("each_up_to_10", "Jeden do 10"),
            ("each_up_to_25", "Jeden do 25"),
            ("each_up_to_100", "Jeden do 100"),
            ("all_up_to_25", "Razem do 25"),
            ("all_up_to_100", "Razem do 100"),
            ("all_up_to_1000", "Razem do 1000"),
        )
    
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name
