
var justice = new AppViewModel();
var VF = Vex.Flow;

function drawEdge(selected,doucided,b,a,darcolor) {
  if (darcolor == null) {darcolor = "black"}
  var sl = Math.sqrt((a.y-b.y)*(a.y-b.y)+(a.x-b.x)*(a.x-b.x));
  if (sl == 0 || isNaN(sl)) {return "";}
  var x0 = b.x + (a.y-b.y)*10/sl + (a.x-b.x)*20/sl;
  var y0 = b.y - (a.x-b.x)*10/sl + (a.y-b.y)*20/sl;
  var x1 = b.x - (a.y-b.y)*10/sl + (a.x-b.x)*20/sl;
  var y1 = b.y + (a.x-b.x)*10/sl + (a.y-b.y)*20/sl;
  var arrow = "<polyline points='"+x1+","+y1+" "+b.x+","+b.y+" "+x0+","+y0+"' fill='"+darcolor+"' stroke='white' stroke-width='5=2' closed='true'/>";
  var ostyle = "stroke-width='2'";
  if (selected) {
    ostyle = "stroke-width='5' stroke-dasharray='5,5'";
  }
  if (doucided) {
    var dx = (a.y-b.y)*.1 + (a.x+b.x)*.5;
    var dy = (a.y+b.y)*.5 - (a.x-b.x)*.1;
    return "<path d='M "+a.x+" "+a.y+" Q "+dx+" "+dy+" "+b.x+" "+b.y+"' fill='none' stroke='white' stroke-width='5' /> \
            <path d='M "+a.x+" "+a.y+" Q "+dx+" "+dy+" "+b.x+" "+b.y+"' fill='none' stroke='"+darcolor+"' "+ostyle+"/>"+arrow;
  } else {
    return "<line x1='"+a.x+"' x2='"+b.x+"' y1='"+a.y+"' y2='"+b.y+"' stroke='white' stroke-width='5'/> \
            <line x1='"+a.x+"' x2='"+b.x+"' y1='"+a.y+"' y2='"+b.y+"' stroke='"+darcolor+"' "+ostyle+"/>"+arrow;
  }
}
function drawstave(uuid,voices) {
    var div = document.getElementById("stave"+uuid)
    if (div == null) {return;}
    $(div).empty();
    var width = $(div).width();

    var renderer = new VF.Renderer(div, VF.Renderer.Backends.SVG);
    renderer.resize(width, 500);
    var context = renderer.getContext();
    context.setFont("Arial", 10, "").setBackgroundFillStyle("#eed");
    var stave = new VF.Stave(10, 10, width-20);

    stave.addClef("treble");//.addTimeSignature("4/4");
    voices.forEach(function(notes) {
      var voice = new VF.Voice({num_beats: 4,  beat_value: 4});
      voice.addTickables(notes);
      var formatter = new VF.Formatter().joinVoices([voice]).format([voice], width-20);
      voice.draw(context, stave);
    });
    stave.setContext(context).draw();
}

function tonesof(notes,octchange,duration){

  var jamba = new VF.StaveNote({
    clef: "treble",
    keys:notes.map(function(x) {
      var y = parseInt(""+x.numeric());
      var postfix = 4+Math.floor(y/12)+octchange;
      return ["c","c#","d","d#","e","f","f#","g","g#","a","a#","b"][y%12]+"/"+postfix;
    }),
    duration:duration
  });
  notes.map(function(x,ind) {
    if ([false,true,false,true,false,false,true,false,true,false,true,false][parseInt(""+x.numeric())%12]) {
      jamba.addAccidental(ind,new VF.Accidental("#"));
    }
  })
  return jamba
};



