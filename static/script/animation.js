

var justice = new AppViewModel();


function rendercontrolpoint(point) {
  return "\
    <circle cx='"+point.x+"' cy='"+point.y+"' r='5' fill='white' stroke='black' strokewidth='3'/>\
    <line x1='"+(point.x-8)+"' x2='"+(point.x+8)+"' y1='"+point.y+"' y2='"+point.y+"' stroke='black' stroke-width='3'/> \
    <line x1='"+point.x+"' x2='"+point.x+"' y1='"+(point.y-8)+"' y2='"+(point.y+8)+"' stroke='black' stroke-width='3'/> "

};
function renderdottedcontrol(point1,point2) {
  return "<line x1='"+point1.x+"' x2='"+point2.x+"' y1='"+point1.y+"' y2='"+point2.y+"' stroke='black' stroke-width='5'/> \
          <line x1='"+point1.x+"' x2='"+point2.x+"' y1='"+point1.y+"' y2='"+point2.y+"' stroke='white' stroke-width='5' stroke-dasharray='5,5'/>"
};




function Layerelem(name) {
  var self = this;
  self.name = ko.observable(name);
  self.editingname = ko.observable(false);
  self.hascolors = false
  self.beginEditName = function() {
    self.editingname(true);
    $("body").on("click", function(){
      self.editingname(false);
      $("body").off("click");
    });
  };
  self.takefocus = function() {
    justice.activelayer(self);
  };
  self.deletelayer = function() {}
  self.enddrag = function(parent) {parent.adopt(self);}
  self.compubounds = function(){
    var bou = self.bounds();
    if (bou[2]<0) {return "0 0 0 0"}
    return ""+(bou[0]-8)+" "+(bou[1]-8)+" "+(bou[2]-bou[0]+16)+" "+(bou[3]-bou[1]+16)
  }
  self.applytransform = function(tra) {
    // console.log(combinetransform(tra,invtransform(tra)))
    // console.log(combinetransform(invtransform(tra),tra))
    self.controlpoints(self.controlpoints().map(function(item){return applytransform(item,tra)}));
  }
  self.doubleclick = function(x,y){}
  self.getglobaltransform = function(elem,downmat) {}
};
function Colorlayer(name) {
  var self = this;
  Layerelem.bind(self)(name);
  self.hascolors = true;
  self.fillcolor = ko.observable("#FFA07A");
  self.strokecolor = ko.observable("#B22222");
  self.strokewidth = ko.observable(0);
  self.deformable  = ko.observable(false);
  self.closed = ko.observable(false);
  self.filled = ko.observable(false);
};
function Grouping(name,children) {
  var self = this;
  Layerelem.bind(self)("new group");
  self.type = "grouping";
  self.expanded = ko.observable(false);
  self.children = ko.observableArray(children==undefined?[]:children);
  self.controlpoints = ko.observableArray([{'x':300,'y':300},{'x':340,'y':300},{'x':300,'y':260},{'x':340,'y':260}]);
  self.touchcontrol = function(index,pos) {
    var root = self.controlpoints()[0]
    if (index == 0) {
      self.controlpoints()[0] = pos
      self.controlpoints()[1] = {'x':pos.x-root.x+self.controlpoints()[1].x,'y':pos.y-root.y+self.controlpoints()[1].y};
      self.controlpoints()[2] = {'x':pos.x-root.x+self.controlpoints()[2].x,'y':pos.y-root.y+self.controlpoints()[2].y};
      self.controlpoints()[3] = {'x':pos.x-root.x+self.controlpoints()[3].x,'y':pos.y-root.y+self.controlpoints()[3].y};
    } else if (index == 3) {
      var oldr = {'x':self.controlpoints()[3].x-root.x,'y':self.controlpoints()[3].y-root.y}
      var newr = {'x':pos.x-root.x,'y':pos.y-root.y}
      // var comat = invtransform([oldr,perpvec(oldr),{'x':0,'y':0}])
      var comat = combinetransform(invtransform([perpvec(oldr),oldr,root]),[perpvec(newr),newr,root]);
      self.controlpoints()[1] = applytransform(self.controlpoints()[1],comat);
      self.controlpoints()[2] = applytransform(self.controlpoints()[2],comat);
      self.controlpoints()[3] = pos;
    } else {
      self.controlpoints()[index] = pos;
      self.controlpoints()[3] = {
        'x':self.controlpoints()[1].x+self.controlpoints()[2].x-root.x,
        'y':self.controlpoints()[1].y+self.controlpoints()[2].y-root.y,
      };
    }
    self.controlpoints.valueHasMutated();
  }
  self.getglobaltransform = function(elem,downmat) {
    downmat = combinetransform(downmat,self.extracttra());
    if (elem == self) return downmat;
    for (let item of self.layers()) {
      var k = item.getglobaltransform(elem,downmat);
      if (k != null) {return k}
    }
  }
  self.extracttra = function() {
    var root = self.controlpoints()[0]
    var basis1 = scalevec(1/40,subtractvec(self.controlpoints()[1],root));
    var basis2 = scalevec(-1/40,subtractvec(self.controlpoints()[2],root));
    var gets = [basis1,basis2,subtractvec(root,mulmatrix({'x':300,'y':300},[basis1,basis2]))];
    console.log("--->>>",gets);
    return gets;
  }
  self.children.subscribeChanged(function(next,prev){
    var tra = self.extracttra();
    var invtra = invtransform(tra);

    next.forEach(function(item){
      if (!prev.includes(item)) {
        console.log("applying backward; thing is coming")
        item.applytransform(invtra);
      }
    });
    prev.forEach(function(item){
      if (!next.includes(item)) {
        console.log("applying forward; thing is leaving")
        item.applytransform(tra);
      }
    });
  });

  self.getsvg = function(indown) {
    var tra = self.extracttra();
    if (indown == undefined) {
      downmat = tra;
      indown = identitytra();
    } else downmat = combinetransform(indown,tra);
    var res = "";
    self.children().forEach(function(item){
      res = item.getsvg(downmat) + res;
    });
    res = res+rendercontrolpoint(applytransform(self.controlpoints()[0],indown))+
              rendercontrolpoint(applytransform(self.controlpoints()[1],indown))+
              rendercontrolpoint(applytransform(self.controlpoints()[2],indown))+
              rendercontrolpoint(applytransform(self.controlpoints()[3],indown));
    return res;
  }
  self.svg = ko.computed(self.getsvg);
  self.editorsvg = ko.computed(function(){
    var res = renderdottedcontrol(self.controlpoints()[0],self.controlpoints()[1])+
              renderdottedcontrol(self.controlpoints()[0],self.controlpoints()[2])+
              rendercontrolpoint(self.controlpoints()[0])+
              rendercontrolpoint(self.controlpoints()[1])+
              rendercontrolpoint(self.controlpoints()[2])+
              rendercontrolpoint(self.controlpoints()[3]);
    return res;
  });
  self.deletelayer = function(lay) {
    self.children.remove(lay);
    self.children().forEach(function(item) {
      item.deletelayer(lay);
    });
  };
  self.adopt = function(old) {
    if (old == justice.dragginglayer) {return}
    if (justice.dragginglayer != null) {
      var nindex = self.children().indexOf(old);
      justice.deletelayer(justice.dragginglayer);
      self.children.splice(nindex,0,justice.dragginglayer);
      justice.dragginglayer = null;
    }
  };
  self.enddrag = function(parent) {
    if (justice.dragginglayer == self) {return;}
    if (self.children().length > 0) {return parent.adopt(self);}
    if (justice.dragginglayer != null) {
      justice.deletelayer(justice.dragginglayer);
      self.children.push(justice.dragginglayer);
      justice.dragginglayer = null;
    }
  }
  self.bounds = function(indown){
    var tra = self.extracttra();
    if (indown == undefined) {
      downmat = tra;
      indown = identitytra();
    } else downmat = combinetransform(indown,tra);
    var fuk = [999999,999999,-999999,-999999];
    self.children().forEach(function(item) {
      var bou = item.bounds(downmat);
      if (bou[0]<fuk[0]) {fuk[0]=bou[0];}
      if (bou[1]<fuk[1]) {fuk[1]=bou[1];}
      if (bou[2]>fuk[2]) {fuk[2]=bou[2];}
      if (bou[3]>fuk[3]) {fuk[3]=bou[3];}
    });
    return fuk;
  };
};
function Polylayer(name) {
  var self = this;
  Colorlayer.bind(self)("new polygon");
  self.type = "polylayer";
  self.controlpoints = ko.observableArray([{'x':400,'y':400},{'x':500,'y':400},{'x':400,'y':500}]);
  self.lasttouched = null;
  self.touchcontrol = function(index,pos) {
    self.controlpoints()[index] = pos;
    self.controlpoints.valueHasMutated();
  }
  self.getsvg = function(downmat) {
    if (downmat == undefined) downmat = identitytra();
    var res = "";
    if (self.closed) {res = "<polyline points='";}
    else {res = "<polygon points='";}
    self.controlpoints().forEach(function(item){
      res=res+stringvec(applytransform(item,downmat))
    });
    // if (self.closed() && self.controlpoints().length>0) {res=res+stringvec(applytransform(self.controlpoints()[0],downmat));}
    res = res + "'";
    if (!self.filled()) {res = res+"fill='none'";}
    else {res = res+"fill='"+self.fillcolor()+"'"}
    res = res+"stroke='"+self.strokecolor()+"'"
    res = res+"stroke-width='"+self.strokewidth()+"'"
    return res+"/>"
  }
  self.svg = ko.computed(self.getsvg);
  self.editorsvg = ko.computed(function(){
    var res = "";
    self.controlpoints().forEach(function(item){
      res = res + rendercontrolpoint(item);
    });
    return res;
  });
  self.bounds = function(downmat){
    if (downmat == undefined) downmat = identitytra();
    var fuk = [999999,999999,-999999,-999999];
    self.controlpoints().forEach(function(unit) {
      var item = applytransform(unit,downmat);
      if (item.x<fuk[0]) {fuk[0]=item.x;}
      if (item.y<fuk[1]) {fuk[1]=item.y;}
      if (item.x>fuk[2]) {fuk[2]=item.x;}
      if (item.y>fuk[3]) {fuk[3]=item.y;}
    });
    return fuk;
  };
  self.doubleclick = function(x,y){
    var pos = {'x':x,'y':y}
    var clindex = null;
    // var closest = null;
    var heur = 99999999;

    self.controlpoints().forEach(function(w,index){
      var v = self.controlpoints()[(index+1)%self.controlpoints().length];
      var t = ((pos.x - v.x) * (w.x - v.x) + (pos.y - v.y) * (w.y - v.y)) / dist2(v, w);
      if (t<0 || t>1) {return}
      var jhg = {'x':v.x+t*(w.x-v.x),'y':v.y+t*(w.y-v.y)}

      var h = dist2(jhg,pos);
      if (h<heur) {
        heur = h;
        // closest = jhg;
        clindex = index;
      }
    });
    if (clindex == null) {return;}
    if (heur > 81) {return;}
    self.controlpoints.splice(clindex+1,0,pos);
  }
}


