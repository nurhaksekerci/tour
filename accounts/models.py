from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from companies.models import Company, Branch

class CustomUser(AbstractUser):
    GENDER_CHOICES = (
        ('male', _('Erkek')),
        ('female', _('Kadın')),
        ('other', _('Diğer')),
    )

    ROLE_CHOICES = (
        ('admin', _('Sistem Yöneticisi')),
        ('company_admin', _('Şirket Yöneticisi')),
        ('branch_admin', _('Şube Yöneticisi')),
        ('employee', _('Çalışan')),
    )

    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_('Şirket')
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        verbose_name=_('Şube')
    )
    phone = models.CharField(
        _('Telefon Numarası'),
        max_length=20,
        null=True,
        blank=True
    )
    gender = models.CharField(
        _('Cinsiyet'),
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    photo = models.ImageField(
        _('Profil Fotoğrafı'),
        upload_to='user_photos/',
        null=True,
        blank=True
    )
    role = models.CharField(
        _('Rol'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee'
    )
    is_company_admin = models.BooleanField(
        _('Şirket Yöneticisi mi?'),
        default=False
    )
    is_branch_admin = models.BooleanField(
        _('Şube Yöneticisi mi?'),
        default=False
    )

    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
        
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_role_display()}"