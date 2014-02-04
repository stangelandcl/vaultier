from django.db import models
from django.db.models.deletion import PROTECT, CASCADE
from django.db.models.manager import Manager
from django.db.models import F, Q
from vaultier.models.fields import AclLevelField
from vaultier.tools.changes import ChangesMixin
from vaultier.tools.tree import TreeItemMixin
from django.utils.timezone import now


class VaultManager(Manager):

    def search(self, user, query, max_results=5):
        list = query.split()
        result = self.all_for_user(user).filter(
            Q(reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in list])) |
            Q(reduce(lambda x, y: x | y, [Q(description__icontains=word) for word in list]))
        ).order_by('updated_at')


        return result[:max_results]

        #return self.all_for_user(user).filter(
        #    Q(name__icontains=query) |
        #    Q(description__icontains=query)
        #)

    def all_for_user(self, user):
        vaults = self.filter(
            deleted_at=None,
            acl__user=user,
            acl__level=AclLevelField.LEVEL_READ
        ).distinct()

        return vaults


class Vault(ChangesMixin, models.Model, TreeItemMixin):
    class Meta:
        db_table = u'vaultier_vault'
        app_label = 'vaultier'

    def __unicode__(self):
        return 'Vault('+str(self.id)+'):'+self.name

    objects = VaultManager()

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=1024, blank=True, null=True)
    workspace = models.ForeignKey('vaultier.Workspace', on_delete=CASCADE)
    created_by = models.ForeignKey('vaultier.User', on_delete=PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    def delete(self, using=None):
        self.deleted_at = now()
        self.save()


    def get_child_objects(self):
        return self.card_set.all()


    def get_parent_object(self):
        return self.workspace