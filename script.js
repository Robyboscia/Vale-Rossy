(() => {
  const products = window.VALE_ROSSY_PRODUCTS || [];
  const config = window.VALE_ROSSY_CONFIG || {};
  const imageUrl = photo => `assets/img/${encodeURIComponent(photo)}`;
  const byId = id => document.getElementById(id);
  const grid = byId('product-grid');
  const dialog = byId('product-dialog');
  let opened = null;
  let openedImageIndex = 0;

  function buildCard(product) {
    const article = document.createElement('article');
    article.className = 'product-card';
    const primary = imageUrl(product.photos[0]);
    const alt = product.photos[1] ? imageUrl(product.photos[1]) : primary;
    article.innerHTML = `<button class="card-image" type="button" aria-label="Guarda ${product.name}">
      <img src="${primary}" alt="${product.name}" loading="lazy" width="1152" height="1536">
      <img class="secondary-image" src="${alt}" alt="" loading="lazy" width="1152" height="1536">
      <span class="card-label">FATTO A MANO</span><span class="card-arrow" aria-hidden="true">↗</span></button>
      <div class="card-content"><div class="type">${product.tag}</div><h3>${product.name}</h3><p>${product.summary}</p><button type="button">Scopri i dettagli <span aria-hidden="true">↗</span></button></div>`;
    article.querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => openProduct(product)));
    return article;
  }

  function renderProducts(filter='tutti') {
    const selected = filter === 'tutti' ? products : products.filter(p => p.category === filter);
    grid.replaceChildren(...selected.map(buildCard));
    byId('product-count').textContent = String(selected.length).padStart(2, '0');
  }
  document.querySelectorAll('.filter').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.filter').forEach(b => { b.classList.remove('active'); b.setAttribute('aria-pressed','false'); });
      button.classList.add('active');button.setAttribute('aria-pressed','true');renderProducts(button.dataset.filter);
    });
  });

  function displayImage() {
    const photo = opened.photos[openedImageIndex];
    const main = byId('dialog-main-image');
    main.src = imageUrl(photo);
    main.alt = `${opened.name}, fotografia ${openedImageIndex+1} di ${opened.photos.length}`;
    byId('dialog-thumbs').replaceChildren(...opened.photos.map((file,index) => {
      const btn = document.createElement('button');btn.type='button';btn.className=index===openedImageIndex?'current':'';
      btn.setAttribute('aria-label',`Mostra la fotografia ${index+1}`);
      const img=document.createElement('img');img.src=imageUrl(file);img.alt='';img.loading='lazy';btn.appendChild(img);
      btn.addEventListener('click',()=>{openedImageIndex=index;displayImage()});return btn;
    }));
  }
  function messageFor(product) { return `Ciao Vale & Rossy! Ho visto sul vostro sito la creazione «${product.name}». Posso avere informazioni sulla disponibilità e sui dettagli? Grazie!`; }
  function whatsappUrl(message) {
    const phone=String(config.whatsapp||'').replace(/\D/g,'');
    return phone ? `https://wa.me/${phone}?text=${encodeURIComponent(message)}` : null;
  }
  function openProduct(product) {
    opened=product;openedImageIndex=0;
    byId('dialog-title').textContent=product.name;
    byId('dialog-description').textContent=product.summary;
    byId('copy-feedback').textContent='';
    displayImage();
    const whats=byId('modal-whatsapp');
    const url=whatsappUrl(messageFor(product));
    whats.hidden=!url;
    if(url){whats.href=url;byId('copy-message').hidden=true;}
    else byId('copy-message').hidden=false;
    dialog.showModal();
  }
  byId('close-dialog').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  dialog.addEventListener('keydown',e=>{
    if(!opened)return;
    if(e.key==='ArrowRight'){openedImageIndex=(openedImageIndex+1)%opened.photos.length;displayImage()}
    if(e.key==='ArrowLeft'){openedImageIndex=(openedImageIndex-1+opened.photos.length)%opened.photos.length;displayImage()}
  });
  byId('copy-message').addEventListener('click',async()=>{
    if(!opened)return;
    const msg=messageFor(opened);
    try{
      if(navigator.clipboard?.writeText) await navigator.clipboard.writeText(msg);
      else { const input=document.createElement('textarea');input.value=msg;input.style.position='fixed';input.style.opacity='0';document.body.appendChild(input);input.select();if(!document.execCommand('copy'))throw Error('copy');input.remove();}
      byId('copy-feedback').textContent='Messaggio copiato. Potrai inviarlo al recapito di Vale & Rossy.';
    } catch {
      byId('copy-feedback').textContent='Copia il testo qui sotto: '+msg;
    }
  });
  function configureContact() {
    const container=byId('contact-links');
    const entries=[];
    const url=whatsappUrl('Ciao Vale & Rossy! Vorrei informazioni sulle vostre creazioni natalizie.');
    if(url)entries.push({href:url,text:'Scrivici su WhatsApp ↗',external:true});
    if(config.instagram && /^https:\/\//.test(config.instagram))entries.push({href:config.instagram,text:'Instagram ↗',external:true,secondary:true});
    if(config.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(config.email))entries.push({href:'mailto:'+config.email,text:'Scrivici via email ↗',external:false,secondary:true});
    for(const item of entries){const a=document.createElement('a');a.href=item.href;a.textContent=item.text;if(item.secondary)a.classList.add('secondary');if(item.external){a.target='_blank';a.rel='noopener noreferrer';}container.appendChild(a)}
    byId('contact-placeholder').hidden=entries.length>0;
  }
  function configureStickyWhatsApp() {
    const bar=byId('whatsapp-sticky');
    if(!bar)return;
    const url=whatsappUrl('Ciao Vale & Rossy! Vorrei informazioni sulle vostre creazioni natalizie.');
    const subtitle=byId('whatsapp-sticky-subtitle');
    const action=byId('whatsapp-sticky-action');
    if(url) {
      bar.href=url;
      bar.target='_blank';
      bar.rel='noopener noreferrer';
      bar.classList.add('is-active');
      subtitle.textContent='+39 328 922 8980 · informazioni sulle creazioni';
      action.textContent='Scrivici ↗';
    } else {
      bar.removeAttribute('href');
      bar.removeAttribute('target');
      bar.removeAttribute('rel');
      bar.classList.remove('is-active');
      subtitle.textContent='Numero WhatsApp non configurato';
      action.textContent='Non disponibile';
      bar.hidden=true;
      return;
    }
    bar.hidden=false;
  }
  const menuButton=document.querySelector('.menu-toggle');
  const nav=byId('main-nav');
  menuButton.addEventListener('click',()=>{const isOpen=nav.classList.toggle('is-open');menuButton.setAttribute('aria-expanded',String(isOpen));menuButton.setAttribute('aria-label',isOpen?'Chiudi il menu':'Apri il menu')});
  nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('is-open');menuButton.setAttribute('aria-expanded','false');menuButton.setAttribute('aria-label','Apri il menu')}));
  renderProducts();configureContact();configureStickyWhatsApp();
})();
