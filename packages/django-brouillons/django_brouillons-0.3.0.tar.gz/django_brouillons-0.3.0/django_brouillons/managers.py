# Django
from django.db import models
from django.utils.timezone import now


class VersionsQueryset(models.QuerySet):
    def public_versions(self, *args, **kwargs):
        from .queries import public_version_q
        return super().filter(*args, **kwargs).filter(public_version_q)

    def draft_versions(self,):
        from .models import VersionStatus
        return super().filter(version_status=VersionStatus.DRAFT.value)


class PublicManager(models.Manager):
    def get_queryset(self):
        return VersionsQueryset(self.model, using=self._db).public_versions()

    def create(self, *args, **kwargs):
        # Local application / specific library imports
        from .models import VersionStatus

        kwargs.update(
            {
                "version_status": VersionStatus.PUBLIC.value,
                "first_publication_date": now(),
            }
        )
        return super().create(*args, **kwargs)


class DraftManager(models.Manager):
    def get_queryset(self):
        return VersionsQueryset(self.model, using=self._db).draft_versions()

    def create(self, *args, **kwargs):
        # Local application / specific library imports
        from .models import VersionStatus

        kwargs.update(version_status=VersionStatus.DRAFT.value)
        return super().create(*args, **kwargs)


class VersionsManager(models.Manager):
    def get_queryset(self):
        return VersionsQueryset(self.model, using=self._db)

    def public_versions(self, *args, **kwargs):
        return self.get_queryset().public_versions(*args, **kwargs)

    def draft_versions(self):
        return self.get_queryset().draft_versions()
