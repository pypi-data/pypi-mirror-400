document.addEventListener('DOMContentLoaded',function(){
  var form=document.getElementById('contact-form');
  var status=document.getElementById('form-status');
  if(form){
    form.addEventListener('submit',function(e){
      e.preventDefault();
      var name=form.querySelector('#name');
      var email=form.querySelector('#email');
      var message=form.querySelector('#message');
      if(!name.value.trim()||!email.value.trim()||!message.value.trim()){
        status.textContent='Please fill in required fields.';
        return;
      }
      var re=/^\S+@\S+\.\S+$/;
      if(!re.test(email.value)){
        status.textContent='Please enter a valid email.';
        return;
      }
      status.textContent='Message sent (simulation). Thank you!';
      form.reset();
    });
  }
});