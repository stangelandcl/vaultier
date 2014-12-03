ApplicationKernel.namespace('Vaultier.dal.model');

var decryptedField = Vaultier.dal.mixin.EncryptedModel.decryptedField;

/**
 * @module vaultier-dal-model
 * @class Vaultier.dal.model.Secret
 * @extends RL.Model
 */
Vaultier.dal.model.Secret = RL.Model.extend(
    Vaultier.dal.mixin.CreatedUpdatedMixin,
    Vaultier.dal.mixin.EncryptedModel.Mixin,
    Vaultier.dal.mixin.PolymorphicModel.Mixin,
    {
        mutableModelTypeField: 'type',
        mutableModelMapping: {
            100: 'Vaultier.dal.model.SecretNoteMixin',
            200: 'Vaultier.dal.model.SecretPasswordMixin',
            300: 'Vaultier.dal.model.SecretFileMixin'
        },

        types: new Utils.ConstantList({
            'NOTE': {
                value: 100,
                text: 'NOTE'
            },
            'PASSWORD': {
                value: 200,
                text: 'PASSWORD'
            },
            'FILE': {
                value: 300,
                text: 'FILE'
            }
        }),

        type: RL.attr('number'),
        data: RL.attr('string'),
        blob_meta: RL.attr('string'),
        card: RL.attr('number'),
        perms: RL.attr('object'),
        name: RL.attr('string')

    });

/**
 * @module model
 * @class Vaultier.dal.model.SecretNoteMixin
 */
Vaultier.dal.model.SecretNoteMixin = Ember.Mixin.create({
    note: decryptedField('data', 'note'),

    isNote: function () {
        return this.get('type') == this.types['NOTE'].value;
    }.property('type')

})

/**
 * @module model
 * @class Vaultier.dal.model.SecretPasswordMixin
 */
Vaultier.dal.model.SecretPasswordMixin = Ember.Mixin.create({
    password: decryptedField('data', 'password'),
    username: decryptedField('data', 'username'),
    url: decryptedField('data', 'url'),
    note: decryptedField('data', 'note'),

    isPassword: function () {
        return this.get('type') == this.types['PASSWORD'].value;
    }.property('type')
})

/**
 * @module model
 * @class Vaultier.dal.model.SecretFileMixin
 */
Vaultier.dal.model.SecretFileMixin = Ember.Mixin.create({
    /**
     * blob_meta encrypted attrs
     */
    filename: decryptedField('blob_meta', 'filename'),
    filesize: decryptedField('blob_meta', 'filesize'),
    filetype: decryptedField('blob_meta', 'filetype'),

    /**
     * data encrypted attrs
     */
    password: decryptedField('data', 'password'),
    username: decryptedField('data', 'username'),
    url: decryptedField('data', 'url'),
    note: decryptedField('data', 'note'),

    blob: null,

    /**
     * @DI store:main
     */
    store: null,

    init: function () {
        this.set('store', Vaultier.__container__.lookup('store:main'))
        this.on('didLoad', this, this.emptyBlob)
        this.on('didReload', this, this.emptyBlob)
        this.emptyBlob();
    },

    isFile: function () {
        return this.get('type') == this.types['FILE'].value;
    }.property('type'),

    emptyBlob: function () {
        this.set('blob', new Vaultier.dal.model.SecretBlob({
            id: this.get('id')
        }));
    },


    loadBlob: function () {
        var blob = this.get('blob');
        if (!blob.get('isNew')) {
            return Ember.RSVP.resolve(blob)
        } else {
            var promise = this.get('store')
                .find('SecretBlob', this.get('id'))
                .then(function (blob) {
                    this.set('blob', blob);
                    return blob;
                }.bind(this));
            return promise;
        }
    },

    saveRecord: function () {
        var blob = this.get('blob');
        return this
            ._super.apply(this, arguments)
            .then(function () {
                blob.set('id', this.get('id'))
                return blob.saveRecord();
            }.bind(this))
            .then(this.emptyBlob.bind(this))
    }

})

/**
 * @module model
 * @class Vaultier.dal.model.SecretBlob
 * @extends RL.Model
 */
Vaultier.dal.model.SecretBlob = RL.Model.extend(
    Vaultier.dal.mixin.EncryptedModel.Mixin,
    {
        blob_meta: RL.attr('string'),
        blob_data: RL.attr('string'),

        filename: decryptedField('blob_meta', 'filename'),
        filesize: decryptedField('blob_meta', 'filesize'),
        filetype: decryptedField('blob_meta', 'filetype'),
        filedata: decryptedField('blob_data', 'filedata'),

        /**
         * @DI service:workspacekey
         */
        workspacekey: null,

        serialize: function () {
            data = this._super.apply(this, arguments)
            var formData = new FormData()
            formData.append('blob_data', new Blob([data['blob_data']], { type: 'application/octet-stream'}))
            formData.append('blob_meta', data['blob_meta']);
            return formData
        },

        saveRecord: function () {
            if (this.get('isDirty')) {
                var params = {
                    url: '/api/secret_blobs/' + this.get('id') + '/',
                    type: 'PUT',
                    data: this.serialize(),
                    processData: false,
                    contentType: false
                };
                return Utils.RSVPAjax(params)
            } else {
                return Ember.RSVP.resolve(this);
            }
        }
    });