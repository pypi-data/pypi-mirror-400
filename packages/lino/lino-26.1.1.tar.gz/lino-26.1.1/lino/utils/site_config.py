# -*- coding: UTF-8 -*-
# Copyright 2009-2026 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from asgiref.sync import sync_to_async
from django.conf import settings
from django.db.utils import DatabaseError
from django.utils import timezone
from lino.utils import date_offset


class SiteConfigPointer:

    # The following were in Site and SiteConfig before 20260104:

    # _site_config = None
    tenant_id = 1

    # def clear_site_config(self):
    #     pass
    #     # self._site_config = None

    @property
    def site_config(self):
        site = settings.SITE
        if "system" not in site.models:
            return None
        if not site._startup_done:
            site.logger.debug("site_config is None because startup not done")
            return None
        if self.tenant_id != 1:
            raise Exception(f"20260107 tenant_id is {self.tenant_id} instead of 1")
            # multitenancy is not yet done
        SiteConfig = site.models.system.SiteConfig
        try:
            return SiteConfig.objects.get(id=self.tenant_id)
        except (SiteConfig.DoesNotExist, DatabaseError):
            # e.g. during migrate the SiteConfig maybe doesn't yet exist
            # except SiteConfig.DoesNotExist:
            return SiteConfig(id=self.tenant_id)

    def get_config_value(self, name, default=None):
        if (sc := self.site_config) is None:
            return default
            # self.site_config_defaults.get(name, default)
        return getattr(sc, name)

    def today(self, *args, **kwargs):
        site = settings.SITE
        if (sc := self.site_config) is None:
            base = site.the_demo_date
        else:
            base = sc.simulate_today or site.the_demo_date
        if base is None:
            # base = datetime.date.today()
            base = timezone.now().date()
        return date_offset(base, *args, **kwargs)

    async def atoday(self, *args, **kwargs):
        return await sync_to_async(self.today)(*args, **kwargs)

    def now(self, *args, **kwargs):
        t = self.today(*args, **kwargs)
        now = timezone.now()
        return now.replace(year=t.year, month=t.month, day=t.day)

    def get_printing_build_method(self):
        sc = self.site_config
        if sc.default_build_method:
            return sc.default_build_method
        return settings.SITE.models.printing.BuildMethods.get_system_default()
