from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from localflavor.tn.tn_governorates import GOVERNORATE_CHOICES

from FM.settings import MEDIA_ROOT
from metadata.models import TanitJobsCategory


@python_2_unicode_compatible
class Offer(models.Model):
    # tanitjobs
    token = models.CharField(max_length=255, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('User', blank=True, null=True)
    slug = models.SlugField()
    job_title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sector_activity = models.ManyToManyField(TanitJobsCategory, blank=True)
    sector_activity_other = models.CharField(max_length=255, blank=True, null=True)
    lieu = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True, choices=GOVERNORATE_CHOICES)
    expired_at = models.DateField(blank=True, null=True)
    company_picture = models.CharField(max_length=255, blank=True, null=True)
    company_picture_file = models.FileField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    company_url = models.CharField(max_length=255, blank=True, null=True)
    company_token = models.CharField(max_length=255, blank=True, null=True)
    company_mail = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "%s" % self.job_title

    @models.permalink
    def get_absolute_url(self):
        return 'post_details', (), {'pk': self.pk, 'slug': self.slug}

    def save(self, *args, **kwargs):
        self.slug = slugify(self.job_title) + '.html'
        super(Offer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    username = models.CharField(_('Username'),
                                help_text=_('Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.'),
                                max_length=30, null=True, blank=True)
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    email = models.EmailField(_('Email Address'), max_length=254, unique=True)
    is_staff = models.BooleanField(_('Staff Status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('Status'), default=True,
                                    help_text=_('Designates whether the user is active or no.'))
    date_joined = models.DateTimeField(_('Date Joined'), default=timezone.now)
    category = models.ForeignKey(TanitJobsCategory, null=True)
    is_employer = models.BooleanField(_('is_employer'), default=False,
                                      help_text=_('Designates whether the user is a is employer or not'))
    is_job_seekers = models.BooleanField(_('is_employer'), default=False,
                                         help_text=_('Designates whether the user is a is employer or not'))
    cv = models.FileField(null=True, blank=True)

    objects = UserManager()
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name
