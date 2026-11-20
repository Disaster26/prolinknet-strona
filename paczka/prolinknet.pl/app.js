(function(){
  var b=document.getElementById('burger');
  if(b){b.addEventListener('click',function(){var on=document.body.classList.toggle('menu');b.setAttribute('aria-expanded',on?'true':'false');});
    document.querySelectorAll('.nav a').forEach(function(a){a.addEventListener('click',function(){document.body.classList.remove('menu');b.setAttribute('aria-expanded','false');});});}

  document.querySelectorAll('[data-rok]').forEach(function(e){e.textContent=new Date().getFullYear();});

  var mob=document.querySelector('.mob'),cel=document.querySelector('[data-mob-od]');
  if(mob&&cel&&'IntersectionObserver' in window){
    new IntersectionObserver(function(en){en.forEach(function(x){mob.classList.toggle('widac',!x.isIntersecting&&x.boundingClientRect.top<0);});}).observe(cel);
  }

  /* tory przesuwane palcem i myszą */
  function przeciagaj(el){
    var x0=0,s0=0,ruch=false,wcisn=false;
    el.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;wcisn=true;ruch=false;x0=e.clientX;s0=el.scrollLeft;});
    window.addEventListener('pointermove',function(e){if(!wcisn)return;var d=e.clientX-x0;if(Math.abs(d)>5){ruch=true;el.classList.add('drag');}if(ruch)el.scrollLeft=s0-d;});
    window.addEventListener('pointerup',function(){if(!wcisn)return;wcisn=false;setTimeout(function(){el.classList.remove('drag');},30);});
    el.addEventListener('click',function(e){if(ruch){e.preventDefault();e.stopPropagation();ruch=false;}},true);
    el.addEventListener('dragstart',function(e){e.preventDefault();});
  }
  document.querySelectorAll('[data-tor]').forEach(function(t){
    przeciagaj(t);
    var id=t.getAttribute('data-tor'),krok=function(){var k=t.children[0];return k?k.getBoundingClientRect().width+parseFloat(getComputedStyle(t).columnGap||16):300;};
    document.querySelectorAll('[data-prev="'+id+'"]').forEach(function(p){p.addEventListener('click',function(){t.scrollBy({left:-krok(),behavior:'smooth'});});});
    document.querySelectorAll('[data-next="'+id+'"]').forEach(function(n){n.addEventListener('click',function(){t.scrollBy({left:krok(),behavior:'smooth'});});});
    var lc=document.querySelector('[data-licz="'+id+'"]');
    if(lc){var upd=function(){var n=t.children.length,i=Math.round(t.scrollLeft/krok())+1;if(t.scrollLeft+t.clientWidth>=t.scrollWidth-4)i=n;lc.textContent=Math.min(i,n)+' / '+n;};var tk=0;t.addEventListener('scroll',function(){if(!tk){tk=1;requestAnimationFrame(function(){tk=0;upd();});}},{passive:true});}
  });

  /* zgody i mapa Google (wczytywana dopiero po zgodzie albo kliknięciu) */
  function zgoda(){try{return localStorage.getItem('pl-zgody');}catch(e){return null;}}
  function wczytajMape(m){
    if(m.getAttribute('data-ok'))return; m.setAttribute('data-ok','1');
    var f=document.createElement('iframe');
    f.src=m.getAttribute('data-src'); f.title=m.getAttribute('data-tytul')||'Mapa Google'; f.loading='lazy';
    f.referrerPolicy='no-referrer-when-downgrade'; f.setAttribute('allowfullscreen','');
    var z=m.querySelector('.mapa-z'); m.appendChild(f); if(z)z.remove();
  }
  var mapy=document.querySelectorAll('.mapa[data-src]');
  mapy.forEach(function(m){var bt=m.querySelector('button');if(bt)bt.addEventListener('click',function(){wczytajMape(m);});});
  function mapyPoZgodzie(){
    if(zgoda()!=='wszystkie')return;
    if('IntersectionObserver' in window){
      var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){wczytajMape(x.target);io.unobserve(x.target);}});},{rootMargin:'300px'});
      mapy.forEach(function(m){io.observe(m);});
    }else mapy.forEach(wczytajMape);
  }
  mapyPoZgodzie();
  var ck=document.querySelector('.ck');
  if(ck){
    ck.querySelectorAll('button').forEach(function(btn){btn.addEventListener('click',function(){try{localStorage.setItem('pl-zgody',btn.getAttribute('data-z'));}catch(e){}ck.hidden=true;mapyPoZgodzie();});});
  }

  /* formularz zapytania */
  var PODGLAD=/github\.io$/.test(location.hostname);
  var KOMUNIKAT_OK='Dziękujemy, zapytanie zostało wysłane. Odpowiemy najszybciej, jak to możliwe. Na podany e-mail wysłaliśmy potwierdzenie - jeśli go nie widać, prosimy zajrzeć do folderu Spam (Oferty, Inne).';
  document.querySelectorAll('form.zap').forEach(function(f){
    var info=f.querySelector('.info'),bt=f.querySelector('button[type=submit]'),zn=f.querySelector('input[name=_z]');
    function pokaz(t,kl){info.textContent=t;info.className='info on '+kl;info.focus();}
    function pobierzZnacznik(){
      if(PODGLAD||!window.fetch)return;
      fetch(f.getAttribute('action')+'?znacznik=1',{headers:{'Accept':'application/json'},credentials:'same-origin'}).then(function(r){return r.json();}).then(function(d){if(d&&d.z)zn.value=d.z;}).catch(function(){});
    }
    var raz=false;
    f.addEventListener('focusin',function(){if(!raz){raz=true;pobierzZnacznik();}});
    f.addEventListener('submit',function(e){
      var tel=f.querySelector('[name=telefon]').value.trim(),em=f.querySelector('[name=email]').value.trim();
      if(f.querySelector('[name=imie]').value.trim().length<2){e.preventDefault();pokaz('Prosimy podać imię i nazwisko lub nazwę firmy.','err');return;}
      if(!tel&&!em){e.preventDefault();pokaz('Prosimy podać telefon lub adres e-mail, żebyśmy mogli odpowiedzieć.','err');return;}
      if(f.querySelector('[name=wiadomosc]').value.trim().length<3){e.preventDefault();pokaz('Prosimy krótko opisać zakres prac.','err');return;}
      if(!f.querySelector('[name=zgoda]').checked){e.preventDefault();pokaz('Prosimy zaznaczyć zgodę na przetwarzanie danych w celu odpowiedzi.','err');return;}
      if(PODGLAD){e.preventDefault();pokaz('To wersja testowa strony: po uruchomieniu na prolinknet.pl formularz wyśle zapytanie na biuro@prolinknet.pl, a klient dostanie potwierdzenie e-mailem.','ok');return;}
      if(!window.fetch||!window.FormData)return; /* bez JS: zwykłe wysłanie, serwer pokaże stronę z wynikiem */
      e.preventDefault(); bt.disabled=true;
      fetch(f.getAttribute('action'),{method:'POST',body:new FormData(f),headers:{'Accept':'application/json'},credentials:'same-origin'})
        .then(function(r){return r.json();})
        .then(function(d){bt.disabled=false;if(d&&d.success){f.reset();pokaz(KOMUNIKAT_OK,'ok');zn.value='';raz=false;}else pokaz((d&&d.komunikat)||'Nie udało się wysłać. Prosimy zadzwonić: 733 800 337.','err');})
        .catch(function(){bt.disabled=false;pokaz('Nie udało się wysłać. Prosimy zadzwonić: 733 800 337 albo napisać na biuro@prolinknet.pl.','err');});
    });
  });
})();