function Bezlayer(name) {
  var self = this;
  Colorlayer.bind(self)("new bezier");
  self.type = "bezlayer";
  self.controlpoints = ko.observableArray([{'x':400,'y':400},{'x':500,'y':400},{'x':500,'y':500},{'x':400,'y':500}]);
  self.closed.subscribe(function(nowclosed){
    if (nowclosed && self.controlpoints().length%3 == 1) {
      var olp = self.controlpoints()[self.controlpoints().length-1];
      var nep = self.controlpoints()[0];
      self.controlpoints.push({'x':(2.0*olp.x+nep.x)/3.0,'y':(2.0*olp.y+nep.y)/3.0});
      self.controlpoints.push({'x':(olp.x+2.0*nep.x)/3.0,'y':(olp.y+2.0*nep.y)/3.0});
    } else if (!nowclosed && self.controlpoints().length%3 == 0) {
      self.controlpoints.splice(self.controlpoints().length-2,2)
    } else {
      console.log("broke");
    }
  });
  self.touchcontrol = function(index,pos) {
    self.controlpoints()[index] = pos;
    self.controlpoints.valueHasMutated();
  }
  self.getsvg = function(downmat) {
    if (downmat == undefined) downmat = identitytra();
    var res = "<path d='M "+stringvec(applytransform(self.controlpoints()[0],downmat));
    for (var i=1;i+2<self.controlpoints().length;i+=3) {
      res = res+"C "+
        stringvec(applytransform(self.controlpoints()[i],downmat))+
        stringvec(applytransform(self.controlpoints()[i+1],downmat))+
        stringvec(applytransform(self.controlpoints()[i+2],downmat));
    }
    var end = self.controlpoints().length;
    if (self.closed()) {
      res = res+"C "+
        stringvec(applytransform(self.controlpoints()[end-2],downmat))+
        stringvec(applytransform(self.controlpoints()[end-1],downmat))+
        stringvec(applytransform(self.controlpoints()[0],downmat));
    }
    res = res + "'";
    if (!self.filled()) {res = res+"fill='none'";}
    else {res = res+"fill='"+self.fillcolor()+"'"}
    res = res+"stroke='"+self.strokecolor()+"'"
    res = res+"stroke-width='"+self.strokewidth()+"'"

    return res+"/>"
  }
  self.svg = ko.computed(self.getsvg);
  self.editorsvg = ko.computed(function(){
    var res = "";
    for (var i=0;i+3<self.controlpoints().length;i+=3) {
      res = res + renderdottedcontrol(self.controlpoints()[i],self.controlpoints()[i+1])
      res = res + renderdottedcontrol(self.controlpoints()[i+2],self.controlpoints()[i+3])
    }
    var end = self.controlpoints().length;
    if (self.closed()) {
      res = res + renderdottedcontrol(self.controlpoints()[end-3],self.controlpoints()[end-2])
      res = res + renderdottedcontrol(self.controlpoints()[end-1],self.controlpoints()[0])
    }
    self.controlpoints().forEach(function(item){
      res = res + rendercontrolpoint(item);
    });
    return res;
  });
  self.bounds = function(downmat){
    if (downmat == undefined) downmat = identitytra();
    var fuk = [999999,999999,-999999,-999999];
    function rowmins(p0,p1,p2,p3,isy) {
      function check(x) {
        if (fuk[0+isy]>x) fuk[0+isy] = x;
        if (fuk[2+isy]<x) fuk[2+isy] = x;
      }
      var a=3*p3- 9*p2+9*p1-3*p0;
      var b=6*p2-12*p1+6*p0;
      var c=3*p1- 3*p0;
      function checkt(t) {
        if (t > 0 && t < 1) {
          var s=1-t;
          check(p0*s*s*s+3*p1*t*s*s+3*p2*t*t*s+p3*t*t*t);
        }
      }
      check(p0)
      check(p3)
      var disc = b * b - 4 * a * c;
      if (disc >= 0) {
        checkt((-b + Math.sqrt(disc)) / (2 * a));
        checkt((-b - Math.sqrt(disc)) / (2 * a));
      }
    }
    var ctrlp = self.controlpoints().map(function(item){return applytransform(item,downmat);})
    for (var i=0;i+3<self.controlpoints().length;i+=3) {
      rowmins(ctrlp[i].x,ctrlp[i+1].x,ctrlp[i+2].x,ctrlp[i+3].x,0)
      rowmins(ctrlp[i].y,ctrlp[i+1].y,ctrlp[i+2].y,ctrlp[i+3].y,1)
    }
    var end = ctrlp.length;
    if (self.closed()) {
      rowmins(ctrlp[end-3].x,ctrlp[end-2].x,ctrlp[end-1].x,ctrlp[0].x,0)
      rowmins(ctrlp[end-3].y,ctrlp[end-2].y,ctrlp[end-1].y,ctrlp[0].y,1)
    }
    return fuk;
  };
  self.doubleclick = function(x,y){
    var pos = {'x':x,'y':y}
    var heur = 999999;
    var dire = null;
    var clindex = null;
    var end = self.controlpoints().length;
    function dotacross(index,direction) {
      var v = self.controlpoints()[index];
      var w = self.controlpoints()[direction?(index+1)%end:(index-1)];
      var t = ((pos.x - v.x) * (w.x - v.x) + (pos.y - v.y) * (w.y - v.y)) / dist2(v, w);
      if (t<0 || t>1) {return}
      var jhg = {'x':v.x+t*(w.x-v.x),'y':v.y+t*(w.y-v.y)}
      var h = dist2(jhg,pos);
      if (h<heur) {
        heur = h;
        clindex = index;
        dire = direction;
      }
    }
    for (var i=0;i+2<end;i+=3) {
      dotacross(i+1,false)
      dotacross(i+2,true)
    }
    if (clindex == null) {return;}
    if (heur > 81) {return;}
    var w = self.controlpoints()[dire?(clindex+1)%end:(clindex-1)];
    var w1 = {'x':(w.x*2+pos.x)/3.0,'y':(w.y*2+pos.y)/3.0};
    var w2 = {'x':(w.x+pos.x*2)/3.0,'y':(w.y+pos.y*2)/3.0};
    if (dire) {
      self.controlpoints.splice(clindex+1,0,pos,w2,w1);
    } else {
      self.controlpoints.splice(clindex,0,w1,w2,pos);
    }
  }
}





