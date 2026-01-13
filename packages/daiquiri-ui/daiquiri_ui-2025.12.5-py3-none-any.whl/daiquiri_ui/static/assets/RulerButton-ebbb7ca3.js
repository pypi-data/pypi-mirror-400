import{P as S,r as b,j as e,ay as I,aj as Z,B as ee,aM as H,a7 as C,bQ as ae,aN as E,b8 as O,aO as $,a_ as _,bR as G,ax as te,aP as V}from"./index-4cf586ed.js";import{O as X,u as T,b as Q,Q as U}from"./index-19c84627.js";import{t as q}from"./QtyHelper-8429914f.js";import{k as J}from"./hooks-e7539055.js";import{c as Y}from"./colors-5bf0897d.js";import{A as N}from"./Anchor-f3716b7b.js";import{b as oe}from"./UseMouseModeInteraction-9b6c111c.js";import{a as ne}from"./types-0be7083b.js";const se={id:S.string,toggleLabel:S.string,href:S.string,target:S.string,onClick:S.func,title:S.node.isRequired,type:S.string,disabled:S.bool,align:ne,menuRole:S.string,renderMenuOnMount:S.bool,rootCloseEvent:S.string,flip:S.bool,bsPrefix:S.string,variant:S.string,size:S.string},B=b.forwardRef(({id:c,bsPrefix:a,size:t,variant:n,title:l,type:u="button",toggleLabel:d="Toggle dropdown",children:o,onClick:s,href:g,target:r,menuRole:v,renderMenuOnMount:m,rootCloseEvent:p,flip:x,...h},f)=>e.jsxs(I,{ref:f,...h,as:Z,children:[e.jsx(ee,{size:t,variant:n,disabled:h.disabled,bsPrefix:a,href:g,target:r,onClick:s,type:u,children:l}),e.jsx(I.Toggle,{split:!0,id:c,size:t,variant:n,disabled:h.disabled,childBsPrefix:a,children:e.jsx("span",{className:"visually-hidden",children:d})}),e.jsx(I.Menu,{role:v,renderOnMount:m,rootCloseEvent:p,flip:x,children:o})]}));B.propTypes=se;B.displayName="SplitButton";const re=B;class le extends ${constructor(){super({uniforms:{color:{value:new _},gapColor:{value:new _},dashSize:{value:0},gapSize:{value:0},scaleX:{value:0},scaleY:{value:0},origin:{value:new C},direction:{value:new C},lineWidth:{value:0}},vertexShader:`
uniform float scaleX;  // signed scale
uniform float scaleY;  // signed scale
uniform vec2 origin;
uniform vec2 direction;
out vec2 pixelCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    vec2 p = vec2(position.x, position.y) - origin;
    float l = dot(p, direction);
    float d = dot(p, vec2(-direction.y, direction.x));
    float scale = (abs(scaleX) + abs(scaleY)) * 0.5;
    pixelCoord = vec2(l, d / scale);
}
      `,fragmentShader:`
uniform vec4 color;
uniform vec4 gapColor;
uniform float gapSize;
uniform float dashSize;
uniform float lineWidth;

in vec2 pixelCoord;

void main() {
    float alpha;
    if (lineWidth >= 1.0) {
        alpha = smoothstep(0.5, 0.0, abs(pixelCoord.y) - lineWidth * 0.5);
    } else {
        // simulate line thiner than 1px with alpha
        alpha = lineWidth;
    }

    if (dashSize == 0.0) {
        gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
        return;
    }

    float dist = abs(pixelCoord.x);
    dist = mod(dist, (dashSize + gapSize));
    if (dist <= dashSize) {
        gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
    } else {
        gl_FragColor = vec4(gapColor.r, gapColor.g, gapColor.b, alpha * gapColor.a);
    }
}
      `})}}H({LineWithDataDashMaterial:le});function W(c){const{p1:a,p2:t,lineWidth:n=1,color:l="black",gapColor:u,dashSize:d=0,gapSize:o=d,opacity:s=1,zIndex:g=0}=c,r=b.useRef(null),v=J(),[m,p,x]=b.useMemo(()=>{const h=new C(t[0]-a[0],t[1]-a[1]).normalize(),i=new C(-h.y,h.x).multiplyScalar(n+1),y=new ae;return y.moveTo(a[0]-i.x,a[1]-i.y),y.lineTo(a[0]+i.x,a[1]+i.y),y.lineTo(t[0]+i.x,t[1]+i.y),y.lineTo(t[0]-i.x,t[1]-i.y),y.closePath(),[y,new C(a[0],a[1]),h]},[a,t,n]);return b.useEffect(()=>{const h=Y(l,s),f=Y(u??"transparent",s);if(r.current){const i=r.current.uniforms;i.color.value=h,i.gapColor.value=f,i.dashSize.value=d,i.gapSize.value=o,i.origin.value=p,i.direction.value=x,i.lineWidth.value=n,E()}},[l,u,d,o,s,p,x,n]),O(({camera:h})=>{if(r.current===null)return;const f=h.scale.x/v.sx,i=h.scale.y/v.sy,y=r.current.uniforms;y.scaleX.value=f,y.scaleY.value=i,E()}),e.jsx("group",{"position-z":g,children:e.jsxs("mesh",{children:[e.jsx("ambientLight",{}),e.jsx("shapeGeometry",{attach:"geometry",args:[m]}),e.jsx("lineWithDataDashMaterial",{attach:"material",transparent:!0,ref:r})]})})}class ie extends ${constructor(){super({uniforms:{color:{value:new _},gapColor:{value:new _},radius:{value:0},startAngle:{value:0},angleRange:{value:0},dashSize:{value:0},gapSize:{value:0},scaleX:{value:0},scaleY:{value:0},lineWidth:{value:0}},vertexShader:`
uniform float scaleX; // signed scale
uniform float scaleY; // signed scale
out vec2 pixelCoord;
// out vec2 dataCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    vec2 pixelScale = abs(vec2(scaleX, scaleY));
    // dataCoord = vec2(position.x, position.y);
    pixelCoord = vec2(position.x, position.y) / pixelScale;
}
      `,fragmentShader:`
uniform vec4 color;
uniform vec4 gapColor;
uniform float gapSize;
uniform float dashSize;
uniform float lineWidth;
uniform float scaleX; // signed scale
uniform float scaleY; // signed scale
uniform float radius;
uniform float startAngle;
uniform float angleRange;
in vec2 pixelCoord;

const float M_PI = 3.1415926535897932384626433832795;
const float AA_DASH = 0.5;

/**
 * Antialiasing following the line of dash and gap.
 *
 * The distances have to be in pixel.
 */
vec4 aa_dash_gap(float dist, float alpha, float dashSize, float gapSize) {
  dist = mod(dist, (gapSize + dashSize));
  float sd1 = (dist < dashSize) ? dist : dist - (dashSize + gapSize);
  float sd2 = -(dist - dashSize);
  if (abs(sd1) <= AA_DASH || abs(sd2) <= AA_DASH) {
    if (abs(sd1) < abs(sd2)) {
      float c = (sd1 + AA_DASH) * (0.5 / AA_DASH);
      return (
        vec4(color.r, color.g, color.b, alpha * color.a) * c
        + vec4(gapColor.r, gapColor.g, gapColor.b, alpha * gapColor.a) * (1.0 - c)
      );
    } else {
      float c = (sd2 + AA_DASH) * (0.5 / AA_DASH);
      return (
        vec4(color.r, color.g, color.b, alpha * color.a) * c
        + vec4(gapColor.r, gapColor.g, gapColor.b, alpha * gapColor.a) * (1.0 - c)
      );
    }
  }
  if (dist <= dashSize) {
    return vec4(color.r, color.g, color.b, alpha * color.a);
  }
  return vec4(gapColor.r, gapColor.g, gapColor.b, alpha * gapColor.a);
}

void main() {
    float r = length(pixelCoord);
    float s = (abs(scaleX) + abs(scaleY)) * 0.5;
    float ss = 1.0 / s;
    float d = abs(r - radius * ss) - lineWidth * 0.5;
    if (d > 1.5) {
      discard;
    }

    float sAngleRange = sign(angleRange);
    float nAngleRange = abs(angleRange);
    float rawA = atan(pixelCoord.x, pixelCoord.y);
    float aa = mod(sAngleRange * (rawA - startAngle) + 8.0 * M_PI, 2.0 * M_PI);

    if (nAngleRange < 2.0 * M_PI && aa < 0.0 || aa > nAngleRange) {
      discard;
    }

    float alpha;
    if (lineWidth >= 1.0) {
      alpha = smoothstep(0.25, 0.0, d);
    } else {
      // simulate line thiner than 1px with alpha
      alpha = lineWidth;
    }

    if (dashSize == 0.0) {
      gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
      return;
    }

    float dist = aa * radius;
    gl_FragColor = aa_dash_gap(dist * ss, alpha, dashSize * ss, gapSize * ss);
}
      `})}}H({ArcDashMaterial:ie});function ce(c){const{center:a,radius:t,startAngle:n,angleRange:l,lineWidth:u=1,color:d="black",gapColor:o,dashSize:s=0,gapSize:g=s,opacity:r=1,zIndex:v=0}=c,m=b.useRef(null),p=J();return b.useEffect(()=>{const x=Y(d,r),h=Y(o??"transparent",r);if(m.current){const f=m.current.uniforms;f.color.value=x,f.radius.value=t,f.startAngle.value=((n+180)%360-180)*Math.PI/180,f.angleRange.value=l*Math.PI/180,f.gapColor.value=h,f.dashSize.value=s,f.gapSize.value=g,f.lineWidth.value=u,E()}},[d,t,n,l,o,s,g,r,u]),O(({camera:x})=>{if(m.current===null)return;const h=x.scale.x/p.sx,f=x.scale.y/p.sy,i=m.current.uniforms;i.scaleX.value=h,i.scaleY.value=f}),e.jsx("group",{position:[a[0],a[1],v],children:e.jsxs("mesh",{children:[e.jsx("ambientLight",{}),e.jsx("planeGeometry",{attach:"geometry",args:[(t+u)*2,(t+u)*2,1,1]}),e.jsx("arcDashMaterial",{attach:"material",transparent:!0,ref:m})]})})}function de(c){const{geometry:a,onGeometryChanged:t,zIndex:n,lineWidth:l=1,color:u="blue",opacity:d=1,readOnly:o=!1,visible:s=!0}=c,{x:g,y:r,angle:v,angleRange:m,radius:p}=a,x=v*Math.PI/180,h=(v-m*.5)*Math.PI/180,f=(v+m*.5)*Math.PI/180,i={x:g+Math.sin(h)*p,y:r+Math.cos(h)*p},y={x:g+Math.sin(f)*p,y:r+Math.cos(f)*p},D={x:g+Math.sin(x)*p*.5,y:r+Math.cos(x)*p*.5},P=`${m.toFixed(2)} deg`,R=10*p/(Math.PI*18),j=b.useCallback((M,w)=>{const A=new C(M.x-a.x,M.y-a.y),k=Math.atan2(A.x,A.y)*180/Math.PI,F=G(a.angle-a.angleRange*.5,k);t==null||t({...a,radius:A.length(),angle:a.angle+F*.5,angleRange:a.angleRange-F},w)},[a,t]),z=b.useCallback((M,w)=>{const A=new C(M.x-a.x,M.y-a.y),k=Math.atan2(A.x,A.y)*180/Math.PI,F=G(a.angle+a.angleRange*.5,k);t==null||t({...a,radius:A.length(),angle:a.angle+F*.5,angleRange:a.angleRange+F},w)},[a,t]);return s?e.jsxs(e.Fragment,{children:[e.jsx(ce,{center:[g,r],radius:p,startAngle:v-m*.5,angleRange:m,lineWidth:l,color:u,opacity:d,gapColor:"#F0F0F0",dashSize:R,gapSize:R,zIndex:n}),e.jsx(W,{p1:[g,r],p2:[i.x,i.y],lineWidth:l,color:u,opacity:d,zIndex:n}),e.jsx(W,{p1:[g,r],p2:[y.x,y.y],lineWidth:l,color:u,opacity:d,zIndex:n}),e.jsx(N,{geometry:{x:g,y:r},onGeometryChanged:(M,w)=>{t==null||t({...c.geometry,x:M.x,y:M.y},w)},color:u,readOnly:o,opacity:d,zIndex:n}),e.jsx(N,{geometry:i,onGeometryChanged:j,color:u,readOnly:o,opacity:d,zIndex:n}),e.jsx(N,{geometry:y,onGeometryChanged:z,color:u,readOnly:o,opacity:d,zIndex:n}),e.jsx(X,{x:D.x,y:D.y,style:{zIndex:100},center:!0,children:e.jsx("div",{className:"text-light p-1 rounded",style:{backgroundColor:"#000000A0"},children:P})})]}):e.jsx(e.Fragment,{})}function K(c){const t=10**Math.ceil(Math.log10(c)),n=c/t;return n>=1?Number(t):n>=.5?.5*t:n>=.25?.25*t:n>=.1?.1*t:c}function ue(c){const{data:a,plotUnit:t}=c,[n,l]=a,u=Q(),{width:d}=u.canvasSize,o=U(p=>{const x=u.getVisibleDomains(p),h=x.xVisibleDomain[1]-x.xVisibleDomain[0];return Math.abs(h)},[d]),s=b.useMemo(()=>K(o/15),[o]),g=n.distanceTo(l),r=n.clone().add(l).multiplyScalar(.5);function v(p,x){return x?x==="px"?`${p.toFixed(2)} px`:q(new V(p,x)).toPrec(.01).toString():p.toFixed(2)}const m=v(g,t);return e.jsxs(e.Fragment,{children:[e.jsx(W,{p1:[n.x,n.y],p2:[l.x,l.y],color:"red",gapColor:"#F0F0F0",dashSize:s,gapSize:s,lineWidth:2,zIndex:3,opacity:.75}),e.jsx(X,{x:r.x,y:r.y,style:{zIndex:100},center:!0,children:e.jsx("div",{className:"bg-dark text-light p-1 rounded",children:m})})]})}function ge(c){const{data:a,plotUnit:t}=c,[n,l]=a,u=Q(),{width:d}=u.canvasSize,o=U(j=>{const z=u.getVisibleDomains(j),M=z.xVisibleDomain[1]-z.xVisibleDomain[0];return Math.abs(M)},[d]),s=b.useMemo(()=>K(o/15),[o]),g=n,r=new te(l.x,n.y),v=r,m=l,p=Math.abs(g.x-r.x),x=Math.abs(v.y-m.y),h=g.clone().add(r).multiplyScalar(.5),f=v.clone().add(m).multiplyScalar(.5);function i(j,z){return z?z==="px"?`${j.toFixed(2)} px`:q(new V(j,z)).toPrec(.01).toString():j.toFixed(2)}const y=i(p,t),D=i(x,t),P=p>x*.05,R=x>p*.05;return e.jsxs(e.Fragment,{children:[P&&e.jsx(W,{p1:[g.x,g.y],p2:[r.x,r.y],color:"red",gapColor:"#F0F0F0",dashSize:s,gapSize:s,lineWidth:2,zIndex:3,opacity:.75}),R&&e.jsx(W,{p1:[v.x,v.y],p2:[m.x,m.y],color:"red",gapColor:"#F0F0F0",dashSize:s,gapSize:s,lineWidth:2,zIndex:3,opacity:.75}),P&&e.jsx(X,{x:h.x,y:h.y,style:{zIndex:100},center:!0,children:e.jsx("div",{className:"bg-dark text-light p-1 rounded",children:y})}),R&&e.jsx(X,{x:f.x,y:f.y,style:{zIndex:100},center:!0,children:e.jsx("div",{className:"bg-dark text-light p-1 rounded",children:D})})]})}function L(c,a){const t=new C(a.x-c.x,a.y-c.y),n=Math.atan2(t.x,t.y)*180/Math.PI;return{x:c.x,y:c.y,radius:t.length(),angle:n,angleRange:30}}function be(c){const{mouseMode:a,disabled:t=!1,plotUnit:n}=c,l=a==="measure-angle",[u,d]=b.useState({x:0,y:0,radius:0,angle:0,angleRange:0}),o=oe();return e.jsxs(e.Fragment,{children:[e.jsx(T,{id:"ruler3-selection-tool",disabled:a!=="measure-angle"||t,onSelectionChange:s=>{if(s===void 0)return;const g=L(s.data[0],s.data[1]);d(g)},onSelectionStart:()=>{o==null||o.actions.captureMouseInteraction()},onSelectionEnd:()=>{o==null||o.actions.releaseMouseInteraction()},onValidSelection:s=>{const g=L(s.data[0],s.data[1]);d(g)},children:s=>e.jsx(e.Fragment,{})}),l&&e.jsx(de,{geometry:u,onGeometryChanged:s=>{d(s)},color:"red",lineWidth:2,zIndex:2,opacity:.75}),e.jsx(T,{id:"ruler-selection-tool",disabled:a!=="measure-distance"||t,onSelectionStart:()=>{o==null||o.actions.captureMouseInteraction()},onSelectionEnd:()=>{o==null||o.actions.releaseMouseInteraction()},children:s=>e.jsx(ue,{...s,plotUnit:n})}),e.jsx(T,{id:"ruler2-selection-tool",disabled:a!=="measure-ortho"||t,onSelectionStart:()=>{o==null||o.actions.captureMouseInteraction()},onSelectionEnd:()=>{o==null||o.actions.releaseMouseInteraction()},children:s=>e.jsx(ge,{...s,plotUnit:n})})]})}function Me(c){const{mouseModeInteraction:a,disabled:t=!1,dropDirection:n}=c,{mouseMode:l,setOrResetMouseMode:u,setMouseMode:d}=a,[o,s]=b.useState("measure-distance"),r={"measure-distance":"fa-ruler","measure-ortho":"fa-ruler-combined","measure-angle":"fam-protractor"}[o]??"",v=l==="measure-distance"||l==="measure-ortho"||l==="measure-angle";return e.jsxs(re,{title:e.jsx("i",{className:`fa ${r} fa-lg"`}),variant:v?"primary":"secondary",align:{lg:"start"},className:n==="up"?"dropup":void 0,autoClose:!0,onClick:()=>{u(o)},disabled:t,children:[e.jsxs(I.Item,{active:l==="measure-distance",onClick:()=>{s("measure-distance"),d("measure-distance")},title:"Measure the distance between 2 points",children:[e.jsx("i",{className:"fa fa-ruler fa-lg"})," Measure distance"]}),e.jsxs(I.Item,{active:l==="measure-ortho",onClick:()=>{s("measure-ortho"),d("measure-ortho")},title:"Measure the orthogonal distance between 2 points",children:[e.jsx("i",{className:"fa fa-ruler-combined fa-lg"})," Measure orthogonal"]}),e.jsxs(I.Item,{active:l==="measure-angle",onClick:()=>{s("measure-angle"),d("measure-angle")},title:"Measure an angle",children:[e.jsx("i",{className:"fa fam-protractor fa-lg"})," Measure angle"]})]})}export{Me as R,re as S,be as a};
