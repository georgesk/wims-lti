# -*- coding: utf-8 -*-
#
#  converters.py
#
#  Authors:
#       - Coumes Quentin <coumes.quentin@gmail.com>
#

import warnings

from django.apps import AppConfig
from django.conf import settings



class WimsConfig(AppConfig):
    name = 'wims'
    verbose_name = "WIMS"
    
    
    def ready(self):
        if settings.SERVER_EMAIL == "root@localhost":
            warnings.warn(
                "Settings 'SERVER_EMAIL' has not been redefined in config.py, "
                "see https://docs.djangoproject.com/fr/2.2/ref/settings/#server-email",
                Warning
            )
            
        if settings.EMAIL_HOST == "localhost":
            warnings.warn(
                "Settings 'EMAIL_HOST' has not been redefined in config.py, "
                "see https://docs.djangoproject.com/fr/2.2/ref/settings/#email-host",
                Warning
            )