var staveuuid = 0;
function Edge(props) {
  var self = this;
  self.a = props.a;
  self.b = props.b;
  self.onload = function() {}
  self.isedge = true;
  self.weight = ko.observable(props.weight|50);
  self.octavechange = ko.observable(props.octavechange|0);
  self.doucided = ko.observable(false);
  self.selected = ko.observable(false);
  self.editingname = ko.observable(false);
  self.uuid = staveuuid++;
  self.name = ko.computed(function() {
    return self.a.name()+"->"+self.b.name();
  });
  self.beginEditName = function() {};
  self.svg = ko.computed(function() {
    var a = self.a.pos();
    var b = self.b.pos();
    var amt = scalevec(justice.radius(),normalize(subtractvec(a,b)))
    var c = addvec(b,amt);
    var d = subtractvec(a,amt);
    var darcolor = "black";
    if (self.octavechange()>0) {darcolor = "#800000";}
    if (self.octavechange()<0) {darcolor = "#003366";}
    return drawEdge(self.selected(),self.doucided(),c,d,darcolor);
  });
  self.disto = function(pos) {
    var a = self.b.pos();
    var b = self.a.pos();
    var amt = scalevec(justice.radius(),normalize(subtractvec(a,b)))
    var c = addvec(b,amt);
    var d = subtractvec(a,amt);

    if (self.doucided()) {
      var k = {'x':(c.y-d.y)*.1 + (c.x+d.x)*.5,'y':(c.y+d.y)*.5 - (c.x-d.x)*.1};
      var djdj = Math.sqrt(dist2quadratic(pos,c,k,d));
      return djdj

    } else {
      return Math.sqrt(dist2line(pos,c,d));
    }
  };
  self.onload = function() {
    voice = []
    // console.log(self.octavechange());
    if (self.a.notes().length != 0) {voice.push(tonesof(self.a.notes(),0,"h"));}
    else {voice.push(new VF.StaveNote({clef: "treble", keys:["c/5"], duration: "hr" }));}
    if (self.b.notes().length != 0) {voice.push(tonesof(self.b.notes(),parseInt(""+self.octavechange()),"h"));}
    else {voice.push(new VF.StaveNote({clef: "treble", keys:["c/5"], duration: "hr" }));}
    drawstave(self.uuid,[voice]);
    // console.log("completed")
  };
  // self.a.notes.subscribe(self.onload);
  // self.b.notes.subscribe(self.onload);
  self.octavechange.subscribe(self.onload);


};


function Note(num) {
  var self = this;
  self.numeric = ko.observable(num);

}


function Node(props) {
  var self = this;
  self.name = ko.observable(props.name);
  self.editingname = ko.observable(false);
  self.isedge = false;
  self.selected = ko.observable(false);
  self.x = ko.observable(props.x);
  self.y = ko.observable(props.y);
  self.uuid = staveuuid++;
  self.notes = ko.observableArray((props.notes==undefined?[]:props.notes).map(function(item){return new Note(item)}));
  $(window).resize(function() {self.notes.notifySubscribers();});
  self.onload   =  function() {self.notes.notifySubscribers();}
  self.selected.subscribe(function(){self.editingname(false);})
  self.name.subscribe(function(chord) {
    var major_scale = [1, 3, 5, 6, 8, 10, 12, 13];
    var index = "cdefgab".indexOf(chord.toLowerCase().charAt(0))
    self.notes([]);

    if (index != -1) {
      self.notes.push(new Note(major_scale[index]));
    } else if (chord.toLowerCase().indexOf("n")!=-1 && !chord.toLowerCase().indexOf("i")!=-1 && !chord.toLowerCase().indexOf("v")!=-1 && !chord.toLowerCase().indexOf("r")!=-1) { // adfsadf = new Note("N6")
      self.notes.push(new Note(major_scale[1] - 1));
    }
    var invert = 0;
    //setting the invert property to the type of inversion based on the last two characters and if they contain "ii"
    // console.log(chord.length)
    if (chord.length >= 2) {
      console.log(chord.substring(chord.length - 1));
      if (chord.substring(chord.length - 1) === ("i")) {
        invert = 1;
      } else if (chord.substring(chord.length - 2) === ("ii")) {
        invert = 2;
      }
    }

    var root = self.notes()[0].numeric();
    var minor = chord.substring(0,1).toLowerCase() === (chord.substring(0,1));

    self.notes.push(new Note(minor ? root + 3 : root + 4));
    self.notes.push(new Note(root + 7));
    if(chord.indexOf("7")!=-1) { self.notes.push(new Note(minor ? root + 10 : root + 11));}
    if(chord.indexOf("9")!=-1) { self.notes.push(new Note(minor ? root + 14 : root + 14));}

    //invert the chords
    if (invert == 1) {
      self.notes()[0].numeric(self.notes()[0].numeric() + 12);
    } else if (invert == 2) {
      self.notes()[0].numeric(self.notes()[0].numeric() + 12);
      self.notes()[1].numeric(self.notes()[1].numeric() + 12);
    }
    self.notes.notifySubscribers();
  });
  self.reinventor = ko.computed(function() {
    var voices = []
    // console.log("reinvented");
    // self.notes().forEach(function(item){console.log(item());});
    if (self.notes().length != 0) {
      voices.push([tonesof(self.notes(),0,"w")]);
    } else {
      voices.push([new VF.StaveNote({clef: "treble", keys:["c/5"], duration: "wr" })]);
    }
    drawstave(self.uuid,voices);
  });
  self.pos = function() {return {'x':self.x(),'y':self.y()};}

  self.beginEditName = function() {
    self.editingname(true);
    $("body").on("click", function(){
      self.editingname(false);
      $("body").off("click");
    });
  };
  self.svg = ko.computed(function() {
    var stwidth = '3';
    if (self.selected()) {stwidth = '6';}
    return "\
      <circle cx='"+self.x()+"' cy='"+self.y()+"' r='"+justice.radius()+"' fill='white' stroke='black' stroke-width='"+stwidth+"'/>\
      <text x='"+self.x()+"' y='"+self.y()+"' text-anchor='middle' fill='black' font-size='20px' font-family='Arial' dy='.3em'>"+self.name()+"</text>";
  });
  self.disto = function(pos) {
    return Math.sqrt(dist2(self.pos(),pos))-justice.radius();
  };

  self.remove = function(item) {
    self.notes.remove(item);
  };
  self.addnew = function() {
    self.notes.push(new Note(0));
  };
};


