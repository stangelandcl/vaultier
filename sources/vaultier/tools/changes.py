from django.dispatch import Signal


post_change = Signal()
"""
Signal sent whenever an instance is saved or deleted
and changes have been recorded.
"""

from django.db.models import signals

CREATE = 0
INSERT = 1
UPDATE = 2
DELETE = 3


class ChangesMixin(object):
    _states = []

    def __init__(self, *args, **kwargs):
        super(ChangesMixin, self).__init__(*args, **kwargs)

        self._states = []
        self._save_state(new_instance=True, event_type=CREATE)

        def _post_save(sender, instance, **kwargs):
            instance._post_save(**kwargs)

        def _post_delete(sender, instance, **kwargs):
            instance._post_delete(*kwargs)

        signals.post_save.connect(
            _post_save,
            weak=False,
            sender=self.__class__,
            dispatch_uid='django-changes-%s' % self.__class__.__name__
        )
        signals.post_delete.connect(
            _post_delete,
            weak=False,
            sender=self.__class__,
            dispatch_uid='django-changes-%s' % self.__class__.__name__
        )

    def _post_save(self, **kwargs):
        if kwargs.get('created'):
            event_type = INSERT
        else:
            event_type = UPDATE
        self._save_state(event_type=event_type)
        post_change.send(sender=self.__class__, instance=self, event_type=event_type)

    def _post_delete(self, **kwargs):
        self._save_state(event_type=DELETE)
        post_change.send(sender=self.__class__, instance=self, event_type=DELETE)


    def _save_state(self, new_instance=False, event_type=INSERT):
        # Pipe the pk on deletes so that a correct snapshot of the current
        # state can be taken.
        if event_type == DELETE:
            self.pk = None

        # Save current state.
        self._states.append(self.current_state())

        # Drop the previous old state
        # _states == [previous old state, old state, previous state]
        #             ^^^^^^^^^^^^^^^^^^
        if len(self._states) > 2:
            self._states.pop(0)

        # Send post_change signal unless this is a new instance
        if not new_instance:
            post_change.send(sender=self.__class__, instance=self, event_type=event_type)

    def current_state(self):
        """
        Returns a ``field -> value`` dict of the current state of the instance.
        """
        field_names = set()
        [field_names.add(f.name) for f in self._meta.local_fields]
        [field_names.add(f.attname) for f in self._meta.local_fields]

        dict = {}
        for field_name in field_names:
            try:
                dict[field_name] = getattr(self, field_name)
            except:
                pass

        return dict


    def previous_state(self):
        """
        Returns a ``field -> value`` dict of the state of the instance after it
        was created, saved or deleted the previous time.
        """
        if len(self._states) > 1:
            return self._states[1]
        else:
            return self._states[0]

    def old_state(self):
        """
        Returns a ``field -> value`` dict of the state of the instance after
        it was created, saved or deleted the previous previous time. Returns
        the previous state if there is no previous previous state.
        """
        return self._states[0]

    def _changes(self, other, current):
        return dict([(key, (was, current[key])) for key, was in other.iteritems() if was != current[key]])

    def changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the previous state to the current state.
        """
        return self._changes(self.previous_state(), self.current_state())

    def old_changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the current state.
        """
        return self._changes(self.old_state(), self.current_state())

    def previous_changes(self):
        """
        Returns a ``field -> (previous value, current value)`` dict of changes
        from the old state to the previous state.
        """
        return self._changes(self.old_state(), self.previous_state())

    def was_persisted(self):
        """
        Returns true if the instance was persisted (saved) in its old
        state.

        Examples::

            >>> user = User()
            >>> user.save()
            >>> user.was_persisted()
            False

            >>> user = User.objects.get(pk=1)
            >>> user.delete()
            >>> user.was_persisted()
            True
        """
        pk_name = self._meta.pk.name
        return bool(self.old_state()[pk_name])

    def is_persisted(self):
        """
        Returns true if the instance is persisted (saved) in its current
        state.

        Examples:

            >>> user = User()
            >>> user.save()
            >>> user.is_persisted()
            True

            >>> user = User.objects.get(pk=1)
            >>> user.delete()
            >>> user.is_persisted()
            False
        """
        return bool(self.pk)

    def old_instance(self):
        """
        Returns an instance of this model in its old state.
        """
        return self.__class__(**self.old_state())

    def previous_instance(self):
        """
        Returns an instance of this model in its previous state.
        """
        return self.__class__(**self.previous_state())


