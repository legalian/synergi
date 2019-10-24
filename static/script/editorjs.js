function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}
function nthIndex(str, pat, n){
    var L= str.length, i= -1;
    while(n-- && i++<L){
        i= str.indexOf(pat, i);
        if (i < 0) break;
    }
    return i;
}
$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.search);
    return (results !== null) ? results[1] || 0 : false;
}
var suhd = $.urlParam('projectId')
var COLORS = shuffle([
    '#e21400', '#91580f', '#f8a700', '#f78b00',
    '#58dc00', '#287b00', '#a8f07a', '#4ae8c4',
    '#3b88eb', '#3824aa', '#a700ff', '#d300e7'
]);
var colori = 0;
// var host = window.location.origin.replace(/^http/, 'ws');
// this.connection = new WebSocket(host);
var socket = io(window.location.origin.replace(/^http/, 'ws'),{transports: ['polling']});//,{query:'loggeduser=user1'}
socket.on('connect', function() {
$.ajax("/join", {
	type: "POST",
	contentType: "application/json",
	data: ko.toJSON({
		projectId:suhd
	}),
	success: function(data){
socket.emit('join',{projectId:suhd})
socket.on('accept',function(servedata){
var projectid = servedata.sessionId
var justice = new AppViewModel();
function Directory(data){
	var self = this;
	self.type = 'tree';
	self.title = data.title;
	self.path = data.path;
	self.children = ko.observableArray([]);
	self.expanded = ko.observable(true);
	self.radd = function(ra) {
		ra.title = ra.title.substr(ra.title.indexOf('/')+1);
		if (ra.title.indexOf('/') == -1) {
			if (ra.type == 'blob') {
				self.children.push(new File(ra));
			} else if (ra.type == 'tree') {
				self.children.push(new Directory(ra));
			}
		} else {
			self.children()[self.children().length-1].radd(ra);
		}
	}
	self.click = function(){}
}
// var Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/++[++^A-Za-z0-9+/=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}
function File(data) {
	var self = this;
	self.type = 'blob';
	self.title = data.title;
	self.path = data.path;
	self.sha = data.sha;
	self.loaded = false
	self.content = ko.observable("");
	self.connectedusers = ko.observableArray([]);
	self.unload = function() {
		self.content("");
		self.loaded = false;
	}
	self.requestload = function(callback) {
		console.log("RequestLoad")
		console.log(self.content().getValue)
		if (!self.loaded) {
			self.loaded = true;
			function aye(data) {
				self.content(data);
				callback();
			};
			$.ajax("/files", {
				type: "POST",
				data: ko.toJSON({
					sessionId:projectid,
					path:self.path
				}),
				contentType: "application/json",
				success: function(data){
					console.log("Success")
					console.log(data)
					console.log(self.content(data).getValue)
					// self.editor
					self.content(data);
					callback();
				}
			});
		}
	}
	self.click = function(){
		justice.openfile(self);
	}
}
function User(data) {
	self.name = data;
	self.color = COLORS[colori];
	colori = (colori+1)%12;
}
function AppViewModel() {
	var self =	this;
	self.children = ko.observableArray([]);
	self.tabs = ko.observableArray([]);
	self.activeusers = ko.observableArray(servedata['activemembers'].split(",").map(function(item){return new User(item);}));
	socket.on('player_join',function(data){
		self.activeusers.push(data.name);
	});
	socket.on('player_leave',function(data){
		self.activeusers.remove(data.name);
	});
	self.editor = ace.edit("editor");
	self.editor.setTheme("ace/theme/monokai");
	self.editor.session.setMode("ace/mode/javascript");
	// var beautify = ace.require("ace/ext/beautify");
	self.listening = 0;
	socket.on('edit',function(data){
		console.log("event edit",data)
		if (self.activefile()==null) {return}
		self.tabs().forEach(function(item){
			if (item.path == self.activefile().path) {
				console.log("change made");
				var icont = item.content();
				if (data.mode == "insert") {
					item.content(icont.slice(0,data.delta.amt)+data.delta.msg+icont.slice(data.delta.amt));
				} else if (data.mode == "remove") {
					item.content(icont.slice(0,data.delta.amt)+icont.slice(data.delta.amt+data.delta.msg.length))
				}
				item.content.notifySubscribers();
			}
		});
		if (self.activefile().path == data.path){
			self.activefile.notifySubscribers();
		}
	});
	self.editor.session.on('change', function(delta) {
		console.log("change edit(B)",delta)
		if (self.activefile()==null) {return}
		if (self.listening != 0) {return}
		console.log("change edit",delta)
		var yaya = self.editor.getValue()
		self.activefile().content(yaya);
		var amt = nthIndex(yaya,"\n",delta.start.row)+1+delta.start.column;
		var msg = delta.lines.join("\n")
		socket.emit('edit', {
			delta:{amt:amt,msg:msg},
			mode:delta.action,
			path:self.activefile().path,
			sessionId:projectid
		});
	});
	self.activefile = ko.observable(null);
	self.activefile.subscribe(function(){
	// self.activecontent = ko.computed(function(){
		if (self.activefile() == null) {return null}
		if (self.activefile().content() == null) {
			self.editor.setReadOnly(true);
			self.editor.setValue("");
		}
		self.editor.setReadOnly(false);
		self.listening++;
		self.editor.session.setValue(self.activefile().content());
		self.listening--;
	});
	self.openfile = function(file) {
		if (self.tabs().indexOf(file) == -1) {
			self.tabs.push(file);
		}
		self.activefile(file);
		file.requestload(function(){self.activefile.notifySubscribers();});
	};
	self.users = ko.observableArray([]);
	$.ajax("/directories", {
		type: "POST",
		contentType: "application/json",
		data: ko.toJSON({
			sessionId:projectid
		}),
		success: function(data){
			console.log(data);
			data.tree.forEach(function(ra){
				ra.title = ra.path;
				console.log(ra.title);
				if (ra.title.indexOf('/') == -1) {
					if (ra.type == 'blob') {
						self.children.push(new File(ra));
					} else if (ra.type == 'tree') {
						self.children.push(new Directory(ra));
					}
				} else {
					self.children()[self.children().length-1].radd(ra);
				}
			});
		}
	});
}
ko.applyBindings(justice);
});
}
});
});