//remember which tool youre on and display it to the user
//allow the user to edit which notes are in each chord, maybe specify which one is the root
//save and load data
//make the delete button work



function AppViewModel() {
  var self = this;
  self.activelayer = ko.observable(null);
  self.nodes = ko.observableArray([]);
  self.edges = ko.observableArray([]);
  self.pos = null;
  self.spos = ko.observable(null);
  self.mode = ko.observable("edit");
  self.radius = ko.observable(30);

  // self.enabled = ko.observable(null);
  self.bloburl = ko.observable(null);

  self.svg = ko.computed(function() {
    var res = "";
    self.nodes().forEach(function(item){
      res = item.svg() + res;
    });
    self.edges().forEach(function(item){
      res = item.svg() + res;
    });
    //add the edge that youre currently drawing...
    if (self.mode() === 'draw' && self.spos()!=null && self.activelayer()!= null && !self.activelayer().isedge) {
      var amt = scalevec(self.radius(),normalize(subtractvec(self.spos(),self.activelayer().pos())))
      var c = addvec(self.activelayer().pos(),amt);
      res = res + drawEdge(true,false,self.spos(),c);
    }
    return res;
  });
  self.activelayer.subscribe(function(){
    //update all paths and nodes that believe they are selected...

    self.nodes().forEach(function(item){
      item.selected(item == self.activelayer());
    });
    self.edges().forEach(function(item){
      item.selected(item == self.activelayer());
    });
  });
  self.edges.subscribe(function() {
    //update all edges that believe they are shared...
    self.edges().forEach(function(item1){
      var duplicate = false;
      self.edges().forEach(function(item2){
        if (item1.a == item2.b && item2.a == item1.b) {duplicate=true;}
      });
      item1.doucided(duplicate);
    });
  })
  draginside($("#target"),function(x,y){
    self.spos(null);
    self.pos = {'x':x,'y':y};
    var closest = null;
    var heur = 9999999;
    self.nodes().forEach(function(item){
      var h = item.disto(self.pos);
      if (h<heur) {
        heur = h;
        closest = item;
      }
    });
    self.edges().forEach(function(item){
      var h = item.disto(self.pos);
      if (h<heur) {
        heur = h;
        closest = item;
      }
    });
    self.activelayer(null);
    if (heur<8) {
      if (self.mode() === 'delete') {
        self.nodes.remove(closest);
        self.edges.remove(closest);
        for (var i=self.edges().length-1;i>=0;i--) {
          if (self.edges()[i].a == closest || self.edges()[i].b == closest) {
            self.edges.remove(self.edges()[i]);
          }
        }
      } else {
        self.activelayer(closest);
      }
    } else if (self.mode() === 'add') {
      var i = new Node({name:'new',x:x,y:y});
      self.nodes.push(i);
      self.activelayer(i);
    }
  },function(x,y){
    if (self.activelayer()==null) {return}
    if (!self.activelayer().isedge) {
      if (self.mode() === 'draw') {
        self.spos({'x':x,'y':y});
      } else {
        self.activelayer().x(self.activelayer().x()+x-self.pos.x);
        self.activelayer().y(self.activelayer().y()+y-self.pos.y);
        self.pos = {'x':x,'y':y};
      }
    }
  },function(x,y){
    var pos = {'x':x,'y':y};
    if (self.mode() === 'draw') {
      var closest = null;
      var heur = 9999999;
      self.nodes().forEach(function(item){
        var h = item.disto(pos);
        if (h<heur) {
          heur = h;
          closest = item;
        }
      });
      if (heur<8 && closest != self.activelayer()) {
        //if edge already exists, don't add...
        //dont add an edge to yourself...
        var valid = true;
        self.edges().forEach(function(item){
          if (item.a == self.activelayer() && item.b == closest) {valid=false;}
        });
        if (valid) {
          var nedg = new Edge({a:self.activelayer(),b:closest});
          self.edges.push(nedg);
          self.activelayer(nedg);
        }
      }
    }
    self.spos(null);
  });
  self.deleteObject = function() {
    self.nodes.remove(self.activelayer());
    self.edges.remove(self.activelayer());
    for (var i=self.edges().length-1;i>=0;i--) {
      if (self.edges()[i].a == self.activelayer() || self.edges()[i].b == self.activelayer()) {
        self.edges.remove(self.edges()[i]);
      }
    }
    self.activelayer(null);
  }
  self.addMode = function() {
    self.mode('add');
  }
  self.drawMode = function() {
    self.mode('draw');
  }
  self.editMode = function() {
    self.mode('edit');
  }
  self.deleteMode = function() {
    self.mode('delete');
  }


  self.fileUpload = function(data,e) {
    var file    = e.target.files[0];
    var reader  = new FileReader();
    reader.onloadend = function (onloadend_e) {
      var result = JSON.parse(atob(reader.result.replace(/^.+,/g,"")));
      self.nodes(result.nodes.map(function(item){return new Node(item);}));
      self.edges(result.edges.map(function(item){return new Edge({
        weight:item.weight,
        octavechange:item.octavechange,
        a:self.nodes()[parseInt(item.a)],
        b:self.nodes()[parseInt(item.b)]
      });}));
      self.activelayer(null);
    };
    if(file) {reader.readAsDataURL(file);}
  };





  self.reinventor = ko.computed(function() {
    // enabled(true);
    var text = '{\n\t"nodes":[\n\t\t'+
    self.nodes().map(function(item){
      return '{"name":"'+item.name()+'","x":'+item.x()+',"y":'+item.y()+',"notes":['+
      item.notes().map(function(element){
        return element.numeric();
      }).join(",")+']}'
    }).join(",\n\t\t")+'\n\t],"edges":[\n\t\t'+
    self.edges().map(function(item){
      return '{"weight":'+item.weight()+',"octavechange":'+item.octavechange()+',"a":'+self.nodes().indexOf(item.a)+',"b":'+self.nodes().indexOf(item.b)+'}';
    }).join(",\n\t\t")+'\n\t]\n}';

    if (self.bloburl()!=null) {
      window.URL.revokeObjectURL(self.bloburl());
    }
    var bb = new Blob([text], {type: "application/json"});
    self.bloburl(window.URL.createObjectURL(bb));
  });




  // dblclickinside($("#target"),function(x,y){self.activelayer().doubleclick(x,y);});
  // draginside($("#timeline"),function(x,y){
  // },function(x,y){
  // },function(x,y){
  // });

  // scrollinside($("#target"));
}
ko.applyBindings(justice);






