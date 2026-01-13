document.addEventListener('DOMContentLoaded',function(){
  var items=document.querySelectorAll('.portfolio-item');
  var lightbox=document.getElementById('lightbox');
  if(!items||!lightbox) return;
  var img=lightbox.querySelector('.lightbox-image');
  var title=lightbox.querySelector('.lightbox-title');
  var close=lightbox.querySelector('.lightbox-close');

  items.forEach(function(el){
    el.addEventListener('click',function(e){
      e.preventDefault();
      var src=el.getAttribute('href');
      img.src=src;
      title.textContent=el.dataset.title||'';
      lightbox.setAttribute('aria-hidden','false');
      lightbox.focus();
    });
  });

  close.addEventListener('click',function(){
    lightbox.setAttribute('aria-hidden','true');
    img.src='';
  });

  document.addEventListener('keydown',function(e){
    if(e.key==='Escape'&&lightbox.getAttribute('aria-hidden')==='false'){
      lightbox.setAttribute('aria-hidden','true');
      img.src='';
    }
  });
});