from user import User
from vaultier.models.secret_blob import SecretBlob
from workspace import Workspace
from secret import Secret
from role import Role
from token import Token
from member import Member
from vault import Vault
from card import Card
from acl import Acl
from history import History

# South introspections
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^vaultier\.models\.fields\.AclDirectionField"])
add_introspection_rules([], ["^vaultier\.models\.fields\.MemberStatusField"])
add_introspection_rules([], ["^vaultier\.models\.fields\.RoleLevelField"])
add_introspection_rules([], ["^vaultier\.models\.fields\.SecretTypeField"])
add_introspection_rules([], ["^vaultier\.models\.fields\.LowerCaseCharField"])
add_introspection_rules([], ["^vaultier\.models\.object_reference\.ObjectReferenceTypeField"])

# Perms signals registration
from vaultier.perms.signals import register_signals as perm_register_signals
perm_register_signals()

#Slugs signals registration
from vaultier.models.slug import register_signals as slug_register_signals
slug_register_signals(Workspace)
slug_register_signals(Vault)
slug_register_signals(Card)

#Secret signals registration
from vaultier.models.secret import register_signals as secret_register_signals
secret_register_signals()

import reversion
reversion.register(Vault,
                   follow=['card_set'],
                   fields=['id', 'workspace', 'name', 'description', 'created_by', 'created_at', 'updated_at', 'deleted_at'])
reversion.register(Card,
                   fields=['id', 'vault', 'name', 'description', 'created_by', 'created_at', 'updated_at', 'deleted_at'])
