



$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.search);
    return (results !== null) ? results[1] || 0 : false;
}
function nthIndex(str, pat, n){
    var L= str.length, i= -1;
    while(n-- && i++<L){
        i= str.indexOf(pat, i);
        if (i < 0) break;
    }
    return i;
}
function handshake(F) {
  var projectId = $.urlParam('projectId');
  socket = io(window.location.origin.replace(/^http/, 'ws'),{transports: ['polling']});//,{query:'loggeduser=user1'}
  socket.on('connect', function() {
    $.ajax("/join", {
      type: "POST",
      contentType: "application/json",
      data: ko.toJSON({
        projectId:projectId
      }),
      success: function(data){
        socket.emit('join',{projectId:projectId});
        socket.on('accept',F)
      }
    });
  });
}
ko.subscribable.fn.subscribeChanged = function (callback) {
  var savedValue = [...this.peek()];
  return this.subscribe(function (latestValue) {
    var oldValue = savedValue;
    savedValue = [...latestValue];
    console.log(latestValue);
    callback(latestValue, oldValue);
  });
};
function delimsplit(string,delim) {
  var insq = false;
  var indq = false;
  var inbrace = 0;
  var inparen = 0;
  var inbrack = 0;
  var las = 0
  var res = []
  for (var h=0;h<string.length;h++) {
    if (!indq && string.charAt(h) === "'") {insq = !insq}
    if (!insq && string.charAt(h) === '"') {indq = !indq}
    if (!insq && !indq) {
      if (string.charAt(h) === "[") {inbrack++;}
      if (string.charAt(h) === "]") {inbrack--;}
      if (string.charAt(h) === "(") {inparen++;}
      if (string.charAt(h) === ")") {inparen--;}
      if (string.charAt(h) === "{") {inbrace++;}
      if (string.charAt(h) === "}") {inbrace--;}
      if (inbrack == 0 && inbrace == 0 && inparen == 0) {
        if (h+delim.length<=string.length && string.slice(h,h+delim.length) === delim) {
          res.push(string.slice(las,h));
          las = h+delim.length;
          h+=delim.length-1;
        }
      }
    }
  }
  res.push(string.slice(las))
  return res;
};
function lengthof(props,syncs) {
  props = Object.assign({head:'{',tail:'}',delim:',',assign:':',keys:false},props)
  var oldmsglength = props.head.length+props.tail.length;
  var correction = 0
  for (const [key, value] of Object.entries(syncs)) {
    correction = -props.delim.length
    if (props.keys) {oldmsglength = oldmsglength+(""+key).length+2+props.assign.length+props.delim.length+value.oldmsglength;}
    else {oldmsglength = oldmsglength+props.delim.length+value.oldmsglength;}
  }
  oldmsglength += correction;
  return oldmsglength;
};
function reconstruct(props,syncs,changedInterval,vlaprops) {
  props = Object.assign({head:'{',tail:'}',delim:',',assign:':',keys:false},props)
  vlaprops = vlaprops==null?null:Object.assign({parser:null,serializer:null,objects:null,resync:null},vlaprops)
  if (vlaprops!=null && props.keys) {throw "Variable-length arrays cannot have keys."}
  changedInterval.endwith(lengthof(props,syncs),props.tail);
  changedInterval.beginwith(props.head)

  var rows = delimsplit(changedInterval.data,props.delim);
  if (vlaprops != null && syncs.length==0) {
    var sof = rows.map(vlaprops.parser);
    vlaprops.objects(sof)
    syncs.splice(0,0,...sof.map(vlaprops.serializer))
    vlaprops.resync();
    return
  }
  var a = changedInterval.start;
  var b = changedInterval.start+changedInterval.length;
  var bwow = 0;
  var first;
  var second;
  function updateentry(start,key,value,i,data) {
    if (data.length==0 && data.data.length==0) {return;}
    var nlength = (props.keys?key.length+2+props.assign.length:0)+value.oldmsglength
    if (vlaprops!=null && data.start==start && data.length==nlength) {
      var sob = data.data.length==0?[]:[vlaprops.parser(data.data)];
      vlaprops.objects.splice(i,1,...sob);
      value.disconnect();
      syncs.splice(i,1,...sob.map(vlaprops.serializer));
      vlaprops.resync();
      return
    }
    data.start-=start;
    if (props.keys) {
      data.beginwith('"'+key+'"'+props.assign);
    }
    value.endpointDown(data);
  }
  var i=0;
  for (const [key, value] of Object.entries(syncs)) {
    if (bwow<=a) {first  = i;}
    if (bwow-props.delim.length<b) {second  = i;}
    if (props.keys)  {bwow+=key.length+2+props.assign.length;}
    bwow += value.oldmsglength+props.delim.length;
    i++;
  }
  i=0;bwow=0;
  for (const [key, value] of Object.entries(syncs)) {
    var nlength = (props.keys?key.length+2+props.assign.length:0)+value.oldmsglength
    if (first == i && second == i) {
      updateentry(bwow,key,value,i,new ChangeInterval(a,b-a,rows[0]));
    } else if (first == i) {
      updateentry(bwow,key,value,i,new ChangeInterval(a,bwow+nlength-a,rows[0]));
    } else if (second == i) {
      updateentry(bwow,key,value,i,new ChangeInterval(bwow,b-bwow,rows[rows.length-1]));
    }
    bwow += nlength+props.delim.length;
    i++;
  }
  if (second+1-first != rows.length || rows.length>2) {
    if (vlaprops==null || props.keys) {throw "Formatting broken; cannot add or remove properties to objects."}
    if (second==first) {
      var sof = rows.slice(1).map(vlaprops.parser);
      vlaprops.objects.splice(first+1,0,...sof);
      syncs.splice(first+1,0,...sof.map(vlaprops.serializer));
      vlaprops.resync();
    } else {
      var sof = rows.slice(1,rows.length-1).map(vlaprops.parser);
      vlaprops.objects.splice(first+1,second-first-1,...sof);
      syncs.slice(first+1,second-(first+1)).forEach(function(item){item.disconnect();});
      syncs.splice(first+1,second-(first+1),...sof.map(vlaprops.serializer));
      vlaprops.resync();
    }
  }
};
function delimsplit(string,delim) {
  var insq = false;
  var indq = false;
  var inbrace = 0;
  var inparen = 0;
  var inbrack = 0;
  var las = 0
  var res = []
  for (var h=0;h<string.length;h++) {
    if (!indq && string.charAt(h) === "'") {insq = !insq}
    if (!insq && string.charAt(h) === '"') {indq = !indq}
    if (!insq && !indq) {
      if (string.charAt(h) === "[") {inbrack++;}
      if (string.charAt(h) === "]") {inbrack--;}
      if (string.charAt(h) === "(") {inparen++;}
      if (string.charAt(h) === ")") {inparen--;}
      if (string.charAt(h) === "{") {inbrace++;}
      if (string.charAt(h) === "}") {inbrace--;}
      if (inbrack == 0 && inbrace == 0 && inparen == 0) {
        if (h+delim.length<=string.length && string.slice(h,h+delim.length) === delim) {
          res.push(string.slice(las,h));
          las = h+delim.length;
          h+=delim.length-1;
        }
      }
    }
  }
  res.push(string.slice(las))
  return res;
};
function ChangeInterval(start,length,data) {
  var self = this;
  self.start = start;
  self.length = length;
  self.data = data;
  self.lendelta = function() {
    return (""+self.data).length-self.length;
  }
  self.end = function() {
    return self.start + self.length;
  }
  self.beginwith = function(prefix) {
    if (self.start<prefix.length) {
      prefix = prefix.slice(self.start);
      var mind = Math.min(self.data.length,prefix.length);
      if (prefix.slice(0,mind) !== self.data.slice(0,mind)) {
        throw "Formatting broken; expected "+prefix;
      }
      self.data = self.data.slice(mind);
      self.start += mind;
    }
    self.start -= prefix.length
  }
  self.endwith = function(length,postfix) {
    if (self.start+self.length>length-postfix.length) {
      console.log(self)
      console.log(length,postfix)
      var overlap = self.start+self.length-(length-postfix.length)
      if (!self.data.endsWith(postfix.slice(0,overlap))) {
        throw "Formatting broken; expected "+postfix;
      }
      self.data = self.data.slice(0,self.data.length-overlap);
      self.length -= overlap;
    }
  }
};
function SyncObservable(props) {
  var self = this;
  // self.endpointUp = props.endpointUp//the endpoint that gets hit when a range is changed. it should eventually go to the server.
  self.endpointDown = props.endpointDown;//the endpoint that gets hit when the server changes some data.
  self.evaluate = props.evaluate;
  self.oldmsglength = props.oldmsglength;
  self.synchronize = function(sessionId,path) {
    var md5buffer = self.evaluate();
    self.endpointUp = function(changedInterval) {
      //send data to the server here.
      console.log("sent to server:",changedInterval);
      var md5 = "placeholder md5 hash here."//take the hash of the md5buffer variable before we change it the line below
      md5buffer = md5buffer.slice(0,changedInterval.start)+changedInterval.data+md5buffer.slice(changedInterval.start+changedInterval.length);
      socket.emit('edit', {
        delta:{start:changedInterval.start,amt:changedInterval.length,msg:changedInterval.data},
        path:path,
        sessionId:sessionId,
        md5:md5
      });
    }
  };
  self.disconnect = function() {
    self.endpointUp = null;
    self.endpointDown = null;
  };
};
SyncObservable.fromObservable = function(props,obs) {
  var props = Object.assign({str:true},props)
  var ace = null;
  var tracking = true;
  var syncobs;
  var syncobs = new SyncObservable({
    endpointDown:function(changedInterval){
      tracking = false;
      if (props.str) {
        changedInterval.endwith(obs().length+2,'"');
        changedInterval.beginwith('"');
      }
      var rye = obs().toString().slice(0,changedInterval.start)+changedInterval.data+obs().toString().slice(changedInterval.start+changedInterval.length);
      if (props.str) {
        syncobs.oldmsglength = rye.length+2;
        obs(rye);
      } else {
        syncobs.oldmsglength = rye.length;
        obs(JSON.parse(rye));
      }
      tracking = true;
    },
    evaluate:function(){
      if (props.str) {return '"'+obs().toString()+'"';}
      else {return obs().toString();}
    },
    oldmsglength:obs().toString().length+(props.str?2:0)
  });
  syncobs.attach = function(aces) {
    if (aces == ace) {aceEnabled=true;ace.session.setValue(obs());return;}
    ace=aces;
    syncobs.disableUI();
    var aceEnabled = true;
    ace.session.setValue(obs());
    syncobs.disableUI = function() {aceEnabled=false;}
    // syncobs.enableUI();
    ace.session.on('change', function(delta) {
      console.log("change edit(B)",delta,tracking,aceEnabled)
      if (!tracking) {return;}
      if (!aceEnabled) {return}
      console.log("change edit",delta)
      var yaya = ace.getValue()
      tracking = false;
      obs(yaya);
      tracking = true;
      var start = nthIndex(yaya,"\n",delta.start.row)+1+delta.start.column;
      var end   = nthIndex(yaya,"\n",delta.end.row)+1+delta.end.column;
      var msg = delta.lines.join("\n");

      var ninterval;
      if (delta.action == 'insert') {
        ninterval = new ChangeInterval(start,0,msg);
      } else if (delta.action == 'remove') {
        ninterval = new ChangeInterval(start,end-start,"");
      }

  // # if edit['mode'] == 'insert':
  // #   book.content = book.content[:edit['delta']['amt']]+edit['delta']['msg']+book.content[edit['delta']['amt']:]
  // # elif edit['mode'] == 'remove':
  // #   book.content = book.content[:edit['delta']['amt']]+book.content[edit['delta']['amt']+len(edit['delta']['msg']):]


      syncobs.endpointUp(ninterval);
      syncobs.oldmsglength+=ninterval.lendelta();// = newValue.toString().length+(props.str?2:0);
    });
  }
  syncobs.disableUI = function() {}
  obs.subscribe(function(newValue){
    if (!tracking) {return;}
    if (ace!=null) {
      tracking = false;
      ace.session.setValue(newValue);
      tracking = true;
      return;
    }
    var ntext;
    if (props.str) {ntext = '"'+newValue.toString()+'"';}
    else {ntext = newValue.toString();}
    syncobs.endpointUp(new ChangeInterval(0,syncobs.oldmsglength,ntext));
    syncobs.oldmsglength = newValue.toString().length+(props.str?2:0);
  });
  return syncobs;
};
SyncObservable.fromjson = function(props,syncs) {
  var props = Object.assign({head:'{',tail:'}',delim:',',assign:':',keys:true},props)
  var syncobs;
  syncobs = new SyncObservable({
    endpointDown:function(changedInterval) {//towards data.
      syncobs.oldmsglength+=changedInterval.lendelta();
      reconstruct(props,syncs,changedInterval);
    },
    evaluate:function() {
      var res = props.head;
      for (const [key, value] of Object.entries(syncs)) {
        if (res.length>props.head.length) {res = res+props.delim;}
        if (props.keys) {res = res + '"'+key+'"'+props.assign}
        res = res+value.evaluate();
      }
      return res+props.tail;
    },
    oldmsglength:lengthof(props,syncs)
  });
  syncobs.enableUI  = function() {for (const [key, value] of Object.entries(syncs)) {value.enableUI();}}
  syncobs.disableUI = function() {for (const [key, value] of Object.entries(syncs)) {value.disableUI();}}
  var oldlen = props.head.length-props.delim.length;
  var prevs = [];
  for (const [key, value] of Object.entries(syncs)) {
    (function() {
      if (props.keys) {oldlen = oldlen + (""+key).length+2+props.delim.length+props.assign.length;}
      else {oldlen = oldlen + props.delim.length}
      var closure = oldlen;
      var closeprevs = [...prevs];
      prevs.push(value);
      value.endpointUp = function(changedInterval) {//towards server.
        changedInterval.start += closure;
        closeprevs.forEach(function(item){changedInterval.start += item.oldmsglength;})
        syncobs.endpointUp(changedInterval);
        syncobs.oldmsglength += changedInterval.lendelta();
      }
    })();
  }
  return syncobs;
};
SyncObservable.fromcsv = function(props,objects,parser,serialize) {
  var props = Object.assign({head:'[',tail:']',delim:','},props)
  var syncs = objects().map(serialize);
  var tracking = true;
  var syncobs;
  function resync() {
    var sof = props.head.length-props.delim.length;
    var prevs = [];
    syncs.forEach(function(item) {
      sof = sof+props.delim.length;
      var closure = sof;
      var closeprevs = [...prevs];
      prevs.push(item);
      item.endpointUp = function(changedInterval) {//to server
        changedInterval.start += closure;
        closeprevs.forEach(function(item2){changedInterval.start += item2.oldmsglength;})
        syncobs.endpointUp(changedInterval);
        syncobs.oldmsglength += changedInterval.lendelta();
      }
    });
  };
  syncobs = new SyncObservable({
    endpointDown:function(changedInterval) {
      tracking = false;
      syncobs.oldmsglength+=changedInterval.lendelta();
      reconstruct(props,syncs,changedInterval,{
        parser:parser,
        serializer:serialize,
        objects:objects,
        resync:resync
      });
      tracking = true;
    },
    evaluate:function() {
      var res = props.head;
      syncs.forEach(function(item) {
        if (res.length>1) {res = res+props.delim;}
        res = res + item.evaluate();
      });
      return res+props.tail;
    },
    oldmsglength:lengthof(props,syncs)
  });
  syncobs.enableUI  = function() {syncs.forEach(function(value){value.enableUI();});}
  syncobs.disableUI = function() {syncs.forEach(function(value){value.disableUI();});}
  objects.subscribeChanged(function(newValue,oldValue){//to server
    if (!tracking) {return;}
    var i = 0;
    var j = 0;
    var missi = 0;
    var missj = 0;
    function commit(i,j) {
      if (i>missi || j>missj) {
        var begin = props.head.length;
        var run = 0
        // if (j == oldValue.length)
        for (var k=0;k<missj;k++) {begin += syncs[k].oldmsglength+props.delim.length;}
        for (var k=missj;k<j;k++) {run   += syncs[k].oldmsglength+props.delim.length;}
        if (oldValue.length>0) {
          if (missj == oldValue.length) {begin -= props.delim.length;}
          else if (j == oldValue.length) {
            if (i==missi && oldValue.length>1) {begin = begin - props.delim.length;}
            else {run = run - props.delim.length;}
          }
        }
        var gpp = newValue.slice(missi,i).map(serialize);
        syncs.slice(missj,j).forEach(function(item){item.disconnect()});
        syncs = syncs.slice(0,missj).concat(gpp).concat(syncs.slice(j));
        resync();
        var newtext = gpp.map(function(p){return p.evaluate();}).join(props.delim);
        if (missj == oldValue.length && missj>0) {newtext = ","+newtext;}
        if (i-missi>0 && j != oldValue.length) {newtext = newtext+",";}
        changedInterval = new ChangeInterval(begin,run,newtext)
        syncobs.endpointUp(changedInterval);
        syncobs.oldmsglength += changedInterval.lendelta();
      }
    }
    while (j<oldValue.length) {
      while (i<newValue.length) {
        while (j<oldValue.length && i<newValue.length && newValue[i] == oldValue[j]) {
          commit(i,j);
          j++;i++;
          missi = i;missj = j;
        }
        if (i<newValue.length) {i++};
      }
      if (j<oldValue.length) {
        j++;
        i = missi;
      }
    }
    commit(newValue.length,oldValue.length);
  });
  resync();
  return syncobs;
};














