import * as T from 'three';
import { OrbitControls } from './OrbitControls.js';
const stage=document.querySelector('#stage'),canvas=stage.querySelector('canvas');
async function setup(){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:true});
 renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFShadowMap;
 const scene=new T.Scene(),camera=new T.OrthographicCamera(-110,110,100,-100,1,1000);
 camera.up.set(0,0,1);
 const controls=new OrbitControls(camera,canvas);controls.enablePan=false;controls.minZoom=.65;controls.maxZoom=4;controls.maxPolarAngle=Math.PI*.495;
 const data=await (await fetch('geometry.json')).json();
 for(const p of data){
  const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(p.vertices,3));g.setIndex(p.faces);
  const flat=g.toNonIndexed();flat.computeVertexNormals();
  const m=new T.Mesh(flat,new T.MeshStandardMaterial({color:p.color,roughness:.85}));m.castShadow=true;m.receiveShadow=true;scene.add(m);
 }
 const ground=new T.Mesh(new T.PlaneGeometry(1200,1200),new T.ShadowMaterial({opacity:.16}));ground.position.z=-.15;ground.receiveShadow=true;scene.add(ground);
 scene.add(new T.AmbientLight(0xffffff,1.5));
 const sun=new T.DirectionalLight(0xfff5df,2.7);sun.position.set(-100,-80,290);sun.target.position.set(75,67,0);scene.add(sun,sun.target);sun.castShadow=true;
 Object.assign(sun.shadow.camera,{left:-130,right:130,top:135,bottom:-135,far:650});sun.shadow.mapSize.set(2048,2048);sun.shadow.bias=-.0003;sun.shadow.normalBias=.1;
 function draw(){renderer.render(scene,camera)}
 function view(top){controls.target.set(108,100.5,25);camera.position.copy(controls.target).add(top?new T.Vector3(0,-.01,290):new T.Vector3(52,-146,245));camera.zoom=1;camera.updateProjectionMatrix();controls.update();draw()}
 function resize(){const w=stage.clientWidth,h=stage.clientHeight,half=Math.max(134,143*h/w);Object.assign(camera,{left:-half*w/h,right:half*w/h,top:half,bottom:-half});camera.updateProjectionMatrix();renderer.setSize(w,h,false);draw()}
 controls.addEventListener('change',draw);document.querySelector('#iso').onclick=()=>view(false);document.querySelector('#top').onclick=()=>view(true);
 view(false);resize();new ResizeObserver(resize).observe(stage);stage.dataset.ready='true';
}
setup().catch(()=>{canvas.hidden=true;stage.style.background="center / contain no-repeat url('tray-preview.png'), #d3ded4";stage.querySelector('.controls').hidden=true;document.querySelector('#hint').textContent='Model preview';});
