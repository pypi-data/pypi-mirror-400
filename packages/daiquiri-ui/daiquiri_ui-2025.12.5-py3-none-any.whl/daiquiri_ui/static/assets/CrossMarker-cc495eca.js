import{aM as f,r as l,aN as h,j as e,aO as u,a_ as x}from"./index-4cf586ed.js";import{c as v}from"./colors-5bf0897d.js";import{S as g}from"./ScreenScale-fdd43179.js";class S extends u{constructor(){super({uniforms:{color:{value:new x},lineWidth:{value:0},sizeInScreen:{value:0}},vertexShader:`
out vec2 pixelCoord;

void main() {
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    pixelCoord = vec2(position.x, position.y);
}
      `,fragmentShader:`
uniform vec4 color;
uniform float lineWidth;
uniform float sizeInScreen;
in vec2 pixelCoord;

/**
 * Exact signed distance function to compute an
 * orthogonal rectangle.
 *
 * @param pos: Pixel position
 * @param center: Center of the rectangle
 * @param size: Size of the rectangle
 */
float sdf_rect(vec2 pos, vec2 center, vec2 size) {
    vec2 d = abs(pos - center) - size * 0.5;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

void main() {
  float d1 = sdf_rect(
    pixelCoord,
    vec2(0.0, 0.0),
    vec2(abs(sizeInScreen), lineWidth)
  );
  float d2 = sdf_rect(
    pixelCoord,
    vec2(0.0, 0.0),
    vec2(lineWidth, abs(sizeInScreen))
  );
  float d = min(d1, d2);

  if (d > 0.2) {
    discard;
  }

  float alpha;
  if (lineWidth >= 1.0) {
    alpha = smoothstep(0.2, 0.0, d);
  } else {
    // simulate line thiner than 1px with alpha
    alpha = lineWidth;
  }

  gl_FragColor = vec4(color.r, color.g, color.b, alpha * color.a);
}
      `})}}f({CrossMarkerMaterial:S});function M(i){const{x:c,y:d,color:n="black",opacity:s,sizeInScreen:r,lineWidth:o=1,zIndex:p=0}=i,a=l.useRef(null);return l.useEffect(()=>{const m=v(n,s);if(a.current){const t=a.current.uniforms;t.color.value=m,t.lineWidth.value=o,t.sizeInScreen.value=r,h()}},[n,s,o,r]),e.jsx("group",{position:[c,d,p],children:e.jsx(g,{children:e.jsxs("mesh",{children:[e.jsx("ambientLight",{}),e.jsx("planeGeometry",{attach:"geometry",args:[r+o,r+o,1,1]}),e.jsx("crossMarkerMaterial",{attach:"material",transparent:!0,ref:a})]})})})}export{M as C};
