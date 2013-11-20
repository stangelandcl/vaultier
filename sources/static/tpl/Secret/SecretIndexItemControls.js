Ember.TEMPLATES["Secret/SecretIndexItemControls"] = Ember.Handlebars.template(function anonymous(Handlebars,depth0,helpers,partials,data) {
this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Ember.Handlebars.helpers); data = data || {};
  var buffer = '', stack1, stack2, hashTypes, hashContexts, options, helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, self=this;

function program1(depth0,data) {
  
  
  data.buffer.push("Edit secret");
  }

  data.buffer.push("<div class=\"vlt-controls\">\r\n    <div class=\"help-block vlt-author col-md-6\">\r\n        By ");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  data.buffer.push(escapeExpression(((stack1 = helpers.printUser || depth0.printUser),stack1 ? stack1.call(depth0, "created_by", options) : helperMissing.call(depth0, "printUser", "created_by", options))));
  data.buffer.push(" Updated: ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers._triageMustache.call(depth0, "updated_ago", {hash:{},contexts:[depth0],types:["ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push("\r\n    </div>\r\n\r\n    <div class=\"vlt-buttons col-md-6\">\r\n        <div class=\"btn-group\">\r\n            <a type=\"button\"\r\n               class=\"btn btn-default dropdown-toggle btn-sm\"\r\n               data-toggle=\"dropdown\">\r\n                <span class=\"glyphicon glyphicon-cog\"></span>\r\n            </a>\r\n            <ul class=\"dropdown-menu caret-left\">\r\n                <li>");
  hashTypes = {};
  hashContexts = {};
  options = {hash:{},inverse:self.noop,fn:self.program(1, program1, data),contexts:[depth0,depth0],types:["STRING","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data};
  stack2 = ((stack1 = helpers['link-to'] || depth0['link-to']),stack1 ? stack1.call(depth0, "Secret.edit", "", options) : helperMissing.call(depth0, "link-to", "Secret.edit", "", options));
  if(stack2 || stack2 === 0) { data.buffer.push(stack2); }
  data.buffer.push("</li>\r\n                <li><a href=\"javascript:\" ");
  hashTypes = {};
  hashContexts = {};
  data.buffer.push(escapeExpression(helpers.action.call(depth0, "deleteSecret", "", {hash:{},contexts:[depth0,depth0],types:["ID","ID"],hashContexts:hashContexts,hashTypes:hashTypes,data:data})));
  data.buffer.push(">Delete secret</a></li>\r\n            </ul>\r\n        </div>\r\n\r\n        <div class=\"clearfix\"></div>\r\n\r\n    </div>\r\n\r\n</div>");
  return buffer;
  
});
