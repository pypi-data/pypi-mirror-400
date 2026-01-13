import{a9 as y,X as m,aM as M,r as z,aR as X,aN as j,b8 as w,j as u,aO as H,a_ as C}from"./index-4cf586ed.js";import{k as W}from"./hooks-e7539055.js";import{c as R}from"./colors-5bf0897d.js";function _(n){const{sz:t=null,sy:s=null,sampx:i=null,sampy:o=null,sampu:a=null,sampv:r=null}=n,e=new URL(`${y()}/tomo/move`);s&&e.searchParams.append("sy",s.toString()),t&&e.searchParams.append("sz",t.toString()),i&&e.searchParams.append("sampx",i.toString()),o&&e.searchParams.append("sampy",o.toString()),a&&e.searchParams.append("sampu",a.toString()),r&&e.searchParams.append("sampv",r.toString()),e.searchParams.append("relative","false");const c=new XMLHttpRequest;c.open("GET",e.href,!0),m.token&&c.setRequestHeader("Authorization",`Bearer ${m.token}`),c.send()}function E(n){const{datacollectionid:t,axisposition:s,deltabeta:i,filename:o}=n;if(t===void 0)return;const a=new URL(`${y()}/tomo/slice_reconstruction`);t!==void 0&&a.searchParams.append("datacollectionid",t.toString()),s!==void 0&&a.searchParams.append("axisposition",s.toString()),i!==void 0&&a.searchParams.append("deltabeta",i.toString()),o!==void 0&&a.searchParams.append("filename",o);const r=new XMLHttpRequest;r.open("GET",a.href,!0),m.token&&r.setRequestHeader("Authorization",`Bearer ${m.token}`),r.send()}class k extends H{constructor(){super({uniforms:{color:{value:new C},gapColor:{value:new C},dashSize:{value:0},gapSize:{value:0},scaleX:{value:0},scaleY:{value:0},size:{value:0},lineWidth:{value:0}},vertexShader:`
uniform float scaleX;
uniform float scaleY;
uniform float size;
out vec2 pixelCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    vec2 pixelScale = vec2(scaleX, scaleY);
    pixelCoord = vec2(position.x + size * 0.5, position.y) / pixelScale;
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
        alpha = smoothstep(lineWidth * 0.5 + 0.01, lineWidth * 0.5 - 0.1, abs(pixelCoord.y));
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
      `})}}M({HDashMaterial:k});function Y(n){const{y:t,x1:s,x2:i,lineWidth:o=1,color:a="black",gapColor:r,dashSize:e=0,gapSize:c=e,opacity:f=1,zIndex:b=0}=n,p=z.useRef(null),h=i-s,P=(s+i)*.5,v=X.useRef(null),x=W();return z.useEffect(()=>{const d=R(a,f),g=R(r??"transparent",f);if(p.current){const l=p.current.uniforms;l.color.value=d,l.gapColor.value=g,l.dashSize.value=e,l.gapSize.value=c,l.size.value=h,l.lineWidth.value=o,j()}},[a,r,e,c,f,h,o]),w(({camera:d})=>{if(v.current===null||p.current===null)return;const g=d.scale.x/x.sx,l=d.scale.y/x.sy;v.current.scale.y=l;const S=p.current.uniforms;S.scaleX.value=g,S.scaleY.value=1}),u.jsx("group",{ref:v,position:[P,t,b],children:u.jsxs("mesh",{children:[u.jsx("ambientLight",{}),u.jsx("planeGeometry",{attach:"geometry",args:[Math.abs(h),o+1,1,1]}),u.jsx("hDashMaterial",{attach:"material",transparent:!0,ref:p})]})})}export{Y as H,E as a,_ as r};
