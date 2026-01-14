import"./CWj6FrbW.js";import"./CN51-NxK.js";import{b as Q,o as U,i as V,d as W,e as X,a as v,p as Y,j as Z,m as $,t as M,w as n,u as y,r as tt,f as z}from"./Cef1s1vS.js";import{i as et}from"./DtBwJrag.js";import{e as at,i as nt}from"./DHQpwR2r.js";import{f as it,s as ot}from"./CepVL_7U.js";import{i as rt}from"./D6HxSY24.js";import{p as e}from"./8WYl0Dy3.js";const xt=l=>{typeof document>"u"||document.documentElement.style.setProperty("--app-text-scale",`${l}`)};var lt=z('<div class="confetti svelte-rtt661"></div>'),st=z("<div></div>");function _t(l,t){Q(t,!1);let b=e(t,"size",8,10),s=e(t,"x",24,()=>[-.5,.5]),d=e(t,"y",24,()=>[.25,1]),f=e(t,"duration",8,2e3),m=e(t,"infinite",8,!1),r=e(t,"delay",24,()=>[0,50]),g=e(t,"colorRange",24,()=>[0,360]),c=e(t,"colorArray",24,()=>[]),k=e(t,"amount",8,50),u=e(t,"iterationCount",8,1),w=e(t,"fallDistance",8,"100px"),S=e(t,"rounded",8,!1),p=e(t,"cone",8,!1),A=e(t,"noGravity",8,!1),D=e(t,"xSpread",8,.15),G=e(t,"destroyOnComplete",8,!0),h=$(!1);U(()=>{!G()||m()||u()=="infinite"||setTimeout(()=>V(h,!0),(f()+r()[1])*u())});function a(i,o){return Math.random()*(o-i)+i}function O(){return c().length?c()[Math.round(Math.random()*(c().length-1))]:`hsl(${Math.round(a(g()[0],g()[1]))}, 75%, 50%)`}rt();var x=W(),R=X(x);{var T=i=>{var o=st();let _;at(o,5,()=>({length:k()}),nt,(j,dt)=>{var C=lt();M((B,E,P,q,F,H,I,J,K,L,N)=>it(C,`
        --fall-distance: ${w()??""};
        --size: ${b()??""}px;
        --color: ${B??""};
        --skew: ${E??""}deg,${P??""}deg;
        --rotation-xyz: ${q??""}, ${F??""}, ${H??""};
        --rotation-deg: ${I??""}deg;
        --translate-y-multiplier: ${J??""};
        --translate-x-multiplier: ${K??""};
        --scale: ${L??""};
        --transition-duration: ${m()?`calc(${f()}ms * var(--scale))`:`${f()}ms`};
        --transition-delay: ${N??""}ms;
        --transition-iteration-count: ${(m()?"infinite":u())??""};
        --x-spread: ${1-D()}`),[()=>n(O),()=>n(()=>a(-45,45)),()=>n(()=>a(-45,45)),()=>n(()=>a(-10,10)),()=>n(()=>a(-10,10)),()=>n(()=>a(-10,10)),()=>n(()=>a(0,360)),()=>(y(d()),n(()=>a(d()[0],d()[1]))),()=>(y(s()),n(()=>a(s()[0],s()[1]))),()=>n(()=>.1*a(2,10)),()=>(y(r()),n(()=>a(r()[0],r()[1])))]),v(j,C)}),tt(o),M(()=>_=ot(o,1,"confetti-holder svelte-rtt661",null,_,{rounded:S(),cone:p(),"no-gravity":A()})),v(i,o)};et(R,i=>{Z(h)||i(T)})}v(l,x),Y()}export{_t as C,xt as s};
//# sourceMappingURL=CRiVJAB7.js.map
