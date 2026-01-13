document.addEventListener('DOMContentLoaded',function(){
  var btn=document.querySelector('.nav-toggle');
  var nav=document.getElementById('primary-navigation');
  if(!btn||!nav) return;
  btn.addEventListener('click',function(){
    var expanded=this.getAttribute('aria-expanded')==='true';
    this.setAttribute('aria-expanded',String(!expanded));
    nav.classList.toggle('open');
  });

  // sticky header year
  var yearEl=document.getElementById('year');
  if(yearEl) yearEl.textContent=new Date().getFullYear();
});