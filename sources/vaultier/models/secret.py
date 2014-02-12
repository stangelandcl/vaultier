from django.db import models
from django.db.models.deletion import PROTECT, CASCADE, SET_NULL
from django.db.models.manager import Manager
from vaultier.models.fields import AclLevelField, SecretTypeField
from vaultier.tools.changes import ChangesMixin, DELETE, post_change


class SecretManager(Manager):

    def on_model(self, signal=None, sender=None, instance=None, event_type=None, **kwargs):
        if event_type==DELETE and instance.blob:
            instance.blob.delete()


    def all_for_user(self, user):
        from vaultier.models.card import Card

        cards = Card.objects.filter(
            acl__user=user,
            acl__level=AclLevelField.LEVEL_READ
        ).distinct()

        secrets = self.filter(
            card__in=cards
        )

        return secrets


class Secret(ChangesMixin, models.Model):
    class Meta:
        db_table = u'vaultier_secret'
        app_label = 'vaultier'

    objects = SecretManager()

    name = models.CharField(max_length=255, default='', blank=True, null=True)
    type = SecretTypeField()
    data = models.TextField(null=True, blank=True)
    blob = models.OneToOneField('vaultier.SecretBlob',
        null=True,
        blank=True,
        on_delete=SET_NULL
    )
    card = models.ForeignKey('vaultier.Card', on_delete=CASCADE)
    created_by = models.ForeignKey('vaultier.User', on_delete=PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def register_signals():
    post_change.connect(Secret.objects.on_model, sender=Secret)