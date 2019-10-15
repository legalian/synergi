ko.subscribable.fn.subscribeChanged = function (callback) {
    var oldValue;
    this.subscribe(function (_oldValue) {
        var value = ko.utils.unwrapObservable(this);
        if (value != null && value.constructor == Array){
            oldValue = _oldValue.slice();
        } else {
            oldValue = _oldValue;
        }
    }, this, 'beforeChange');

    this.subscribe(function (newValue) {
        callback(newValue, oldValue);
    });
};





function scrollinside(elem,sc) {
  elem.bind('mousewheel DOMMouseScroll', function(event){
    event.stopPropagation();
    sc(event.originalEvent.wheelDeltaX,event.originalEvent.wheelDeltaY);
  });
};
function draginside(elem,md,mm,mu) {
  elem.on("mousedown",function(e){
    md(e.pageX - elem.offset().left,e.pageY - elem.offset().top);
    elem.on("mousemove",function(e){
      mm(e.pageX - elem.offset().left,e.pageY - elem.offset().top);
    });
    $(document).on("mouseup",function(e){
      elem.off("mousemove");
      $(document).off("mouseup");
      mu(e.pageX - elem.offset().left,e.pageY - elem.offset().top);
    });
  });
};
function dblclickinside(elem,db) {
  elem.on("dblclick",function(e){
    db(e.pageX - elem.offset().left,e.pageY - elem.offset().top);
  });
};



function cuberoot(x) {
    var y = Math.pow(Math.abs(x), 1/3);
    return x < 0 ? -y : y;
}


function dot(a,b) {return a.x*b.x + a.y*b.y}

function dist2(v, w) { return (v.x-w.x)*(v.x-w.x) + (v.y-w.y)*(v.y-w.y) }

function perpvec(vec) {
  return {'x':vec.y,'y':-vec.x}
}
function mulmatrix(vec,mat) {
  return {'x':vec.x*mat[0].x+vec.y*mat[1].x,'y':vec.x*mat[0].y+vec.y*mat[1].y}
}
function invmatrix(mat) {
  var det = 1/(mat[0].x*mat[1].y-mat[0].y*mat[1].x);
  return [{'x':mat[1].y*det,'y':-mat[0].y*det},{'x':-mat[1].x*det,'y':mat[0].x*det}]
}
function combinemat(mat1,mat2) {
  return [mulmatrix(mat2[0],mat1),mulmatrix(mat2[1],mat1)]
}
function subtractvec(vec1,vec2) {
  return {'x':vec1.x-vec2.x,'y':vec1.y-vec2.y}
}
function stringvec(vec) {
  return vec.x+","+vec.y+" ";
}
function addvec(vec1,vec2) {
  return {'x':vec1.x+vec2.x,'y':vec1.y+vec2.y}
}
function scalevec(scal,vec) {
  return {'x':vec.x*scal,'y':vec.y*scal}
}
function applytransform(vec,tra) {
  return addvec(mulmatrix(vec,tra),tra[2])
}
function invtransform(tra) {
  var mat = invmatrix(tra)
  return [mat[0],mat[1],mulmatrix(scalevec(-1,tra[2]),mat)]
}
function combinetransform(tra1,tra2) {
  var mat = combinemat(tra1,tra2)
  return [mat[0],mat[1],addvec(mulmatrix(tra1[2],tra2),tra2[2])]
}
function identitytra() {
  return [{'x':1,'y':0},{'x':0,'y':1},{'x':0,'y':0}];
}

function normalize(vec1) {
  return scalevec(1.0/Math.sqrt(dot(vec1,vec1)),vec1);
}

function dist2point(P,P0) {
    return dist2(P,P0);
}
function dist2line(pos,v,w) {
    var t = ((pos.x - v.x) * (w.x - v.x) + (pos.y - v.y) * (w.y - v.y)) / dist2(v, w);
    if (t>1) {t=1;}
    if (t<0) {t=0;}
    return dist2({'x':v.x+t*(w.x-v.x),'y':v.y+t*(w.y-v.y)},pos);
}
function dist2quadratic(pos,A,B,C) {
    var a = subtractvec(B,A);
    var b = addvec(subtractvec(A,scalevec(2,B)),C);
    var c = scalevec(2,a);
    var d = subtractvec(A,pos);
    var kk = 1.0 / dot(b,b);
    var kx = kk * dot(a,b);
    var ky = kk * (2.0*dot(a,a)+dot(d,b)) / 3.0;
    var kz = kk * dot(d,a);
    var p = ky - kx*kx;
    var p3 = p*p*p;
    var q = kx*(2.0*kx*kx - 3.0*ky) + kz;
    var h = q*q + 4.0*p3;
    if( h >= 0.0) { 
        h = Math.sqrt(h);
        t = Math.cbrt(( h-q)/2.0) + Math.cbrt((-h-q)/2.0) - kx;
        if (t>1) {t=1;}
        if (t<0) {t=0;}
        return dist2(pos,addvec(A,scalevec(t,addvec(c,scalevec(t,b)))));
    } else {
        var z = Math.sqrt(-p);
        var v = Math.acos( q/(p*z*2.0) ) / 3.0;
        var tx = (2*Math.cos(v))*z-kx;
        var ty = (-Math.cos(v)-Math.sin(v)*1.732050808)*z-kx;
        if (tx<0) {tx=0;}
        if (ty<0) {ty=0;}
        if (tx>1) {tx=1;}
        if (ty>1) {ty=1;}
        return Math.min(dist2(pos,addvec(A,scalevec(tx,addvec(c,scalevec(tx,b))))),dist2(pos,addvec(A,scalevec(ty,addvec(c,scalevec(ty,b))))))
    }
}






