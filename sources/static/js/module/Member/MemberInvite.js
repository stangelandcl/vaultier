Vaultier.MemberInviteRoute = Ember.Route.extend(
    {

        inviteObject: null,

        model: function (params, transition) {
            this.setProperties(this.setupInviteData(params));

            // check permissions
            if (!this.get('auth').checkPermissions(transition, function () {
                return this.get('inviteObject.perms.invite')
            }.bind(this), true)) {
                return;
            }
        },

        /**
         * override this to setup invite workspace and invite to object
         */
        setupInviteData: function (params) {
            throw 'Please override this in your route'
        },

        /**
         * override this to setup invite breadcrumbs
         */
        setupBreadcrumbs: function () {
            throw 'Please override this in your route'
        },

        /**
         * override this to setup invite breadcrumbs
         */
        setupRoleLevels: function () {
            return Vaultier.Role.proto().roles.toArray();
        },

        actions: {
            save: function (invited, role, resend) {
                var invitations = this.get('invitations');
                var inviteWorkspace = this.get('inviteWorkspace');
                var inviteParams = this.get('inviteParams');
                var invitedPromises = [];

                invited.forEach(function (emailOrId) {
                    invitedPromises.push(
                        invitations.invite(
                            inviteWorkspace,
                            emailOrId,
                            role,
                            inviteParams,
                            true,
                            resend
                        ));
                });

                var bulk = Ember.RSVP.all(invitedPromises)
                    .then(function () {
                        $.notify('Your invitations has been saved', 'success');
                        window.history.go(-1);
                    })
                    .catch(function () {
                        $.notify('Oooups! Something went wrong.', 'error');
                    })

                return bulk;
            }
        },

        setupController: function (ctrl, model) {
            ctrl.set('workspace', this.modelFor('Workspace'))
            ctrl.set('breadcrumbs', this.setupBreadcrumbs());
            ctrl.set('content', []);
            ctrl.set('roleLevels', this.setupRoleLevels());
        },

        renderTemplate: function () {
            // this is important if you want to inherite this route https://github.com/emberjs/ember.js/issues/1872 to use proper controller
            this.render('MemberInvite', {controller: this.get('controller')})
        }

    });

Vaultier.MemberInviteController = Ember.Controller.extend({
    workspace: null,
    role: null,
    invited: [],
    resend: true,

    isSubmitDisabled: function () {
        return !this.get('invited.length')
    }.property('invited.length'),

    breadcrumbs: null
});

Vaultier.MemberInviteView = Ember.View.extend({
    templateName: 'Member/MemberInvite',
    layoutName: 'Layout/LayoutStandard',

    Select: Vaultier.MemberSelectRoleView
});