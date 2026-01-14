(()=>{var U=Object.defineProperty;var Z=Object.getPrototypeOf;var _=Reflect.get;var S=(s,n)=>(n=Symbol[s])?n:Symbol.for("Symbol."+s),x=Math.pow,ee=(s,n,e)=>n in s?U(s,n,{enumerable:!0,configurable:!0,writable:!0,value:e}):s[n]=e;var p=(s,n,e)=>(ee(s,typeof n!="symbol"?n+"":n,e),e);var A=(s,n,e)=>_(Z(s),e,n);var w=(s,n,e)=>new Promise((t,i)=>{var a=l=>{try{o(e.next(l))}catch(c){i(c)}},r=l=>{try{o(e.throw(l))}catch(c){i(c)}},o=l=>l.done?t(l.value):Promise.resolve(l.value).then(a,r);o((e=e.apply(s,n)).next())}),te=function(s,n){this[0]=s,this[1]=n};var T=s=>{var n=s[S("asyncIterator")],e=!1,t,i={};return n==null?(n=s[S("iterator")](),t=a=>i[a]=r=>n[a](r)):(n=n.call(s),t=a=>i[a]=r=>{if(e){if(e=!1,a==="throw")throw r;return r}return e=!0,{done:!1,value:new te(new Promise(o=>{var l=n[a](r);if(!(l instanceof Object))throw TypeError("Object expected");o(l)}),1)}}),i[S("iterator")]=()=>i,t("next"),"throw"in n?t("throw"):i.throw=a=>{throw a},"return"in n&&t("return"),i};var M=class extends HTMLElement{connectedCallback(){var t;let n=((t=this.getAttribute("events"))==null?void 0:t.split(","))||[],e=this.getAttribute("prefix")||"kd-event-reinterpret";for(let i of n)this.addEventListener(i,a=>{let r=a.composedPath()[0];r instanceof HTMLElement&&this.dispatchEvent(new CustomEvent(`${e}-${i}`,{detail:JSON.parse(JSON.stringify({dataset:r.dataset,classList:Array.from(r.classList),tagName:r.tagName,originalDetail:a instanceof CustomEvent?a.detail:void 0})),bubbles:!0}))})}};customElements.define("kd-event-reinterpret",M);var b=class extends HTMLElement{static get shadowInit(){return{mode:"open"}}static get shadowStyle(){return""}get nanoElementRef(){return this.constructor}constructor(){super();let{shadowInit:n}=this.nanoElementRef;n&&this.attachShadow(n)}attributeChangedCallback(n,e,t){this.isConnected&&this.render()}connectedCallback(){let n=new CSSStyleSheet;n.replaceSync(this.nanoElementRef.shadowStyle);let{shadowRoot:e}=this;e&&(e.adoptedStyleSheets=[n]),this.render()}render(){}},C=class{constructor(...n){p(this,"classList");this.classList=n}},y=class{constructor(n){this.id=n}},E=class{constructor(n,e){this.key=n;this.value=e}},k=class{constructor(n){this.name=n}},H=class s{constructor(n,...e){this.tag=n;p(this,"content");this.content=e}render(){let n=document.createElement(this.tag);for(let e of this.content)if(e instanceof C)for(let t of e.classList)t&&n.classList.add(t);else e instanceof s?n.appendChild(e.render()):e instanceof HTMLElement?n.appendChild(e):e instanceof y?n.id=e.id:e instanceof E?n.dataset[e.key]=e.value:e instanceof k?n.setAttribute("name",e.name):n.appendChild(document.createTextNode(e));return n}},d={tag:(s,...n)=>new H(s,...n).render(),class:(...s)=>new C(...s),data:(s,n)=>new E(s,n),id:s=>new y(s),name:s=>new k(s)};var R=class extends b{constructor(){super();p(this,"tableElement");p(this,"renderComplete",Promise.resolve());p(this,"headerSpanMap",new Map);new MutationObserver(this.render.bind(this)).observe(this,{childList:!0}),this.addEventListener("click",e=>{e.ctrlKey&&this.classList.toggle("hover-overflow")}),this.addEventListener("mousemove",e=>{var r;let t=e.composedPath().filter(o=>o instanceof HTMLTableCellElement)[0];if(!t)return;for(;t.getBoundingClientRect().right<e.clientX;){let o=t.nextElementSibling;if(!o)break;t=o}let i=t.closest("tr"),{tableElement:a}=this;if(!(!i||!a)&&!(i.classList.contains("hover")&&t.classList.contains("hover")))if(t.tagName==="TD"){this.clearHover(),i.classList.add("hover");let o=Number(t.dataset.col),l=Number(i.dataset.row);(r=a.querySelector(`tr[data-row="${l}"] th`))==null||r.classList.add("hover");for(let h of a.querySelectorAll(`td[data-col="${o}"]`))h.classList.add("hover");let c=this.getSlotContent(t.querySelector("slot"));this.dispatchEvent(new CustomEvent("hover-cell",{detail:{row:l,col:o,content:c}}))}else this.clearHover(),a.querySelectorAll(`tr[data-row="${i.dataset.row}"]`).forEach(o=>{o.classList.add("hover")})}),this.addEventListener("mouseleave",e=>{this.clearHover(),this.dispatchEvent(new CustomEvent("clear-hover"))})}static get shadowStyle(){let e="2px";return`
      :host {
        --background: var(--kd-compact-table-background, white);
        --col-hover-background: color-mix(in srgb, orange 12%, var(--background));
        --deemph-color: color-mix(in srgb, currentcolor 26.6%, var(--background));
        --row-hover-background: color-mix(in srgb, currentcolor 7%, var(--background));
        --stripe-0: color-mix(in srgb, currentcolor 4%, var(--background));
        --stripe-1: var(--background);
        --stripe-background: repeating-linear-gradient(
              45deg,
              var(--stripe-0), var(--stripe-0) 5px,
              var(--stripe-1) 5px, var(--stripe-1) 10px);
        display: inline-block;
      }

      ::slotted(*) {
        overflow: hidden;
        padding: ${e} 8px;
        padding-right: 0;  /* No padding since ellipsis gives enough space. */
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      ::slotted(*.deemph) {
        color: var(--deemph-color);
      }

      table {
        border-collapse: collapse;
        color: inherit;
      }

      th {
        background: var(--background);
        height: 0;
        left: 0;
        padding: 0;
        position: sticky;
        text-align: right;
        z-index: 3;
      }

      /* Note that we style the child of the th since borders on sticky th
         elements apparently do not have sticky behavior. */
      th > * {
        border-right: 2px solid currentcolor;
        height: 100%;
        padding: ${e} 8px;
      }

      td {
        border-right: 1px solid lightgray;
        box-sizing: border-box;
        max-width: var(--kd-compact-table-td-width, 60px);
        min-width: var(--kd-compact-table-td-width, 60px);
        padding: 0;
        position: relative;
      }

      td > div {
        /* Restrict content to one line. */
        max-height: calc(1lh + 2 * ${e});
        overflow: hidden;
      }

      td.four {
        border-left: 3px solid lightgray;
      }

      td:empty {
        background: var(--stripe-background);
      }

      tr.hover td:empty {
        background: var(--stripe-background);
      }

      tr + tr {
        border-top: 1px solid lightgray;
      }

      tr.boundary {
        border-top: 2px solid lightgray;
      }

      th.hover,
      tr.hover,
      tr.hover th {
        background: var(--row-hover-background);
      }

      td.hover {
        background: var(--col-hover-background);
      }

      td.active::before {
        content: '';
        height: 100%;
        outline: 2px solid orange;
        position: absolute;
        width: 100%;
        z-index: 2;
      }

      .header-text {
        /* This class is only for styling and should not be a click target. */
        pointer-events: none;
      }

      tr.clickable {
        th {
          cursor: pointer;
        }
        .header-text {
          text-decoration: underline;
        }
      }

      tr.deemph {
        .header-text {
          color: var(--deemph-color);
        }
      }

      :host(.hover-overflow) td.hover ::slotted(*) {
        background: var(--col-hover-background);
        box-sizing: border-box;
        min-width: calc(100% + 1px);
        padding-right: 8px;
        position: relative;
        z-index: 1;
      }

      :host(.hover-overflow) td.hover > div {
        width: fit-content;
      }
    `}static get shadowInit(){return{mode:"open",slotAssignment:"manual"}}static get observedAttributes(){return["data-headers","data-max-folds","data-header-classes"]}get headerWidth(){var e,t,i;return((i=(t=(e=this.tableElement)==null?void 0:e.querySelector("th"))==null?void 0:t.getBoundingClientRect())==null?void 0:i.width)||0}clearHover(){var e;for(let t of((e=this.shadowRoot)==null?void 0:e.querySelectorAll(".hover"))||[])t.classList.remove("hover")}getCellAssignedNode(e,t){var i,a,r;return(r=(a=(i=this.tableElement)==null?void 0:i.querySelector(`tr[data-row="${e}"] td[data-col="${t}"] slot`))==null?void 0:a.assignedNodes())==null?void 0:r[0]}get headers(){var e;return((e=this.dataset.headers)==null?void 0:e.split(","))||[]}renderCell(e,t,i,a){let r=d.tag("td",d.tag("div",d.tag("slot"))),o=r.children[0].children[0];return e.appendChild(r),o.assign(this.children[t*i+a]),r}getHeaderSpanCount(e){return this.headerSpanMap.get(e)||1}setCellActive(e,t){var i,a,r;(r=(a=(i=this.tableElement)==null?void 0:i.querySelector(`tr[data-row="${e}"] td[data-col="${t}"]`))==null?void 0:a.classList)==null||r.add("active")}clearCellActive(){var e,t;(t=(e=this.tableElement)==null?void 0:e.querySelectorAll(".active"))==null||t.forEach(i=>{i.classList.remove("active")})}renderHeader(e){let t=this.getHeaderSpanCount(e),i=d.tag("th",d.tag("div",d.data("header",e),d.tag("span",d.class("header-text"),e)));return i.setAttribute("rowspan",String(t)),i}getHeaderClasses(e){var t;return((t=this.dataset.headerClasses)==null?void 0:t.split(" ").map(i=>i.split(":")).filter(i=>i[0]===e).flatMap(i=>i[1].split(",")).filter(i=>i))||[]}renderRows(e,t,i,a){let r=this.renderHeader(t),o=this.getHeaderSpanCount(t),l=this.getHeaderClasses(t),c=[];for(let h=0;h<o;h++){let u=d.tag("tr",d.class(...l));u.dataset.row=String(a),a>0&&h===0&&u.classList.add("boundary"),e.appendChild(u),c.push(u),h===0&&u.append(r);for(let m=0;m<h;m++)u.append(document.createElement("td"));for(let m=h;m<i;m+=o){let g=this.renderCell(u,i,a,m);g.setAttribute("colspan",String(o)),g.dataset.col=String(m),h===0&&m>0&&m%4===0&&g.classList.add("four"),u.append(g)}}return c}measureCellWidth(e){var a;let t=document.createElement("td");e.appendChild(t);let i=(a=Number(window.getComputedStyle(t).maxWidth.replace("px","")))!=null?a:0;return t.remove(),i}getSlotContent(e){var t,i;return(i=(t=e==null?void 0:e.assignedElements())==null?void 0:t[0])!=null?i:e}updateSpanCount(e,t,i){let a=Number(this.dataset.maxFolds||2),r=i.flatMap(l=>Array.from(l.querySelectorAll("slot"))).map(l=>this.getSlotContent(l)).map(l=>{if(l.classList.contains("always-elide")||l.scrollWidth<=(l instanceof HTMLElement?l.offsetWidth:0))return 1;let c=Math.ceil(Math.log2(Math.max(Math.ceil(l.scrollWidth/t),1)));return Math.min(x(2,Math.min(c,a)))}).reduce((l,c)=>Math.max(l,c),1),o=this.getHeaderSpanCount(e);return r<=o?!1:(this.headerSpanMap.set(e,r),!0)}clearSpanCounts(){this.headerSpanMap.clear()}attributeChangedCallback(e,t,i){e==="data-max-folds"&&this.clearSpanCounts(),super.attributeChangedCallback(e,t,i)}render(){return w(this,null,function*(){let{shadowRoot:e}=this;if(!e)return;let{headers:t,cellWidth:i,allRows:a}=this.renderPass(e),r=()=>{let o=!1;for(let l=0;l<t.length;l++)this.updateSpanCount(t[l],i,a[l])&&(o=!0);o&&this.renderPass(e)};return this.renderComplete=new Promise(o=>setTimeout(()=>{r(),o()},0)),this.renderComplete})}renderPass(e){e.textContent="",this.tableElement=document.createElement("table");let t=this.tableElement;e.appendChild(t);let i=this.measureCellWidth(t),{headers:a}=this,r=[],o=Math.floor(this.children.length/a.length);for(let l=0;l<a.length;l++){let c=this.renderRows(t,a[l],o,l);r.push(c)}return{headers:a,cellWidth:i,allRows:r}}};customElements.define("kd-compact-table",R);var D=class extends b{static get shadowStyle(){let n="var(--kd-multi-index-flag-color, white)";return`
      :host {
        border-left: 2px solid ${n};
        display: flex;
        flex-direction: column;
        height: 100%;
        justify-content: space-around;
        position: absolute;
        top: 0;
      }

      div {
        background: ${n};
        border-left: 0;
        border-radius: 0 2px 2px 0;
        font-weight: bold;
        min-width: 20px;
        padding: 2px 4px;
        text-align: right;
      }

      :host(.small) div {
        font-size: 10px;
        font-weight: normal;
        line-height: 12px;
        min-width: 10px;
      }

      div:empty {
        visibility: hidden;
      }
    `}static get observedAttributes(){return["data-index"]}get index(){var n,e;return(e=(n=this.dataset.index)==null?void 0:n.split(","))!=null?e:[]}render(){let{shadowRoot:n}=this;if(n){n.textContent="";for(let e of this.index){let t=document.createElement("div");t.textContent=e,n.appendChild(t)}}}};customElements.define("kd-multi-index-flag",D);function P(s,n,e,t){var a;let i=((a=s[n])==null?void 0:a[t])||0;if(n+1>=s.length)return{size:i,depth:0};{let r=[];for(let o=0;o<i;o++)r.push(P(s,n+1,e,e[n]+o));return e[n]+=i,{size:r.map(o=>o.size).reduce((o,l)=>o+l,0),children:r,depth:Math.max(...r.map(o=>o.depth))+1}}}function F(s,n,e,t,i,a,r){if(t.right<0||t.left>=s.canvas.width)return;let o=2,l=o/2,c=n==null?void 0:n.children,h=t.left,u=(c==null?void 0:c.length)||(n==null?void 0:n.size)||0,m=Math.floor(.5*(i+a));for(let g=0;g<u;g++){let v=c==null?void 0:c[g],f=t.width*((v==null?void 0:v.size)||1)/((n==null?void 0:n.size)||1),J=.8*((m+g%2+l)/(r+o))+.1;s.fillStyle=`hsl(210, 40%, ${100*J}%)`,s.fillRect(h,t.top,f,e);let G=new DOMRect(h,t.top+e,f,e),Y=g%2?m+1:i,Q=g%2?a:m;F(s,v,e,G,Y,Q,r),h+=f}}function W(s,n){let e=s.children;if(!e)return[n];for(let t=0;t<e.length;t++){if(n<e[t].size)return[t,...W(e[t],n)];n-=e[t].size}return[]}function*q(s,n,e,t,i){let{children:a}=s;if(s.depth===n){let r=a?a.map(l=>l.size):Array.from({length:s.size}).fill(1),o=[e[0]];for(let l of r)o.push((o.at(-1)||0)+l);for(let l=1;l<o.length;l++){let c=o[l-1],h=o[l];if(c>=i)break;if(h>t){let u=Math.max(c,t),m=Math.min(h,i);yield{index:l-1,size:m-u}}}e[0]+=s.size}else if(s.depth>n){if(!a)return;for(let r=0;r<a.length;r++)yield*T(q(a[r],n,e,t,i))}}var z=class extends b{constructor(){super(...arguments);p(this,"wrapperElement");p(this,"canvasElement");p(this,"currentFlag");p(this,"cursorFlag");p(this,"node",{size:0,depth:0});p(this,"numDimsFromSizes",0);p(this,"bottomCellWidth",1)}static get shadowStyle(){return`
    :host {
      --background: var(--kd-multi-dim-nav-background, white);
      --stripe-background: color-mix(in srgb, currentcolor 4%, var(--background));
      background: repeating-linear-gradient(
        45deg, var(--stripe-background), var(--stripe-background) 5px,
        var(--background) 5px, var(--background) 10px);
      cursor: none;
      display: block;
      overflow-x: auto;
      overflow-y: hidden;
      position: relative;
      user-select: none;
    }

    :host(*:hover),
    :host(*[hover]) {
      --kd-multi-dim-nav-internal-cursor-visibility: visible;
      --kd-multi-dim-nav-internal-current-filter: brightness(0.8);
    }

    kd-multi-index-flag {
      height: 100%;
      left: 0;
      position: absolute;
      top: 0;
    }

    [cursor] {
      --kd-multi-index-flag-color: var(--kd-multi-dim-nav-cursor-background, white);
      visibility: var(--kd-multi-dim-nav-internal-cursor-visibility, hidden);
    }

    [current] {
      --kd-multi-index-flag-color: var(--kd-multi-dim-nav-current-background, white);
      visibility: var(--kd-multi-dim-nav-current-visibility, visible);
      filter: var(--kd-multi-dim-nav-internal-current-filter, none);
    }

    canvas {
      left: 0;
      position: absolute;
      top: 0;
      width: 100%;
    }
  `}static get observedAttributes(){return["data-sizes","data-layout"]}get numDims(){return this.numDimsFromSizes}get totalSize(){var e;return((e=this.node)==null?void 0:e.size)||0}get rowHeight(){var e;return Number((e=this.dataset.rowHeight)!=null?e:30)}*sizeSliceInDim(e,t,i){yield*T(q(this.node,this.numDims-e-1,[0],t,i))}connectedCallback(){super.connectedCallback();let{shadowRoot:e}=this;if(!e)return;this.canvasElement=document.createElement("canvas");let t=d.class(this.dataset.layout==="small"?"small":"");this.currentFlag=d.tag("kd-multi-index-flag",t),this.cursorFlag=d.tag("kd-multi-index-flag",t),this.currentFlag.setAttribute("current",""),this.cursorFlag.setAttribute("cursor","");let i=d.tag("slot");this.wrapperElement=d.tag("div",d.id("wrapper"),i,this.currentFlag,this.cursorFlag),e.append(this.canvasElement,this.wrapperElement);let a=new MutationObserver(o=>{for(let l of new Set(o.map(c=>c.target)))l instanceof HTMLElement&&this.repositionSlottedElement(l)});i.addEventListener("slotchange",()=>{for(let o of i.assignedElements())o instanceof HTMLElement&&(a.observe(o,{attributes:!0}),this.repositionSlottedElement(o))}),this.addEventListener("mousemove",o=>{this.moveFlagToClientX(this.cursorFlag,o)}),this.addEventListener("click",o=>{let l=this.moveFlagToClientX(this.currentFlag,o);this.dispatchEvent(new CustomEvent("change-current",{detail:{position:l,index:Math.floor(this.clientXToPosition(o.clientX)/this.bottomCellWidth)}}))});let r=this.render.bind(this);this.addEventListener("scroll",r),new ResizeObserver(r).observe(this),this.render()}repositionSlottedElement(e){e.style.setProperty("top","0");let t=Number(e.dataset.begin)||0,i=Number(e.dataset.end)||0;e.style.setProperty("position","absolute"),e.style.setProperty("left",`${Math.round(this.bottomCellWidth*t)}px`),e.style.setProperty("width",`${Math.round(this.bottomCellWidth*(i-t))}px`)}moveFlagToPosition(e,t){if(!this.wrapperElement||!e)return;let i=Math.max(0,Math.min(t,(this.wrapperElement.getBoundingClientRect().width||0)-1)),a=W(this.node,Math.floor(i/this.bottomCellWidth));return e.style.setProperty("left",`${i}px`),e.setAttribute("data-index",(a!=null?a:[]).join(",")),a}clientXToPosition(e){var t,i;return e-(((i=(t=this.wrapperElement)==null?void 0:t.getBoundingClientRect())==null?void 0:i.left)||0)}moveFlagToClientX(e,t){return this.moveFlagToPosition(e,this.clientXToPosition(t.clientX))}moveCurrentFlagToIndex(e){this.moveFlagToPosition(this.currentFlag,e*this.bottomCellWidth)}attributeChangedCallback(e,t,i){if(e==="data-sizes"){let a=JSON.parse(i||"[]");this.numDimsFromSizes=a.length,this.node=P(a,0,Array.from({length:a.length}).fill(0),0),super.attributeChangedCallback(e,t,i)}}render(){var u,m,g,v,f,L;let{canvasElement:e,node:t,rowHeight:i}=this;if(!e)return;let a=e.getContext("2d");if(!a)return;let r=Math.round(this.getBoundingClientRect().width);this.bottomCellWidth=Math.max(Math.floor(r/Math.max(t.size,1)),1);let o=this.bottomCellWidth*t.size,l=i*(t.depth+1);(m=(u=this.wrapperElement)==null?void 0:u.style)==null||m.setProperty("height",`${l}px`),(v=(g=this.wrapperElement)==null?void 0:g.style)==null||v.setProperty("width",`${o}px`);let c=-r+this.scrollLeft;e.width=Math.min(2*r,o-this.scrollLeft)+r,e.height=l,e.style.setProperty("left",`${c}px`),e.style.setProperty("width",`${e.width}px`),e.style.setProperty("height",`${l}px`),a.clearRect(0,0,e.width,e.height);let h=x(2,this.numDims)-1;F(a,t,i,new DOMRect(-this.scrollLeft+r,0,o,i),0,h,h),((L=(f=this.currentFlag)==null?void 0:f.index)==null?void 0:L.length)!==t.depth&&this.moveFlagToPosition(this.currentFlag,0)}};customElements.define("kd-multi-dim-nav",z);function I(s,n,e){let{visibleRange:t,loadedRange:i,loadedMargin:a}=s,r=Math.ceil(t[1]-t[0]);if(n<i[0]||n+r>=i[1]){let o=i[1]-i[0],l=n+r+a-.5*o;e(Math.max(n,l),n)}}function $(s,n,e,t){let{loadedRange:i,loadedMargin:a,visibleRange:r}=s,[o,l]=n,c=a,h=i[0]+c,u=i[1]-c;if(u<h){let g=(h+u)/2;h=g,u=g,c=h-i[0]}let m=.5*(i[1]-i[0]);i[0]>0&&o<=h&&t(Math.ceil(r[1]-m+c),r[0]),i[1]<((e==null?void 0:e.totalSize)||0)&&l>=u&&t(Math.floor(r[0]+m-c),r[0])}function ie(s,n){s.dataset.row=String(n==null?void 0:n.row),s.dataset.col=String(n==null?void 0:n.col)}function O(s,n){return String(n==null?void 0:n.row)===(s==null?void 0:s.dataset.row)&&String(n==null?void 0:n.col)===(s==null?void 0:s.dataset.col)}function B(s,n,e,t){var h;let i=e==null?void 0:e.row,a=e==null?void 0:e.col,r=Array.from(s).filter(u=>u.hasAttribute("slot")).length,o=(s.length-r)/t;if(n.dataset.row!==String(i)&&(n.textContent="",i!=null&&a!=null))for(let u=0;u<o;u++){let m=s[i*o+u],g=document.createElement("slot");g.dataset.col=String(u),g.dataset.row=String(i),n.appendChild(g),m&&g.assign(m)}ie(n,e);let l=n.children[(h=e==null?void 0:e.col)!=null?h:-1],c=l instanceof HTMLSlotElement?l:null;for(let u of n.children)u.classList.remove("active");return c==null||c.classList.add("active"),c&&(n.scrollTop=c.offsetTop),c}function ae(s,n){let e=d.tag("select",d.id("cell-width-select"),d.tag("option","60"),d.tag("option","120"),d.tag("option","240"));return e.value=String(s||120),e.addEventListener("change",t=>{t.target instanceof HTMLSelectElement&&(n.cellWidth=String(t.target.value))}),e}function re(){let s=document.createElement("input");return s.type="checkbox",s.checked=!0,s}function se(s,n){let e=d.tag("select",d.id("tiling-select"),d.tag("option","1"),d.tag("option","2"),d.tag("option","4"));return e.value=String(x(2,s)),e.addEventListener("change",t=>{t.target instanceof HTMLSelectElement&&(n.maxFolds=String(Math.log2(Number(t.target.value))))}),e}function V(s,n,e){let t=re(),i=d.tag("div",d.id("view-options"),d.tag("span"," overflow ",t),d.tag("span"," cell width ",ae(n,s)),d.tag("span"," max tiling ",se(e,s))),a=d.tag("div",d.tag("div",d.id("message-wrapper"),d.tag("slot",d.name("message"))),d.id("info-bar"),i);return{overflowCheckbox:t,infoBar:a}}function X(s,n){let e=d.tag("div",d.id("view")),t=d.tag("div",d.class("shade")),i=d.tag("div",d.class("shade")),a=d.tag("kd-multi-dim-nav",d.data("sizes",s.sizes),d.data("rowHeight","20"),d.data("layout","small"),e,t,i),r=oe(s,n,a),o=d.tag("div",d.id("main"),d.tag("div",d.id("nav"),a),r),l=d.tag("div",d.id("detail")),c=d.tag("div",d.id("data-region"),o,l);return{main:o,dataRegion:c,compactTable:r,dimNav:a,detailPane:l,viewElement:e,shadeBefore:t,shadeAfter:i}}function oe(s,n,e){let t=[],i=[],a=Number(s.dimIndexBase)||0;for(let r=0;r<e.numDims;r++){let o=`[dim_${r+a}]`;i.push(o),t.push(`${o}:deemph`)}return s.headers&&i.push(s.headers||""),s.headerClasses&&t.push(s.headerClasses||""),d.tag("kd-compact-table",d.data("headers",i.join(",")),d.data("headerClasses",t.join(" ")),d.data("maxFolds",String(n)),d.class("hover-overflow"))}function j(s,n,e,t,i){if(t.textContent="",i){let[r,o]=e;for(let l=0;l<i.numDims;l++){let c=r;for(let{index:h,size:u}of i.sizeSliceInDim(l,r,o))for(let m=0;m<u;m++){let g=l+1<i.numDims&&m===0;t.append(d.tag("div",d.class(g?"":"deemph"),d.class("dim-index"),d.data("index",String(c++)),d.data("dimension",String(l)),String(h)))}}}let a=Array.from(s).filter(r=>!r.getAttribute("slot"));for(let r of a){let o;switch(n||"clone"){case"text":o=document.createElement("div"),o.textContent=r.textContent;for(let l of r.classList)o.classList.add(l);break;default:o=r.cloneNode(!0);break}t.appendChild(o)}}function K(){let s="var(--kd-multi-dim-table-detail-width, 30%)";return`
    :host {
      --background: var(--kd-multi-dim-table-background, white);
      /* This is used as a margin to prevent the detail outline from being clipped. */
      --detail-outline-width: var(--kd-multi-dim-table-detail-outline-width, 2px);
      --kd-compact-table-background: var(--background);
      --kd-compact-table-td-width: 120px;
      --kd-multi-dim-nav-background: var(--background);
      --kd-multi-dim-nav-current-visibility: hidden;
      --kd-multi-dim-nav-cursor-background: var(--background);
      --kd-multi-dim-nav-current-background: color-mix(in srgb, var(--background), orange 25%);
      background: var(--background);
      display: inline-block;
      position: relative;
    }

    :host([hover-col]) {
      --kd-multi-dim-nav-current-visibility: visible;
    }

    :host(.loading) {
      filter: brightness(0.9) saturate(0);
      pointer-events: none;
    }

    :host(.all-loaded) kd-multi-dim-nav {
      display: none;
    }

    :host(.clickable-dim-index) .dim-index {
      cursor: pointer;
      text-decoration: underline;
    }

    #data-region {
      display: flex;
      margin-right: var(--detail-outline-width);
      position: relative;
    }

    #main {
      display: var(--kd-multi-dim-table-main-display, flex);
      flex-direction: column;
      position: relative;
      width: calc(100% - ${s});
    }

    #nav {
      position: sticky;
      top: 0;
      width: 100%;
      z-index: 1;
    }

    #view,
    .shade {
      box-sizing: border-box;
      height: 100%;
      position: absolute;
    }

    #view {
      background: color-mix(in srgb, var(--background) 50%, transparent);
      border: 2px solid var(--background);
    }

    #view-options {
      box-sizing: border-box;
      display: var(--kd-multi-dim-table-view-options-display, flex);
      flex-wrap: wrap;
      gap: 12px;
      justify-content: flex-end;
      /* Keeps view options aligned with the detail pane when possible. */
      min-width: var(--kd-multi-dim-table-detail-width, 30%);
      padding: 4px 8px;
      row-gap: 0;
    }

    #view-options span {
      white-space: nowrap;
    }

    #info-bar {
      align-items: flex-end;
      display: flex;
      justify-content: space-between;
      margin-right: var(--detail-outline-width);
    }

    #message-wrapper {
      color: gray;
      flex: 1;
    }

    .shade {
      background: gray;
      mix-blend-mode: saturation;
    }

    #detail {
      --detail-border-width: 1px;
      border: var(--detail-border-width) solid lightgray;
      box-sizing: border-box;
      flex: 1 1;
      /* Keep height smaller than user-specified height always. When possible,
         use the height of the main element or the active cell. We add double
         the border width to avoid a scrollbar when the height is exactly
         the active cell height. */
      max-height: min(
          max(var(--main-height, 0px),
              calc(var(--active-cell-height, 0px) + 2 * var(--detail-border-width))),
          var(--kd-multi-dim-table-detail-height, 400px));
      overflow: auto;
      position: sticky;
      top: 0;
      white-space: pre-wrap;
      width: ${s};

      &:empty::before {
        align-items: center;
        box-sizing: border-box;
        color: gray;
        content: "Hover on cell to show contents here and click to toggle pinning.";
        display: flex;
        font-size: 12px;
        height: 100%;
        justify-content: center;
        padding: 16px;
        position: absolute;
        width: 100%;
      }

      slot {
        cursor: pointer;
        display: block;
        padding: 16px;
        position: relative;
      }

      slot::slotted(*) {
        cursor: default;
      }

      /* No pointer when there is only one element. */
      slot:first-child:last-child {
        cursor: default;
      }

      slot + slot {
        border-top: 1px solid lightgray;
      }

      slot.active {
        outline: var(--detail-outline-width) solid orange;
        outline-offset: calc(-1 * var(--detail-outline-width));
        z-index: 1;
      }

      slot::before {
        border-radius: 10px;
        content: '';
        display: block;
        height: 9px;
        left: 4px;
        position: absolute;
        top: 4px;
        width: 9px;
      }

      &.pinned slot.active::before {
        background: orange;
      }
    }

    kd-compact-table {
      box-sizing: border-box;
      flex-grow: 1;
      overflow-x: auto;
      overflow-y: hidden;
      /* Keep the scroll bar away from cells. */
      padding-bottom: var(--kd-compact-table-padding-bottom, 16px);
      position: relative;
      width: 100%;
      z-index: 0;
    }

    select {
      background: var(--background);
      color: currentcolor;
    }

    input {
      margin-right: 0;
      vertical-align: bottom;
    }
  `}var N=class s extends b{constructor(){super();p(this,"viewElement");p(this,"shadeBefore");p(this,"shadeAfter");p(this,"compactTable");p(this,"detailPane");p(this,"hoverCellDetail");p(this,"hoverIndex");p(this,"overflowCheckbox");p(this,"dimNav");p(this,"main");p(this,"lastScrollLeft",0);p(this,"suppressLoadRequests",0);new MutationObserver(this.onMutation.bind(this)).observe(this,{childList:!0});let{shadowRoot:e}=this;e==null||e.addEventListener("hover-cell",t=>{var a;let i=t;(a=this.dimNav)==null||a.moveCurrentFlagToIndex(i.detail.col+this.loadedRange[0]),this.setAttribute("hover-col","")},!0),e==null||e.addEventListener("clear-hover",()=>{var t;this.removeAttribute("hover-col"),this.detailPane&&!((t=this.detailPane)!=null&&t.classList.contains("pinned"))&&(this.detailPane.textContent="",this.detailPane.dataset.row="",this.detailPane.dataset.col="")},!0)}static get shadowStyle(){return K()}static get observedAttributes(){return["content-mode","data-cell-width","data-headers","data-header-classes","data-loaded-range","data-max-folds","data-sizes"]}attributeChangedCallback(e,t,i){return w(this,null,function*(){var a,r;if(e==="data-cell-width")this.style.setProperty("--kd-compact-table-td-width",`${i}px`),(a=this.compactTable)==null||a.clearSpanCounts(),yield(r=this.compactTable)==null?void 0:r.render(),this.syncViewWithVisibleRange();else if(e==="data-max-folds"){let{compactTable:o}=this;o&&(o.dataset.maxFolds=i)}else e==="data-loaded-range"?this.updateShades():A(s.prototype,this,"attributeChangedCallback").call(this,e,t,i)})}connectedCallback(){super.connectedCallback();let e=()=>{this.syncViewWithVisibleRange(),this.updateShades()};new ResizeObserver(e).observe(this),window.addEventListener("resize",()=>{setTimeout(e,0)})}get cellWidth(){return Number(this.dataset.cellWidth||120)}get maxFolds(){return Number(this.dataset.maxFolds||0)}static get shadowInit(){return{mode:"open",slotAssignment:"manual"}}get visibleRange(){let{compactTable:e,cellWidth:t}=this;if(!e)return[0,0];let{scrollLeft:i,headerWidth:a,offsetWidth:r}=e,o=this.loadedRange[0],l=i/t+o,c=l+(r-a)/t;return[l,c]}get loadedMargin(){return Number(this.dataset.loadedMargin||0)}syncViewWithVisibleRange(){let{visibleRange:e,viewElement:t}=this;return t&&(t.dataset.begin=String(e[0]),t.dataset.end=String(e[1])),e}get loadedRange(){let e=(this.dataset.loadedRange||"").split(",").map(Number),t=e[0]||0,i=e[1]||0;return[t,i]}updateShades(){let[e,t]=this.loadedRange,{shadeBefore:i,shadeAfter:a,dimNav:r}=this;!i||!a||!r||(i.dataset.begin="0",i.dataset.end=String(e),a.dataset.begin=String(t),a.dataset.end=String(r.totalSize),this.classList.toggle("all-loaded",e===0&&t>=r.totalSize))}scrollToIndex(e){var i;let t=e-this.loadedRange[0];(i=this.compactTable)==null||i.scrollTo({left:t*this.cellWidth}),this.syncViewWithVisibleRange()}dispatchRequestLoad(e,t){if(this.suppressLoadRequests>0){this.suppressLoadRequests--;return}let i=this.hasAttribute("one-request-load");i&&this.classList.contains("loading")||(this.dispatchEvent(new CustomEvent("request-load",{detail:{centerIndex:e,viewBegin:t}})),i&&this.classList.add("loading"))}get requestLoadParams(){return{loadedRange:this.loadedRange,loadedMargin:this.loadedMargin,visibleRange:this.visibleRange}}onCompactTableHoverCell(e){if(e instanceof CustomEvent){let{detailPane:t}=this;this.hoverCellDetail=e.detail,t&&!t.classList.contains("pinned")&&this.applyHoveredContent()}}onCompactTableScroll(e){var i;this.lastScrollLeft=((i=this.compactTable)==null?void 0:i.scrollLeft)||0;let{compactTable:t}=this;if(this.classList.contains("loading")&&t){t.scrollLeft=this.lastScrollLeft;return}$(this.requestLoadParams,this.syncViewWithVisibleRange(),this.dimNav,this.dispatchRequestLoad.bind(this))}onCompactTableClick(e){var t,i;if(e.ctrlKey)e.ctrlKey&&this.syncOverflowCheckbox();else{let{detailPane:a,hoverCoords:r}=this;O(a,r)?(t=this.detailPane)==null||t.classList.toggle("pinned"):((i=this.detailPane)==null||i.classList.add("pinned"),this.applyHoveredContent())}}focusDataCell(e,t){var a,r;e+=((a=this.dimNav)==null?void 0:a.numDims)||0;let i=(r=this.compactTable)==null?void 0:r.getCellAssignedNode(e,t);i instanceof HTMLElement&&(this.hoverCellDetail={row:e,col:t,content:i},this.applyHoveredContent())}get hoverCoords(){let{hoverCellDetail:e,dimNav:t}=this;if(!e||!t)return;let i=e.row-t.numDims,a=e.col;return i>=0?{row:i,col:a}:void 0}updateMainHeightCssVar(){var e,t;this.style.setProperty("--main-height",`${(t=(e=this.main)==null?void 0:e.offsetHeight)!=null?t:0}px`)}applyHoveredContent(){var l,c;let{detailPane:e,compactTable:t,hoverCoords:i,dimNav:a}=this;if(!e||!t||!a)return;let r=t.headers.length-a.numDims,o=B(this.children,e,i,r);o instanceof HTMLElement&&e.style.setProperty("--active-cell-height",`${o.offsetHeight}px`),this.updateMainHeightCssVar(),t.clearCellActive(),i&&t.setCellActive(((l=this.hoverCellDetail)==null?void 0:l.row)||0,((c=this.hoverCellDetail)==null?void 0:c.col)||0)}syncOverflowCheckbox(){let{compactTable:e,overflowCheckbox:t}=this;!e||!t||(t.checked=e.classList.contains("hover-overflow"))}render(){return w(this,null,function*(){var l;let{shadowRoot:e}=this;if(!e)return;let t=((l=this.dimNav)==null?void 0:l.scrollLeft)||0;e.textContent="";let i=V(this.dataset,this.cellWidth,this.maxFolds);e.appendChild(i.infoBar),i.overflowCheckbox.addEventListener("change",()=>{var c;(c=this.compactTable)==null||c.classList.toggle("hover-overflow"),this.syncOverflowCheckbox()});let a=X(this.dataset,this.maxFolds);e.appendChild(a.dataRegion),Object.assign(this,a);let{dimNav:r,compactTable:o}=a;o.addEventListener("hover-cell",this.onCompactTableHoverCell.bind(this)),o.addEventListener("scroll",this.onCompactTableScroll.bind(this)),o.addEventListener("click",this.onCompactTableClick.bind(this)),r.addEventListener("change-current",c=>{let{compactTable:h}=this;if(c instanceof CustomEvent&&h){let u=c.detail.index;this.scrollToIndex(u),I(this.requestLoadParams,u,this.dispatchRequestLoad.bind(this))}}),r.scrollLeft=t,a.detailPane.addEventListener("click",c=>{let{target:h}=c;if(h instanceof HTMLSlotElement){let u=Number(h.dataset.row),m=Number(h.dataset.col);this.focusDataCell(u,m),this.suppressLoadRequests=1,this.scrollToIndex(m+this.loadedRange[0])}}),this.onMutation(),yield o.renderComplete,this.syncViewWithVisibleRange(),this.updateShades()})}onMutation(){var a,r;let{compactTable:e,dimNav:t}=this;e&&this.isConnected&&j(this.children,this.getAttribute("content-mode"),this.loadedRange,e,t);let i=this.querySelectorAll('[slot="message"]');(r=(a=this.shadowRoot)==null?void 0:a.querySelector('slot[name="message"]'))==null||r.assign(...i),this.updateMainHeightCssVar()}};customElements.define("kd-multi-dim-table",N);})();
/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
/**
 * @license
 * Copyright 2024 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
//# sourceMappingURL=data_slice_webcomponents.js.map
