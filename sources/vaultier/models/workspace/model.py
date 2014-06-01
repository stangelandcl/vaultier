from django.db import models
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager
from django.db.models.query_utils import Q
from modelext.softdelete.softdelete import SoftDeleteManagerMixin, SoftDeleteMixin
from modelext.tree.iterator import TreeIterableModelMixin
from vaultier.models.acl.fields import AclLevelField
from vaultier.models.member.fields import MemberStatusField
from vaultier.models.member.model import Member
from vaultier.models.role.fields import RoleLevelField
from vaultier.models.role.model import Role
from modelext.changes.changes import ChangesMixin
from vaultier.models.workspace.tree import WorkspaceTreeIterator
from django.db.models.aggregates import Count


class WorkspaceManager(SoftDeleteManagerMixin, Manager):
    def all_for_user(self, user):
        workspaces = self.filter(
            acl__user=user,
            acl__level=AclLevelField.LEVEL_READ
        ).distinct()

        return workspaces

    def get_workspaces_with_recoverable_info(self, user):
        """
        Add an extra column with the number of members to the result set from
        filtering the workspaces where the user is a member
        :param user:
        :return: QuerySet
        """
        annotated_workspaces = self.filter(
            membership__status=MemberStatusField.STATUS_MEMBER,
            pk__in=Member.objects.filter(user=user).values_list('workspace_id', flat=True)) \
            .annotate(is_recoverable=Count('membership'))

        return annotated_workspaces | self.filter(membership__user=user, membership__status=MemberStatusField.STATUS_MEMBER_WITHOUT_WORKSPACE_KEY)

    def create_member_with_workspace(self, workspace):
        attrs_needed = ['_user', ]
        if not all(hasattr(workspace, attr) for attr in attrs_needed):
            raise AttributeError('_user attribute is required to create related membership')

        m = Member(
            workspace=workspace,
            user=workspace._user,
            status=MemberStatusField.STATUS_MEMBER_WITHOUT_WORKSPACE_KEY,
            created_by=workspace._user
        )
        m.save()

        r = Role(
            member=m,
            to_workspace=workspace,
            created_by=workspace._user,
            level=RoleLevelField.LEVEL_WRITE
        )
        r.save()


class Workspace(ChangesMixin, SoftDeleteMixin, TreeIterableModelMixin, models.Model):
    class Meta:
        db_table = u'vaultier_workspace'
        app_label = 'vaultier'

    tree_iterator_class = WorkspaceTreeIterator

    objects = WorkspaceManager()

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=1024, blank=True, null=True)
    created_by = models.ForeignKey('vaultier.User', on_delete=PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        created = self.id == None
        super(Workspace, self).save(*args, **kwargs)
        if created:
            Workspace.objects.create_member_with_workspace(self)
