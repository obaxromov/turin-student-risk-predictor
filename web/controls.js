"use strict";
/* V7 custom controls. The original <select> and <input type=file> remain in the DOM
   as the only values that the app reads, so existing API, validation and tests keep working.
   Popovers are portaled outside cards to avoid clipped menus. */
(() => {
  const words = {
    en:{search:'Search options…',select:'Select',noFile:'No file selected',choose:'Choose file',files:'files',none:'No matching options'},
    ru:{search:'Поиск…',select:'Выбрать',noFile:'Файл не выбран',choose:'Выбрать файл',files:'файлов',none:'Нет совпадений'},
    uz:{search:'Qidirish…',select:'Tanlash',noFile:'Fayl tanlanmagan',choose:'Fayl tanlash',files:'fayl',none:'Mos variant topilmadi'}
  };
  const tr = k => (words[document.documentElement.lang]||words.en)[k];
  let open = null;
  let serial = 0;
  const escapeText = s => String(s??'');
  function labelFor(el) {
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label');
    const lab = el.closest('label');
    if(lab) {
      const parts=[...lab.childNodes].filter(n=>n!==el && n.nodeType===Node.TEXT_NODE).map(n=>n.textContent.trim()).filter(Boolean);
      if(parts.length) return parts[0];
    }
    return tr('select');
  }
  function closePicker({restore=false}={}) {
    if (!open) return;
    const {popup,button,clean} = open;
    clean();popup.remove();button.setAttribute('aria-expanded','false');
    if(restore && button.isConnected) button.focus({preventScroll:true});
    open=null;
  }
  function updateSelect(el){
    const wrap = el.closest('.liquid-select-wrap');if(!wrap)return;
    const button=wrap.querySelector('.liquid-trigger'),label=wrap.querySelector('.liquid-selected');
    if(!button||!label)return;
    const current=el.selectedOptions?.[0];
    const value=current?.label || current?.textContent || tr('select');
    if(label.textContent!==value)label.textContent=value;
    if(button.title!==value)button.title=value;
    if(open?.select===el){
      open.popup.querySelectorAll('.liquid-option').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.value===el.value)));
    }
  }
  function openPicker(el,button){
    if(open?.select===el){closePicker();return;}
    closePicker();
    const popup=document.createElement('div');popup.className='liquid-dropdown';
    const list=document.createElement('div');list.className='liquid-options';list.setAttribute('role','listbox');
    const id='liquid-options-'+(++serial);list.id=id;
    button.setAttribute('aria-controls',id);button.setAttribute('aria-expanded','true');
    const options=[...el.options];
    let shown=[];let focusIndex=0;
    let search=null;
    if(options.length>10){
      search=document.createElement('input');search.className='field liquid-search';search.type='search';
      search.placeholder=tr('search');search.setAttribute('aria-label',tr('search'));search.autocomplete='off';
      popup.append(search);
    }
    popup.append(list);document.body.append(popup);
    function position(){
      if(!button.isConnected){closePicker();return;}
      const r=button.getBoundingClientRect(),padding=8;
      const width=Math.min(Math.max(r.width,205),window.innerWidth-2*padding);
      popup.style.width=width+'px';
      const maxh=Math.min(popup.getBoundingClientRect().height,window.innerHeight-18);
      const below=window.innerHeight-r.bottom;
      let top=below>Math.min(maxh,250)||below>=r.top? r.bottom+7:r.top-maxh-7;
      top=Math.max(8,Math.min(top,window.innerHeight-maxh-8));
      popup.style.left=Math.max(padding,Math.min(r.left,window.innerWidth-width-padding))+'px';
      popup.style.top=top+'px';
    }
    function renderOptions(query=''){
      const q=query.toLocaleLowerCase().trim();list.replaceChildren();shown=[];focusIndex=0;
      options.forEach((opt,i)=>{
        if(q && !opt.textContent.toLocaleLowerCase().includes(q)) return;
        const item=document.createElement('button');item.type='button';item.className='liquid-option';
        item.setAttribute('role','option');item.textContent=opt.textContent;
        item.dataset.value=opt.value;item.dataset.index=i;
        item.setAttribute('aria-selected',String(el.value===opt.value));
        item.disabled=opt.disabled;
        item.addEventListener('click',ev=>{ev.preventDefault();pick(i);});
        list.append(item);shown.push(item);
      });
      if(!shown.length){const empty=document.createElement('p');empty.className='muted small';empty.style.padding='8px 11px';empty.textContent=tr('none');list.append(empty);}
      const active=shown.findIndex(b=>b.dataset.value===el.value && !b.disabled);
      focusIndex=Math.max(0,active);
      showFocus();position();
    }
    function showFocus(){
      shown.forEach((b,i)=>b.dataset.highlight=String(i===focusIndex));
    }
    function move(step){
      if(!shown.length)return;
      let attempts=0;
      do{focusIndex=(focusIndex+step+shown.length)%shown.length;attempts++;}while(shown[focusIndex].disabled&&attempts<=shown.length);
      showFocus();shown[focusIndex].scrollIntoView({block:'nearest'});
    }
    function pick(index){
      const opt=options[index];if(!opt||opt.disabled)return;
      el.value=opt.value;
      el.dispatchEvent(new Event('change',{bubbles:true}));
      updateSelect(el);closePicker({restore:true});
    }
    function onKey(e){
      if(e.key==='Escape'){e.preventDefault();closePicker({restore:true});}
      if(e.key==='ArrowDown'){e.preventDefault();move(1);}
      if(e.key==='ArrowUp'){e.preventDefault();move(-1);}
      if(e.key==='Home' && e.target!==search){e.preventDefault();focusIndex=0;showFocus();}
      if(e.key==='End' && e.target!==search){e.preventDefault();focusIndex=shown.length-1;showFocus();}
      if(e.key==='Enter' && shown[focusIndex]){e.preventDefault();pick(Number(shown[focusIndex].dataset.index));}
    }
    popup.addEventListener('keydown',onKey);
    const onWindowKey=e=>{if(e.key==='Escape'){e.preventDefault();closePicker({restore:true});}else if(document.activeElement===button)onKey(e);};
    const onOutside=e=>{if(!popup.contains(e.target)&&!button.contains(e.target))closePicker();};
    const onScroll=e=>{if(e.target!==list&&e.target!==search)position();};
    const onResize=()=>position();
    document.addEventListener('keydown',onWindowKey);
    document.addEventListener('pointerdown',onOutside,true);
    window.addEventListener('resize',onResize);
    window.addEventListener('scroll',onScroll,true);
    open={select:el,button,popup,clean:()=>{
      document.removeEventListener('keydown',onWindowKey);
      document.removeEventListener('pointerdown',onOutside,true);
      window.removeEventListener('resize',onResize);
      window.removeEventListener('scroll',onScroll,true);
    }};
    if(search) search.addEventListener('input',()=>renderOptions(search.value));
    renderOptions();
    if(search) search.focus({preventScroll:true});
  }
  function enhanceSelect(el){
    if(el.dataset.liquidReady)return;
    el.dataset.liquidReady='1';el.setAttribute('aria-hidden','true');el.tabIndex=-1;
    const wrap=document.createElement('span');wrap.className='liquid-select-wrap';
    el.before(wrap);wrap.append(el);el.classList.add('liquid-native');
    const trigger=document.createElement('button');trigger.type='button';trigger.className='liquid-trigger';
    trigger.setAttribute('role','combobox');trigger.setAttribute('aria-haspopup','listbox');
    trigger.setAttribute('aria-label',labelFor(el));trigger.setAttribute('aria-expanded','false');
    const text=document.createElement('span');text.className='liquid-selected';
    const chevron=document.createElement('span');chevron.className='liquid-chevron';chevron.textContent='⌄';chevron.setAttribute('aria-hidden','true');
    trigger.append(text,chevron);wrap.append(trigger);
    trigger.addEventListener('click',ev=>{ev.preventDefault();openPicker(el,trigger);});
    trigger.addEventListener('keydown',ev=>{
      if(['ArrowDown','ArrowUp',' ','Enter'].includes(ev.key)){ev.preventDefault();if(!open||open.select!==el)openPicker(el,trigger);}
    });
    el.addEventListener('change',()=>updateSelect(el));
    updateSelect(el);
  }
  function enhanceUpload(el){
    if(el.dataset.liquidReady)return;el.dataset.liquidReady='1';el.setAttribute('aria-hidden','true');el.tabIndex=-1;
    const wrap=document.createElement('div');wrap.className='liquid-upload';
    el.before(wrap);wrap.append(el);el.classList.add('liquid-native');
    const trigger=document.createElement('button');trigger.className='btn';trigger.type='button';
    trigger.textContent='↥  '+tr('choose');trigger.setAttribute('aria-label',tr('choose'));
    const filename=document.createElement('span');filename.className='liquid-filename';
    filename.textContent=tr('noFile');filename.setAttribute('role','status');
    wrap.append(trigger,filename);
    trigger.addEventListener('click',()=>el.click());
    el.addEventListener('change',()=>{
      filename.textContent=el.files.length===0?tr('noFile'):
        el.files.length===1?escapeText(el.files[0].name):el.files.length+' '+tr('files');
      filename.title=filename.textContent;
    });
    for(const type of ['dragenter','dragover'])wrap.addEventListener(type,e=>{e.preventDefault();wrap.classList.add('drag-over');});
    for(const type of ['dragleave','drop'])wrap.addEventListener(type,e=>{e.preventDefault();wrap.classList.remove('drag-over');});
    wrap.addEventListener('drop',e=>{
      if(!e.dataTransfer?.files?.length)return;
      try{
        const dt=new DataTransfer();for(const f of e.dataTransfer.files){if(!el.multiple&&dt.files.length)break;dt.items.add(f);}
        el.files=dt.files;el.dispatchEvent(new Event('change',{bubbles:true}));
      }catch(err){/* OS or browser may prohibit assigning dropped files. Native picker still works. */}
    });
  }
  let scheduled=false;
  function scan(){
    scheduled=false;
    const root=document.getElementById('app');if(!root)return;
    root.querySelectorAll('select:not([data-liquid-ready])').forEach(enhanceSelect);
    root.querySelectorAll('input[type=file]:not([data-liquid-ready])').forEach(enhanceUpload);
    // The activity dropdown replaces its options when a cohort is loaded.
    if(open && !open.button.isConnected)closePicker();
    root.querySelectorAll('select[data-liquid-ready]').forEach(updateSelect);
  }
  const root=document.getElementById('app');
  if(root){
    const obs=new MutationObserver(()=>{if(!scheduled){scheduled=true;requestAnimationFrame(scan);}});
    obs.observe(root,{subtree:true,childList:true});
    scan();
  }
})();
