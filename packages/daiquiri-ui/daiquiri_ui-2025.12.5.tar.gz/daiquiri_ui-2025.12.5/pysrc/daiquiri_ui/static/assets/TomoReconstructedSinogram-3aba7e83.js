var fe=Object.defineProperty;var he=(t,a,s)=>a in t?fe(t,a,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[a]=s;var D=(t,a,s)=>(he(t,typeof a!="symbol"?a+"":a,s),s);import{r as v,j as e,w as xe,c as ge,m as pe,aa as q,aP as T,aU as O,aj as U,B as P,ay as V,g as L,R as S,C as f,O as ve,x as F,aM as oe,aO as ie,a_ as K,aN as ne,b8 as ye,a7 as I,aL as re,u as le,b9 as je,A as z,ba as Se,bb as be,aX as we,aY as Ce,bc as J,bd as Ae,a1 as ee,be as Me,q as _e}from"./index-4cf586ed.js";import{b as De,L as Fe,u as Ne,T as te,D as Re,S as Pe}from"./UseMouseModeInteraction-9b6c111c.js";import{S as ze}from"./StackedNameState-94be4a7b.js";import{a as G,r as Ie}from"./HSegment-26c3fd51.js";import{H as ke}from"./HistogramDomainSlider-9c6d3e2d.js";import{e as We,f as Te,g as Ee,h as qe,i as He,j as ae,k as Be}from"./hooks-e7539055.js";import{u as $e,L as Le,I as Oe,A as Ve}from"./AutoscaleOption-e2ee098d.js";import{u as Ge}from"./colormap-0981f7dc.js";import{u as Ye}from"./hooks-e8b12550.js";import{w as Xe}from"./index-19c84627.js";import{C as Ue}from"./Cross-80ee2b29.js";import{S as Ke}from"./SceneScale-47e8e288.js";import{p as A,f as Qe,c as Ze}from"./geometry-252a228f.js";import{c as Q}from"./colors-5bf0897d.js";import{L as W}from"./Label-7daca8b6.js";import{C as Je}from"./CrossMarker-cc495eca.js";import{S as et}from"./ScreenScale-fdd43179.js";import{P as tt}from"./SelectionPoint-7fbd4e1f.js";import"./Image-c1578ac2.js";import"./VSegment-5d77576e.js";import"./QtyHelper-8429914f.js";function at(t){return t?t.status===null?["PROCESSING","warning"]:t.status===0?["FAILED","danger"]:t.status===1?["DONE","success"]:["UNKNOWN","fatal"]:["NONE","secondary"]}function st(t){v.useEffect(()=>{if(t.datacollectionid!==void 0&&t.programs!==void 0){const o=setInterval(()=>{t.datacollectionid!==void 0&&t.programs!==void 0&&t.actions.fetch({datacollectionid:t.datacollectionid,programs:t.programs})},500);return()=>{clearInterval(o)}}},[t.datacollectionid,t.programs]);const[a,s]=at(t.autoprocprogram);return e.jsx(ze,{className:t.className,name:`${t.name}`,state:a,stateVariant:s,description:`${t.description}`,minWidth:5})}const ot=(t,a)=>{const{autoprocprograms:s}=a.providers.metadata,o=s.selector("order",t);return{autoprocprogram:o&&o[0]?o[0][0]:null}},it=(t,a)=>{const{autoprocprograms:s}=a.providers.metadata;return{actions:{fetch:o=>{s.setParams({...o,order:"desc"},!0)}}}},nt=xe({metadata:pe})(ge(ot,it)(st));class H extends Error{}class rt{constructor(a,s){D(this,"isAborted");D(this,"request");D(this,"supportsFloat16Array");D(this,"error");D(this,"updateCallback");this.isAborted=!1,this.request=void 0,this.updateCallback=a,this.supportsFloat16Array=s}async fetchGroup(a){const s=await q.get("/h5grove/meta/",{...this.request,path:a});if(this.isAborted)throw new H;const o=s.data;if(o.type!=="group")throw new Error(`The path '${a}' is not a group`);let i;const n={},r={},l=async()=>{i=await this.fetchAttributes(a,o.attributes)},h=o.children.map(async c=>{c.type==="group"?r[c.name]=await this.fetchGroup(`${a}/${c.name}`):c.dtype==="|O"?n[c.name]=await this.fetchObjDataset(`${a}/${c.name}`,c):n[c.name]=await this.fetchDataset(`${a}/${c.name}`,c)});await Promise.all([...h,l()]);for(const c of o.children)if(this.isAborted)throw new H;if(i===void 0)throw new Error(`Attributes from path '${a}' was not fetched`);return{attrs:i,datasets:n,groups:r,name:o.name}}async fetchObjDataset(a,s){const o=await this.fetchAttributes(a,s.attributes),i=await q.get("/h5grove/data/",{...this.request,path:a,format:"json"}).then(n=>n.data).catch(n=>{});return{...s,attrs:o,data:i}}async fetchDataset(a,s){let o,i;const n=async()=>{o=await this.fetchAttributes(a,s.attributes)},r=this.supportsFloat16Array&&s.dtype==="<f2",l=async()=>{const h=await q.get("/h5grove/data/",{...this.request,path:a,format:"bin",dtype:r?"origin":"safe"},!0,"arraybuffer").then(m=>m.data).catch(m=>{console.error(m)});function c(m){if(!m)return;const g=s.shape.length===0?[1]:s.shape;if(r){const p=We(m,"<u2");return new Te(p,g)}const d=Ee(s.dtype);return qe(m,g,d)}i=c(h)};if(await Promise.all([l(),n()]),o===void 0)throw new Error(`Attributes from path '${a}' was not fetched`);return{...s,attrs:o,data:i}}async fetchAttributes(a,s){const i=(await q.get("/h5grove/attr/",{...this.request,path:a,attr_keys:s.map(r=>r.name)})).data,n={};return s.forEach(r=>{n[r.name]={...r,data:i[r.name]}}),n}async fetch(a){const{request:s}=a;if(this.isAborted=!1,this.request=s,s.datacollectionid===void 0){this.updateCallback({loading:!1});return}try{this.updateCallback({loading:!0});const o=await this.fetchGroup(s.path);if(this.isAborted)throw new H;this.updateCallback({loading:!1,group:o,request:s})}catch(o){if(!(o instanceof H)){const i=o instanceof Error?o.message:String(o);this.updateCallback({loading:!1,error:i,request:s})}}}abort(){this.isAborted=!0}}function lt(t){const[a,s]=v.useState({loading:!1});return v.useEffect(()=>{const o=new rt(s,t.supportsFloat16Array??!1);return o.fetch({request:{datacollectionid:t.datacollectionid,autoprocprogramid:t.autoprocprogramid,autoprocprogramattachmentid:t.autoprocprogramattachmentid,path:t.path,type:t.type}}),()=>{o.abort()}},[t.datacollectionid,t.autoprocprogramid,t.autoprocprogramattachmentid,t.path,t.type]),a}function ct(t){if(t===void 0||t.dtype!=="|O")return null;const a=t.data;return typeof a=="string"?[a]:t}function $(t){if(t===void 0||t.dtype!=="|O")return null;const a=t.data;return typeof a!="string"?null:a}function N(t){var s;if(!t)return null;const a=(s=t.data)==null?void 0:s.get(0);return a===void 0?null:a}function R(t){var o;if(!t)return null;const a=(o=t.data)==null?void 0:o.get(0);if(a===void 0)return null;const s=$(t.attrs.units);return s===null?null:new T(a,s)}function dt(){const t=$e({name:"tomo/slicecolormap"}),[a,s]=O("tomo/slicereconstruction/delta-beta",200),[o,i]=O("tomo/sliceview/axes",!0),[n,r]=O("tomo/sliceview/crosshair",!1);return{deltaBeta:a,setDeltaBeta:s,...t,displayAxes:o,setDisplayAxes:i,crossHair:n,setCrossHair:r}}function ut(t){const{as:a=void 0,className:s}=t;function o(i,n){const l=t.lut===i?"primary":"secondary";return e.jsx(P,{disabled:t.disabled,variant:l,onClick:()=>{t.onSelectLut(i)},className:"text-nowrap",title:n,size:"sm",children:e.jsx(Le,{name:i})})}return e.jsxs(U,{as:a,className:s,children:[o("Greys","Gray"),o("Viridis","Viridis"),o("Cividis","Cividis"),o("Magma","Magma"),o("Inferno","Inferno"),o("Plasma","Plasma")]})}function mt(t,a){return t===a?"primary":"secondary"}function B(t){return e.jsx(P,{variant:mt(t.var,t.value),onClick:()=>{t.setter(t.value)},className:"text-nowrap",size:"sm",children:t.children})}function ft(t){const{as:a=void 0,variant:s="secondary",config:o}=t;return e.jsxs(V,{as:a,className:`${t.dropDirection==="up"?"dropup":""}`,children:[e.jsx(V.Toggle,{id:"dropdown-basic",variant:s,className:"d-flex align-items-center",children:e.jsx("i",{className:"fa fa-sliders fa-fw fa-lg"})}),e.jsx(V.Menu,{className:"dropdown-menu-center",children:e.jsx("div",{className:"ms-1 me-1",style:{minWidth:"300px"},children:e.jsxs(L,{children:[e.jsxs(S,{children:[e.jsx(f,{className:"my-auto",children:"Colormap"}),e.jsx(f,{xs:7,children:e.jsx(ut,{lut:o.colorMap,onSelectLut:o.setColorMap})})]}),e.jsxs(S,{className:"mt-1",children:[e.jsx(f,{className:"my-auto",children:"Display axes"}),e.jsx(f,{xs:7,children:e.jsxs(U,{children:[e.jsx(B,{var:o.displayAxes,value:!0,setter:o.setDisplayAxes,children:"Yes"}),e.jsx(B,{var:o.displayAxes,value:!1,setter:o.setDisplayAxes,children:"No"})]})})]}),e.jsxs(S,{className:"mt-1",children:[e.jsx(f,{className:"my-auto",children:"Crosshair"}),e.jsx(f,{xs:7,children:e.jsxs(U,{children:[e.jsx(B,{var:o.crossHair,value:!0,setter:o.setCrossHair,children:"Yes"}),e.jsx(B,{var:o.crossHair,value:!1,setter:o.setCrossHair,children:"No"})]})})]})]})})})]})}class k extends Error{}function ht(t){if(!t)return null;const a=ct(t.attrs.signal);if(!a)throw new k("No signal found in NXdata");if(a.length!==1)throw new k(`Expect one and only one signal, found ${a.length}`);function s(w){try{const j=w.groups.histo,M=j.datasets.counts,C=j.datasets.bin_edges,_=M.data,u=C.data;return ae(_),ae(u),{values:_,bins:u}}catch(j){console.error(j);return}}function o(w){try{const j=w.groups.stats;return j===void 0?void 0:{min:N(j.datasets.min),max:N(j.datasets.max),minPositive:N(j.datasets.min_positive),mean:N(j.datasets.mean),std:N(j.datasets.std)}}catch{return}}const i=t.datasets[a[0]];if(!i)throw new k(`Dataset from signal ${a[0]} does not exists`);if(i.shape.length!==2)throw new k(`Dataset from signal ${a[0]} must be 2 ndim (found ${i.shape.length})`);const n=i.data;He(n);const r=R(t.datasets.sample_x_axis),l=R(t.datasets.sample_y_axis),h=R(t.datasets.y_axis),c=R(t.datasets.sample_pixel_size),m=R(t.datasets.used_axis_position)||new T(0,"px"),g=R(t.datasets.estimated_axis_position)||new T(0,"px"),d=N(t.datasets.delta_beta),p=$(t.datasets.backend),x=$(t.datasets.cor_backend),y=$(t.datasets.source_filename);return{histogram:s(t),imageArray:n,sampxPosition:r,sampyPosition:l,syPosition:h,axisPosition:m,samplePixelSize:c,estimatedAxisPosition:g,deltaBeta:d,backend:p,corBackend:x,stats:o(t),sourceFilename:y}}function xt(t){const{event:a}=t,[s,o]=v.useState({});return v.useEffect(()=>{if(a&&a.type===t.type){const{datacollectionid:i,autoprocprogramid:n}=a;console.log("event",a),i!==void 0&&n!==void 0&&o(r=>({...r,[`${i}`]:n}))}},[t.event]),v.useMemo(()=>{if(t.datacollectionid===void 0)return;const i=s[`${t.datacollectionid}`];return i!==void 0&&s[`group${t.datacollectiongroupid}`]!==i&&o(n=>({...n,[`group${t.datacollectiongroupid}`]:i})),i??s[`group${t.datacollectiongroupid}`]},[s,t.datacollectionid])}function gt(t){var r,l,h,c,m;const{datacollectionid:a,actions:s}=t,o=((l=(r=t.reconstructionInfo)==null?void 0:r.estimatedAxisPosition)==null?void 0:l.scalar)??void 0,i=((c=(h=t.reconstructionInfo)==null?void 0:h.axisPosition)==null?void 0:c.scalar)??void 0,n=((m=t.reconstructionInfo)==null?void 0:m.sourceFilename)??void 0;return v.useEffect(()=>{o!==void 0&&a!==void 0&&(s==null||s.updateDataCollectionMeta(a,{sourceFilename:n}))},[n]),v.useEffect(()=>{o!==void 0&&a!==void 0&&(s==null||s.updateDataCollectionMeta(a,{estimatedCor:o}))},[o]),v.useEffect(()=>{o!==void 0&&a!==void 0&&(s==null||s.updateDataCollectionMeta(a,{actualCor:i,requestedCor:null}))},[i]),e.jsx(e.Fragment,{})}function pt(t){function a(){t.datacollectionid!==void 0&&t.actions.requestSliceReconstruction({datacollectionid:t.datacollectionid,filename:t.sourceFilename})}return e.jsx(P,{variant:"secondary",title:"Recompute the slice from the sinogram",disabled:t.datacollectionid===null,onClick:a,children:e.jsx("i",{className:"fa fa-rotate-right fa-solid"})})}function vt(t){const{fetchedResult:a,reconstructedInfo:s}=t;function o(i){var n,r,l,h;return s===null?e.jsxs(F,{id:"reconstructed-slice-info",...i,children:[e.jsx(F.Header,{as:"h3",children:"Displayed data info"}),e.jsx(F.Body,{children:"No data"})]}):e.jsxs(F,{id:"reconstructed-slice-info",...i,children:[e.jsx(F.Header,{as:"h3",children:"Displayed data info"}),e.jsx(F.Body,{children:e.jsxs(L,{style:{width:"17em"},children:[a.request&&e.jsxs(e.Fragment,{children:[e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"Collection ID"}),e.jsx(f,{children:(n=a==null?void 0:a.request)==null?void 0:n.datacollectionid})]}),e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"Program ID"}),e.jsx(f,{children:((r=a==null?void 0:a.request)==null?void 0:r.autoprocprogramid)??"last"})]})]}),e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"Backend"}),e.jsx(f,{children:s==null?void 0:s.backend})]}),e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"COR backend"}),e.jsx(f,{children:s==null?void 0:s.corBackend})]}),e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"Axis position"}),e.jsxs(f,{children:[(l=s.axisPosition)==null?void 0:l.scalar.toFixed(2)," px"]})]}),e.jsxs(S,{className:"g-0",children:[e.jsx(f,{children:"Delta/beta"}),e.jsx(f,{children:(h=s.deltaBeta)==null?void 0:h.toFixed(2)})]})]})})]})}return e.jsx(ve,{trigger:["hover","focus"],placement:"bottom",overlay:o,children:e.jsx(P,{variant:"secondary",disabled:s===null,children:e.jsx("i",{className:"fa-solid fa-info fa-fw fa-lg"})})},"arg")}function yt(t){function a(o,i){return Math.round(o)===o?o.toFixed(0):o.toFixed(i)}const s=4;return e.jsxs(L,{style:{width:"150px"},children:[e.jsxs(S,{children:[e.jsx(f,{xs:3,children:"u"}),e.jsx(f,{xs:8,children:t.py.toFixed(s)}),e.jsx(f,{xs:1,children:t.inMotorSpace?"mm":"px"})]}),e.jsxs(S,{children:[e.jsx(f,{xs:3,children:"v"}),e.jsx(f,{xs:8,children:t.px.toFixed(s)}),e.jsx(f,{xs:1,children:t.inMotorSpace?"mm":"px"})]}),t.pixel&&e.jsxs(S,{children:[e.jsx(f,{xs:3,children:"pixel"}),e.jsx(f,{xs:8,children:a(t.pixel,s)}),e.jsx(f,{xs:1})]})]})}class jt extends ie{constructor(){super({uniforms:{color:{value:new K},gapColor:{value:new K},radius:{value:0},dashSize:{value:0},gapSize:{value:0},scaleX:{value:0},scaleY:{value:0},lineWidth:{value:0}},vertexShader:`
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
in vec2 pixelCoord;

const float M_PI = 3.1415926535897932384626433832795;
const float AA_DASH = 0.5;

/**
 * Antialiasing following the line of dash and gap
 */
vec4 aa_dash_gap(float dist, float alpha) {
  dist = mod(dist, (dashSize + gapSize));
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
    float d = abs(r - radius / s) - lineWidth * 0.5;
    if (d > 1.5) {
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

    // try to fit a fixed integer number of dashes + gaps
    // could be computed in the vertex shader
    float full = 2.0 * M_PI * (radius / s) / (dashSize + gapSize);
    float coef = ceil(full) / full;

    float dist = 2.0 * atan(pixelCoord.y, pixelCoord.x) * (radius / s) * coef;
    gl_FragColor = aa_dash_gap(dist, alpha);
}
      `})}}oe({CircleDashMaterial:jt});function Y(t){const{center:a,radius:s,lineWidth:o=1,color:i="black",gapColor:n,dashSize:r=0,gapSize:l=r,opacity:h=1,zIndex:c=0}=t,m=v.useRef(null),g=Be();return v.useEffect(()=>{const d=Q(i,h),p=Q(n??"transparent",h);if(m.current){const x=m.current.uniforms;x.color.value=d,x.radius.value=s,x.gapColor.value=p,x.dashSize.value=r,x.gapSize.value=l,x.lineWidth.value=o,ne()}},[i,s,n,r,l,h,o]),ye(({camera:d})=>{if(m.current===null)return;const p=d.scale.x/g.sx,x=d.scale.y/g.sy,y=m.current.uniforms;y.scaleX.value=p,y.scaleY.value=x}),e.jsx("group",{position:[a[0],a[1],c],children:e.jsxs("mesh",{children:[e.jsx("ambientLight",{}),e.jsx("planeGeometry",{attach:"geometry",args:[(s+o)*2,(s+o)*2,1,1]}),e.jsx("circleDashMaterial",{attach:"material",transparent:!0,ref:m})]})})}function St(t){const{sampleStage:a}=t,s=a.sampu?A(a.sampu):null,o=a.sampv?A(a.sampv):null,{tomoDetector:i,detector:n}=a;if(i===null||n===null||s===null||o===null)return e.jsx(e.Fragment,{});const r=Qe(i,n);if(r===null)return e.jsx(e.Fragment,{});const l=new I(o,s),h=r[0]*.5,c=r[0];function m(){const d=a.sy?A(a.sy):null;return d===null||r===null?null:r[0]*.5+Math.abs(d)}const g=m();return e.jsxs(e.Fragment,{children:[e.jsx(Y,{center:[l.x,l.y],radius:h,color:"#000000",gapColor:"#FF0000",opacity:.5,dashSize:5,gapSize:5,lineWidth:1}),e.jsx(W,{datapos:[l.x-h*.95,l.y-h*.35],color:"#FF0000",text:"Full"}),e.jsx(Y,{center:[l.x,l.y],radius:c,color:"#000000",gapColor:"#FF0000",opacity:.5,dashSize:5,gapSize:5,lineWidth:1}),e.jsx(W,{datapos:[l.x-c*.95,l.y-c*.35],color:"#FF0000",text:"Half"}),g!==null&&e.jsxs(e.Fragment,{children:[e.jsx(Y,{center:[l.x,l.y],radius:g,color:"#000000",gapColor:"#FF0000",dashSize:5,gapSize:5,lineWidth:1}),e.jsx(W,{datapos:[l.x-g,l.y-g*.175],color:"#FF0000",text:"Actual region"})]})]})}function bt(t){const{sampleStage:a}=t,s=a.sampu?A(a.sampu):null,o=a.sampv?A(a.sampv):null;return(a.sy?A(a.sy):null)===null||s===null||o===null?e.jsx(e.Fragment,{}):e.jsxs(e.Fragment,{children:[e.jsx(Je,{x:o,y:s,color:"red",sizeInScreen:30,lineWidth:2.5}),e.jsx(W,{datapos:[o,s],color:"#FF0000",anchor:"top-right",text:"Actual axis position"})]})}class wt extends ie{constructor(){super({uniforms:{color:{value:new K},lineWidth:{value:0},sizeInScreen:{value:0},angle:{value:0}},vertexShader:`
out vec2 pixelCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    pixelCoord = vec2(position.x, position.y);
}
      `,fragmentShader:`
// Based on antialiased arrow fields
// Nicolas P. Rougier (http://www.loria.fr/~rougier)
// https://www.shadertoy.com/view/ldlSWj
// Released under BSD license.

uniform vec4 color;
uniform float lineWidth;
uniform float sizeInScreen;
uniform float angle;
in vec2 pixelCoord;

// Computes the signed distance from a line
float sdf_line(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    return dot(rel_p, vec2(dir.y, -dir.x));
}

// Computes the signed distance from a line segment
float sdf_segment(vec2 p, vec2 p1, vec2 p2) {
    vec2 center = (p1 + p2) * 0.5;
    float len = length(p2 - p1);
    vec2 dir = (p2 - p1) / len;
    vec2 rel_p = p - center;
    float dist1 = abs(dot(rel_p, vec2(dir.y, -dir.x)));
    float dist2 = abs(dot(rel_p, dir)) - 0.5*len;
    return max(dist1, dist2);
}

float sdf_arrow(vec2 texcoord,
  float body, float head, float height,
  float linewidth, float antialias
) {
  float d;
  float w = linewidth/2.0 + antialias;
  vec2 start = -vec2(body / 2.0, 0.0);
  vec2 end   = +vec2(body / 2.0, 0.0);

  // Arrow tip (beyond segment end)
  if( texcoord.x > body / 2.0) {
    // Head : 2 segments
    float d1 = sdf_line(texcoord, end, end - head*vec2(+1.0, -height));
    float d2 = sdf_line(texcoord, end - head*vec2(+1.0, +height), end);
    // Body : 1 segment
    float d3 = end.x - texcoord.x;
    d = max(max(d1, d2), d3);
  } else {
    // Head : 2 segments
    float d1 = sdf_segment(texcoord, end - head * vec2(+1.0, -height), end);
    float d2 = sdf_segment(texcoord, end - head * vec2(+1.0, +height), end);
    // Body : 1 segment
    float d3 = sdf_segment(texcoord, start, end - vec2(linewidth, 0.0));
    d = min(min(d1, d2), d3);
  }
  return d;
}

vec4 filled(float distance, float linewidth, float antialias, vec4 fill)
{
    vec4 frag_color;
    float t = linewidth / 2.0 - antialias;
    float signed_distance = distance;
    float border_distance = abs(signed_distance) - t;
    float alpha = border_distance / antialias;
    alpha = exp(-alpha * alpha);

    // Within linestroke
    if (border_distance < 0.0) {
        return fill;
    }
    // Within shape
    if (signed_distance < 0.0) {
      return fill;
    }
    // Outside shape
    if (border_distance > (linewidth / 2.0 + antialias)) {
        discard;
    }
    // Line stroke exterior border
    return vec4(fill.rgb, alpha);
}

void main() {
    const float M_PI = 3.1415926535897932384626433832795;

    float theta = angle * M_PI / 180.0;
    float cos_theta = cos(theta);
    float sin_theta = sin(theta);
    vec2 pixelCoord2 = vec2(
      cos_theta * pixelCoord.x - sin_theta * pixelCoord.y,
      sin_theta * pixelCoord.x + cos_theta * pixelCoord.y
    );

    const float antialias = 1.0;
    float body = sizeInScreen;
    float d = sdf_arrow(pixelCoord2, body, 0.30 * body, 0.8, lineWidth, antialias);
    gl_FragColor = filled(d, lineWidth, antialias, color);
}
    `})}}oe({ArrowMarkerMaterial:wt});function X(t){const{x:a,y:s,color:o="black",opacity:i,sizeInScreen:n,angle:r,lineWidth:l=1,zIndex:h=0}=t,c=v.useRef(null);return v.useEffect(()=>{const m=Q(o,i);if(c.current){const g=c.current.uniforms;g.color.value=m,g.lineWidth.value=l,g.sizeInScreen.value=n,g.angle.value=r,ne()}},[o,i,l,n,r]),e.jsx("group",{position:[a,s,h],children:e.jsx(et,{screenDirection:!1,children:e.jsxs("mesh",{children:[e.jsx("ambientLight",{}),e.jsx("planeGeometry",{attach:"geometry",args:[n+l,n+l,1,1]}),e.jsx("arrowMarkerMaterial",{attach:"material",transparent:!0,ref:c})]})})})}function Ct(t){const{sampleStage:a}=t,s=a.sampu?A(a.sampu):null,o=a.sampv?A(a.sampv):null,i=a.somega?-Ze(a.somega):null;if(i===null||s===null||o===null)return e.jsx(e.Fragment,{});const n=i/Math.PI*180,r=(t.viewRange[0][1]-t.viewRange[0][0])*.5+(t.viewRange[1][1]-t.viewRange[1][0])*.5,l=new I(0,1).rotateAround(new I(0,0),i),h=new I(-l.y,l.x).multiplyScalar(.3*r),m=new I(o,s).clone().add(l.clone().multiplyScalar(.375*r)),g=m.clone().add(h),d=m,p=m.clone().sub(h);return e.jsxs(e.Fragment,{children:[e.jsx(X,{x:g.x,y:g.y,sizeInScreen:80,angle:90-n,color:"red",lineWidth:3}),e.jsx(X,{x:d.x,y:d.y,sizeInScreen:80,angle:90-n,color:"red",lineWidth:3}),e.jsx(X,{x:p.x,y:p.y,sizeInScreen:80,angle:90-n,color:"red",lineWidth:3}),e.jsx(W,{datapos:[d.x,d.y],color:"#FF0000",text:"Beam",anchor:"bottom"})]})}const se=re("daiquiri.components.tomo.reconstructedslice.MoveMotorInteraction");function At(t){const a=De(),{mouseMode:s}=a??{},{disabled:o,requestMoveSampleAxisAtPosition:i}=t,n=v.useCallback(r=>{const l=r.dataPt.x,h=r.dataPt.y;i(h,l)},[i]);return o||s!=="move-sample-to-axis"?(se("MoveMotorInteraction disabled."),e.jsx(e.Fragment,{})):(se("MoveMotorInteraction enabled."),e.jsx(tt,{onClick:n}))}function Mt(t){var g;const{sampleStage:a,mouseMode:s}=t,o=(g=t.reconstructedInfo)==null?void 0:g.imageArray,i=v.useRef(null),n=le();if(!t.reconstructedInfo||o===void 0)return e.jsx(e.Fragment,{});const l=(a.somega!==null?je(a.somega):!0)?1:-1;function h(d){const p=(o==null?void 0:o.shape[1])??0,x=(o==null?void 0:o.shape[0])??0;if(d.samplePixelSize===null||d.sampxPosition===null||d.sampyPosition===null||d.imageArray===null)return{inMotorSpace:!1,xRange:[0,x],yRange:[0,p],center:[p/2,x/2,0],scale:[1,1,1],height:x,width:p};const y=d.samplePixelSize.to("mm").scalar,w=d.sampxPosition.to("mm").scalar,j=d.sampyPosition.to("mm").scalar,M=d.imageArray.shape[1]*.5,C=d.imageArray.shape[0]*.5;return{inMotorSpace:!0,xRange:[j-M*y,j+M*y],yRange:[w-C*y,w+C*y],center:[j,w,0],scale:[-y,-l*y,1],width:M*y*2,height:C*y*2}}const c=h(t.reconstructedInfo);function m(d,p){return d===null||!c.inMotorSpace?`${p} (px)`:`${d.alias??d.name} (mm)`}return e.jsx("div",{style:{flex:"1 1 auto",display:"flex",margin:0,minHeight:0},className:t.className,children:e.jsxs(Fe,{plotRef:t.plotRef,abscissaConfig:{visDomain:c.xRange,label:m(a.sampv,"lateral-axis"),flip:!0},ordinateConfig:{visDomain:c.yRange,label:m(a.sampu,"x-axis")},mouseMode:s,aspect:"equal",showAxes:t.config.displayAxes,children:[e.jsx(Oe,{ref:i,values:o,domain:t.imageDomain,colorMap:t.imageColorMap,invertColorMap:t.imageInvertColorMap,position:c.center,scale:c.scale,scaleType:t.imageScaleType,size:{width:o.shape[1],height:o.shape[0]}}),e.jsx(Xe,{guides:t.config.crossHair?"both":void 0,renderTooltip:(d,p)=>{var y;const x=(y=i.current)==null?void 0:y.pick(d,p);return e.jsx(yt,{px:d,py:p,pixel:x,inMotorSpace:c.inMotorSpace})}}),e.jsx(Ue,{centerX:c.center[0],centerY:c.center[1],width:c.width,height:c.height,color:"white",gapColor:"black",dashSize:5,gapSize:5,lineWidth:1}),c.inMotorSpace&&e.jsxs(e.Fragment,{children:[e.jsx(St,{sampleStage:a}),e.jsx(bt,{sampleStage:a}),e.jsx(Ct,{sampleStage:a,viewRange:[c.xRange,c.yRange]})]}),e.jsx(At,{disabled:!n,requestMoveSampleAxisAtPosition:t.requestMoveSampleAxisAtPosition}),e.jsx(Ke,{unit:c.inMotorSpace?"mm":"px"})]})})}function _t(t){const{fetchedResult:a}=t;return t.datacollectionid===void 0?e.jsx(z,{variant:"secondary",children:"Not yet datacollection"}):t.autoprocprogramid===void 0&&a.group===void 0?e.jsxs(z,{variant:"secondary",children:["Not yet reconstruction for datacollection ",t.datacollectionid]}):a.loading?e.jsx(z,{variant:"warning",children:"Waiting for data"}):a.error?e.jsxs(z,{variant:"danger",children:[e.jsx("p",{children:"Error during fetching:"}),e.jsx("p",{children:a.error})]}):t.parsingError?e.jsxs(z,{variant:"danger",children:[e.jsx("p",{children:"Data format unsupported:"}),e.jsx("p",{children:t.parsingError})]}):e.jsx(e.Fragment,{})}const Dt=re("daiquiri.components.tomo.TomoReconstructedSinogram");function Ft(t){var Z;const{options:a}=t,s=Se(a.datacollectionid),o=v.useRef(),i=(s==null?void 0:s.datacollectionid)??void 0,n=be(),{uri:r,tomoconfig:l,events:h,...c}=a,m=le(),g=v.useRef(null),d=Ne("zoom"),{mouseMode:p}=d,x=dt(),y=we(l??""),w=Ce(y),j=Ye(t.options.events);function M(){g.current&&g.current.actions.resetZoom()}const C=xt({type:"tomo-sinogram-reconstruction",datacollectionid:s.datacollectionid,datacollectiongroupid:s.datacollectiongroupid,event:j??void 0});v.useEffect(()=>()=>{o.current&&clearTimeout(o.current)},[]);const _=lt({datacollectionid:s.datacollectionid,autoprocprogramid:C,type:"processing",path:r,supportsFloat16Array:!0}),[u,ce]=v.useMemo(()=>{try{return[ht(_.group),void 0]}catch(b){if(b instanceof k)return[null,b.message];throw b}},[_]);function de(b,E){if(d.resetMouseMode(),u===null){Dt("Move cancelled: reconstructedInfo is null");return}const ue=T(b,"mm"),me=T(E,"mm");Ie({sampu:ue,sampv:me})}return Ge({statistics:u==null?void 0:u.stats,...x}),e.jsxs("div",{className:"plot2d-container w-100 h-100",style:{flex:"1 1 0%",display:"flex",flexDirection:"column"},children:[e.jsxs(te,{align:"center",children:[e.jsx(gt,{reconstructionInfo:u,datacollectionid:i,actions:n}),e.jsx(Re,{mouseModeInteraction:d}),e.jsx(P,{title:"Reset zoom (sample stage overview)",variant:"secondary",onClick:()=>{M()},children:e.jsx("i",{className:"fa fa-expand fa-fw fa-lg"})}),e.jsx(Pe,{}),e.jsx(P,{title:m?"Move the motors to set rotation axis on the sample":"You have to get the control on the session to move motors",disabled:!m,variant:p==="move-sample-to-axis"?"danger":"secondary",onClick:()=>{d.setOrResetMouseMode("move-sample-to-axis")},children:e.jsx("i",{className:"fa fam-arrow-h-over-rot fa-fw fa-lg"})}),e.jsx(nt,{name:"Worker",description:"Automatic slice reconstruction from sinogram",datacollectionid:s.datacollectionid,programs:"tomo-sinogram-reconstruction",providers:{metadata:{autoprocprograms:{namespace:"tomosinogramreconstruction"}}}}),e.jsx(pt,{datacollectionid:s.datacollectionid,sourceFilename:(u==null?void 0:u.sourceFilename)??void 0,actions:{requestSliceReconstruction:G}})]}),e.jsxs(te,{align:"center",children:[e.jsx(Ve,{disabled:(u==null?void 0:u.stats)===void 0,...x}),e.jsx(ke,{disabled:u===void 0,histogram:u==null?void 0:u.histogram,...x}),e.jsx(vt,{fetchedResult:_,reconstructedInfo:u}),e.jsx(ft,{config:x})]}),e.jsxs(L,{children:[e.jsxs(S,{className:"g-0 align-items-center",children:[e.jsx(f,{xs:"3",title:"Location of the rotation axis from the left side of the sinogram (in pixel)",children:"Axis position:"}),e.jsx(f,{xs:"9",children:e.jsx(J,{hardwareValue:((Z=u==null?void 0:u.axisPosition)==null?void 0:Z.scalar)??0,hardwareIsDisabled:u===null,onMoveRequested:b=>(s.datacollectionid!==void 0&&G({datacollectionid:s.datacollectionid,axisposition:b,deltabeta:x.deltaBeta,filename:(u==null?void 0:u.sourceFilename)??void 0}),null)})})]}),e.jsxs(S,{className:"g-0 align-items-center",children:[e.jsx(f,{xs:"3",title:"Delta/beta ratio for the Paganin filter",children:"Delta/beta:"}),e.jsx(f,{xs:"9",children:e.jsx(J,{hardwareValue:x.deltaBeta,hardwareIsDisabled:!1,onMoveRequested:b=>{var E;return x.setDeltaBeta(b),s.datacollectionid!==void 0&&G({datacollectionid:s.datacollectionid,axisposition:(E=u==null?void 0:u.axisPosition)==null?void 0:E.scalar,deltabeta:b,filename:(u==null?void 0:u.sourceFilename)??void 0}),null}})})]})]}),e.jsx(_t,{datacollectionid:s.datacollectionid,autoprocprogramid:C,fetchedResult:_,parsingError:ce}),e.jsx(Mt,{config:x,imageColorMap:x.colorMap,imageInvertColorMap:x.invertColorMap,imageDomain:x.scaleDomain,imageScaleType:x.scaleType,reconstructedInfo:u,className:"flex-grow-1",sampleStage:w,mouseMode:p,plotRef:g,requestMoveSampleAxisAtPosition:de})]})}function Nt(t){return e.jsx(Ft,{...t})}function Jt(t){const{yamlNode:a,datacollectionid:s,uri:o,tomoconfig:i,events:n,...r}=t;Ae(a,"events",n),ee(a,"tomoconfig",i),ee(a,"uri",o),Me(a,"datacollectionid",s),_e(a,r);const l={datacollectionid:s,uri:o,tomoconfig:i,events:n};return e.jsx(Nt,{options:l})}export{Jt as default};
