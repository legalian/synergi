
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
	self.children = [];
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
			self.children[self.children.length-1].radd(ra);
		}
	}
	self.click = function(){}
}
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
		if (!self.loaded) {
			self.loaded = true;
			function aye(data) {
				self.content(data);
				callback();
			};
			$.ajax("/files", {
				type: "GET",
				data: ko.toJSON({
					projectid:projectid,
					path:self.path
				}),
				contentType: "application/json",
				success: function(data){
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
	self.children = [];
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

	self.listening = 0;

	socket.on('edit',function(data){
		var data = data.data;
		if (self.activefile()==null) {return}
		self.tabs().forEach(function(item){
			if (item.path == self.activefile().path) {
				console.log("change made");
				var icont = item.content();
				item.content(icont.slice(0,data.delta.amt)+data.delta.msg+icont.slice(data.delta.amt));
				item.content.notifySubscribers();
			}
		});
		if (self.activefile().path == data.path){
			self.activefile().notifySubscribers();
		}
	});
	self.editor.session.on('change', function(delta) {
		if (self.activefile()==null) {return}
		if (self.listening != 0) {return}
		var yaya = self.editor.getValue()
		self.activefile().content(yaya);
		var amt = nthIndex(yaya,"\n",delta.start.row)+1+delta.start.column;
		var msg = delta.lines.join("\n")
		socket.emit('edit', {data:{
			delta:{amt:amt,msg:msg},
			path:self.activefile().path,
			projectId:projectid
		}});
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
			projectId:projectid
		}),
		success: function(data){
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
					self.children[self.children.length-1].radd(ra);
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