function AppViewModel() {
  var self = this;
  self.activelayer = ko.observable(null);
  self.dragginglayer = null;
  self.draggingvertex = null;


  self.sdrag = function(imp) {
    self.dragginglayer = imp;
    $(document).on("mouseup", function(){
      self.dragginglayer = null;
      $(document).off("mouseup");
    });
  }

  self.getglobaltransform = function(elem) {
    for (let item of self.layers()) {
      var k = item.getglobaltransform(elem,identitytra());
      if (k != null) {return k}
    }
  }


  self.layers = ko.observableArray([]);


  self.deletelayer = function(lay) {
    self.activelayer(null);
    self.layers.remove(lay);
    self.layers().forEach(function(item) {
      item.deletelayer(lay);
    });
  };
  self.adopt = function(old) {
    if (old == self.dragginglayer) {return}
    if (self.dragginglayer != null) {
      var nindex = self.layers().indexOf(old);
      self.deletelayer(self.dragginglayer);
      self.layers.splice(nindex,0,self.dragginglayer);
      self.dragginglayer = null;
    }
  };
  self.svg = function() {
    var res = "";
    self.layers().forEach(function(item){
      res = item.svg() + res;
    });
    if (self.activelayer() != null) {
      res = res + self.activelayer().editorsvg();
    }
    return res;
  };

  draginside($("#target"),function(x,y){
    var pos = {'x':x,'y':y}
    if (self.activelayer()==null) {return}
    var closest = null;
    var heur = 9999999;
    self.activelayer().controlpoints().forEach(function(item,index){
      var h = dist2(item,pos);
      if (h<heur) {
        heur = h;
        closest = index;
      }
    });
    if (heur<64) {self.draggingvertex = closest;}
  },function(x,y){
    var pos = {'x':x,'y':y}
    if (self.activelayer()==null) {return}
    if (self.draggingvertex==null) {return}
    self.activelayer().touchcontrol(self.draggingvertex,pos);
  },function(x,y){
    self.draggingvertex = null;
  });


  dblclickinside($("#target"),function(x,y){self.activelayer().doubleclick(x,y);});



  draginside($("#timeline"),function(x,y){
  },function(x,y){
  },function(x,y){
  });

  // scrollinside($("#target"));
}
ko.applyBindings(justice);










