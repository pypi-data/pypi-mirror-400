import{aM as j,r as x,aR as W,aN as M,b8 as R,j as o,aO as V,a_ as C}from"./index-4cf586ed.js";import{k as X}from"./hooks-e7539055.js";import{c as S}from"./colors-5bf0897d.js";class Y extends V{constructor(){super({uniforms:{color:{value:new C},gapColor:{value:new C},dashSize:{value:0},gapSize:{value:0},scaleX:{value:0},scaleY:{value:0},size:{value:0},lineWidth:{value:0}},vertexShader:`
uniform float scaleX;
uniform float scaleY;
uniform float size;
out vec2 pixelCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    vec2 pixelScale = vec2(scaleX, scaleY);
    pixelCoord = vec2(position.x, position.y + size * 0.5) / pixelScale;
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
        alpha = smoothstep(lineWidth * 0.5 + 0.01, lineWidth * 0.5 - 0.1, abs(pixelCoord.x));
    } else {
        // simulate line thiner than 1px with alpha
        alpha = lineWidth;
    }

    if (dashSize == 0.0) {
        gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
        return;
    }

    float dist = abs(pixelCoord.y);
    dist = mod(dist, (dashSize + gapSize));
    if (dist <= dashSize) {
        gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
    } else {
        gl_FragColor = vec4(gapColor.r, gapColor.g, gapColor.b, alpha * gapColor.a);
    }
}
      `})}}j({VDashMaterial:Y});function G(u){const{x:z,y1:p,y2:f,lineWidth:r=1,color:h="black",gapColor:d,dashSize:i=0,gapSize:m=i,opacity:s=1,zIndex:y=0}=u,a=x.useRef(null),t=f-p,b=(p+f)*.5,n=W.useRef(null),v=X();return x.useEffect(()=>{const l=S(h,s),c=S(d??"transparent",s);if(a.current){const e=a.current.uniforms;e.color.value=l,e.gapColor.value=c,e.dashSize.value=i,e.gapSize.value=m,e.size.value=t,e.lineWidth.value=r,M()}},[h,d,i,m,s,t,r]),R(({camera:l})=>{if(n.current===null||a.current===null)return;const c=l.scale.x/v.sx,e=l.scale.y/v.sy;n.current.scale.x=c;const g=a.current.uniforms;g.scaleX.value=1,g.scaleY.value=e}),o.jsx("group",{ref:n,position:[z,b,y],children:o.jsxs("mesh",{children:[o.jsx("ambientLight",{}),o.jsx("planeGeometry",{attach:"geometry",args:[r+1,Math.abs(t),1,1]}),o.jsx("vDashMaterial",{attach:"material",transparent:!0,ref:a})]})})}export{G as V};
