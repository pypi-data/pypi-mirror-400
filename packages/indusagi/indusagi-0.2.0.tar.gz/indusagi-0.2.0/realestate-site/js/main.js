document.addEventListener('DOMContentLoaded',()=>{
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('primary-nav');
  if(menuToggle){
    menuToggle.addEventListener('click',()=>{
      const expanded = menuToggle.getAttribute('aria-expanded') === 'true';
      menuToggle.setAttribute('aria-expanded', String(!expanded));
      nav.classList.toggle('open');
    });
  }

  document.getElementById('year') && (document.getElementById('year').textContent = new Date().getFullYear());

  let listingsData = [];

  fetch('data/listings.json')
    .then(r=>r.json())
    .then(data=>{
      listingsData = data;
      renderFeatured(data.slice(0,3));
      if(document.getElementById('listings-grid')) renderListings(data);
      if(document.getElementById('property-root')) renderPropertyFromQuery(data);
    }).catch(err=>{console.error('Failed to load listings',err)});

  function renderFeatured(items){
    const featuredGrid = document.getElementById('featured-grid');
    if(!featuredGrid) return;
    featuredGrid.innerHTML = '';
    items.forEach(item=> featuredGrid.appendChild(createPropertyCard(item)));
  }

  function renderListings(items){
    const grid = document.getElementById('listings-grid');
    const qInput = document.getElementById('filter-q');
    const bedsSelect = document.getElementById('filter-beds');
    const clearBtn = document.getElementById('filter-clear');

    const resultCount = document.createElement('p');
    resultCount.className = 'result-count';
    grid.parentNode.insertBefore(resultCount, grid);

    function applyFilters(){
      const q = qInput.value.trim().toLowerCase();
      const beds = bedsSelect.value;
      let results = items.filter(it=>{
        const matchesQ = !q || it.city.toLowerCase().includes(q) || it.title.toLowerCase().includes(q);
        const matchesBeds = !beds || it.beds >= Number(beds);
        return matchesQ && matchesBeds;
      });
      resultCount.textContent = `${results.length} result${results.length!==1?'s':''}`;
      grid.innerHTML = '';
      if(results.length===0){
        grid.innerHTML = '<p>No results found.</p>';
        return;
      }
      results.forEach(r=> grid.appendChild(createPropertyCard(r)));
    }

    qInput && qInput.addEventListener('input', debounce(applyFilters,250));
    bedsSelect && bedsSelect.addEventListener('change', applyFilters);
    clearBtn && clearBtn.addEventListener('click', ()=>{ if(qInput) qInput.value=''; if(bedsSelect) bedsSelect.value=''; applyFilters(); });

    applyFilters();
  }

  function renderPropertyFromQuery(items){
    const params = new URLSearchParams(location.search);
    const id = params.get('id');
    const root = document.getElementById('property-root');
    if(!id){ root.innerHTML = '<p>Missing property id.</p>'; return; }
    const item = items.find(i=>i.id===id);
    if(!item){ root.innerHTML = '<p>Property not found.</p>'; return; }
    root.innerHTML = `
      <article class="property-detail">
        <h1>${escapeHtml(item.title)}</h1>
        <div class="property-layout">
          <div class="gallery">
            <img src="${firstImage(item)}" alt="${escapeHtml(item.title)}" loading="lazy">
          </div>
          <aside class="details">
            <div class="price">$${numberWithCommas(item.price)}</div>
            <p class="location">${escapeHtml(item.city)}</p>
            <p>${escapeHtml(item.description)}</p>
            <p><a href="contact.html?ref=${item.id}" class="btn primary">Contact Agent</a></p>
          </aside>
        </div>
      </article>
    `;
  }

  function createPropertyCard(item){
    const card = document.createElement('article');
    card.className = 'property-card';
    const imgSrc = firstImage(item);
    const saved = isSaved(item.id);
    card.innerHTML = `
      <a href="property.html?id=${item.id}" class="card-link">
        <div class="card-media">
          <img src="${imgSrc}" alt="${escapeHtml(item.title)}" loading="lazy">
          <button class="save-btn" data-id="${item.id}" aria-pressed="${saved}">${saved? '♥' : '♡'}</button>
        </div>
        <div class="meta">
          <h3>${escapeHtml(item.title)}</h3>
          <div class="property-meta">
            <div class="price">$${numberWithCommas(item.price)}</div>
            <div class="location">${escapeHtml(item.city)}</div>
          </div>
        </div>
      </a>
    `;
    // save button handler (delegate)
    const btn = card.querySelector('.save-btn');
    btn.addEventListener('click', (e)=>{
      e.preventDefault();
      e.stopPropagation();
      toggleSaved(item.id);
      const isNow = isSaved(item.id);
      btn.textContent = isNow? '♥' : '♡';
      btn.setAttribute('aria-pressed', String(isNow));
    });
    return card;
  }

  function firstImage(item){
    if(item.images && item.images.length && item.images[0]) return item.images[0];
    return `https://picsum.photos/seed/${item.id}/800/600`;
  }

  function numberWithCommas(x){return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g,",")}
  function escapeHtml(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}

  // simple saved properties using localStorage
  function getSaved(){try{const v=localStorage.getItem('savedProperties');return v?JSON.parse(v):[]}catch(e){return []}}
  function isSaved(id){return getSaved().indexOf(id)!==-1}
  function toggleSaved(id){const arr=getSaved();const idx=arr.indexOf(id);if(idx===-1){arr.push(id)}else{arr.splice(idx,1)}localStorage.setItem('savedProperties',JSON.stringify(arr))}

  function debounce(fn,ms){let t;return (...args)=>{clearTimeout(t);t=setTimeout(()=>fn.apply(this,args),ms)}}

});