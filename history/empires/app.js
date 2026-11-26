/* Empires' notebook and study progress are independent of the other units. */
(() => {
  'use strict';
  const {escapeHTML: esc, normalize} = HistoryCore;
  const terms = HISTORY_TERMS;
  const slug = term => term.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+$/g, '');
  const bySlug = new Map(terms.map(item => [slug(item.term), item]));
  const byName = new Map(terms.map(item => [item.term, item]));
  const profiles = 'history-studio-empires-notebook-v1';
  const ids = ['matching', 'overview', 'library', 'review', 'practice'];
  const paths = {
    book:'<path d="M3 4c3-.8 6-.5 9 1.3C15 3.5 18 3.2 21 4v14c-3-.7-6-.5-9 1.5C9 17.5 6 17.3 3 18zM12 5.3v14"/>',
    stack:'<rect x="7" y="6" width="13" height="16" rx="2"/><path d="M4 17H3V3h12"/>',
    check:'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="m7 12 3 3 6-7"/>',
    flag:'<path d="M5 21V3c5-3 8 3 14 0v10c-6 3-9-3-14 0"/>',
    pencil:'<path d="m4 16 12-12a2 2 0 0 1 3 0l1 1a2 2 0 0 1 0 3L8 20l-5 1zM14 6l4 4M4 16l4 4"/>',
    sound:'<path d="m11 5-5 4H3v6h3l5 4zM15 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
    mute:'<path d="m11 5-5 4H3v6h3l5 4zM15 9l6 6m0-6-6 6"/>',
    bookmark:'<path d="M6 3h12v18l-6-4-6 4z"/>',
    search:'<circle cx="10" cy="10" r="6.5"/><path d="m15 15 5 5"/>',
    list:'<path d="M8 5h13M8 12h13M8 19h13M3 5h.1M3 12h.1M3 19h.1"/>',
    compass:'<circle cx="12" cy="12" r="9"/><path d="m15 8-2 6-5 2 2-6z"/>',
    prev:'<path d="m14 6-6 6 6 6"/>', next:'<path d="m10 6 6 6-6 6"/>'
  };
  const icon = name => '<svg class="glyph" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+paths[name]+'</svg>';
  const modes = [
    ['flash','Flashcards','Flip a card to see its meaning and drawing.','stack'],
    ['choice','Meaning quiz','Match a definition to the right term.','check'],
    ['scenario','Scenario practice','Choose the term that fits a historical situation.','flag'],
    ['type','Recall challenge','Read a clue and type the term from memory.','pencil'],
    ['listen','Listen & spell','Hear a term aloud, then spell it.','sound']
  ];
  const get = id => document.getElementById(id);
  const inputDefaults = () => ({seen:[], missed:[], saved:[], sound:true});
  let state = inputDefaults();
  let query = '';
  let lastRoute = '';
  let audioContext;
  let pendingSubset = null;
  try {
    const stored = JSON.parse(localStorage.getItem(profiles) || '{}');
    for (const group of ['seen','missed','saved']) {
      if (Array.isArray(stored?.[group])) state[group] = [...new Set(stored[group].filter(name => byName.has(name)))];
    }
    state.sound = stored?.sound !== false;
  } catch { get('storage-note').hidden = false; }

  function persist() {
    try { localStorage.setItem(profiles,JSON.stringify(state)); }
    catch { get('storage-note').hidden = false; }
    updateNav();
  }
  const review = () => terms.filter(item => state.saved.includes(item.term) || state.missed.includes(item.term));
  function updateNav() {
    const count = review().length;
    get('review-nav-count').textContent = count || '';
    const sound = get('sound');
    sound.setAttribute('aria-pressed',String(state.sound));
    sound.setAttribute('aria-label',state.sound ? 'Turn quiz sounds off' : 'Turn quiz sounds on');
    sound.innerHTML = icon(state.sound ? 'sound' : 'mute')+'<span class="sound-label">Sound '+(state.sound ? 'on':'off')+'</span>';
  }
  function updateSet(group,name,on) {
    state[group] = state[group].filter(value => value !== name);
    if (on) state[group].push(name);
  }
  function report(name, correct) {
    if (!byName.has(name)) return;
    updateSet('seen',name,true);
    updateSet('missed',name,!correct);
    persist();
  }
  function sketch(name) {
    const data = byName.get(name);
    if (!data) return '';
    return '<svg class="sketch" role="img" aria-label="'+esc(data.draw)+'" viewBox="0 0 260 140"><use href="sprite.svg#'+slug(name)+'"></use></svg>';
  }
  function playFeedback(correct) {
    if (!state.sound) return;
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      audioContext ??= new Audio();
      void audioContext.resume().catch(()=>{});
      const ctx = audioContext;
      (correct ? [523,784] : [330,220]).forEach((hz,i) => {
        const t = ctx.currentTime+i*.15, osc = ctx.createOscillator(), gain = ctx.createGain();
        osc.type = 'sine'; osc.frequency.value = hz;
        gain.gain.setValueAtTime(.001,t);gain.gain.exponentialRampToValueAtTime(.23,t+.025);
        gain.gain.exponentialRampToValueAtTime(.001,t+.23);
        osc.connect(gain).connect(ctx.destination);osc.start(t);osc.stop(t+.25);
      });
    } catch { /* Visual grading is available on every device. */ }
  }
  let speechToken = 0;
  let speechTimer;
  let currentUtterance;
  function stopSpeech() {
    speechToken++;
    clearTimeout(speechTimer);
    currentUtterance=null;
    if ('speechSynthesis' in window) speechSynthesis.cancel();
  }
  function say(text, onResult=()=>{}) {
    stopSpeech();
    if (!('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) {
      onResult(false);return false;
    }
    const token=speechToken;
    function finish(ok) {
      if (token!==speechToken) return;
      clearTimeout(speechTimer);speechToken++;currentUtterance=null;
      onResult(ok);
    }
    try {
      const phrase = new SpeechSynthesisUtterance(text);
      currentUtterance=phrase;
      const voices = speechSynthesis.getVoices();
      const voice = voices.find(v=>v.lang==='en-US') || voices.find(v=>/^en\b/i.test(v.lang));
      if (voices.length && !voice) {finish(false);return false;}
      phrase.lang=voice?.lang || 'en-US';
      if (voice) phrase.voice=voice;
      phrase.rate=.86;phrase.volume=1;
      phrase.onend=()=>finish(true);phrase.onerror=()=>finish(false);
      const timeout=()=>{if(token===speechToken){finish(false);speechSynthesis.cancel();}};
      phrase.onstart=()=>{if(token===speechToken){clearTimeout(speechTimer);speechTimer=setTimeout(timeout,55000);}};
      speechTimer=setTimeout(timeout,7000);
      speechSynthesis.resume();speechSynthesis.speak(phrase);
      return true;
    } catch { finish(false);return false; }
  }
  const crumbs = label => '<div class="crumb"><a href="#overview">Empires Vocabulary</a>'+icon('next')+'<span>'+esc(label)+'</span></div>';
  function overview() {
    const seen=state.seen.length, remaining=review().length;
    get('overview-view').innerHTML = `
    <div class="crumb"><a href="../">History Studio</a>${icon('next')}<span>Empires Vocabulary</span></div>
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow"><span class="rule"></span>World history</div>
        <h1>Empires<br><em>Vocabulary</em></h1>
        <p>Match definitions to the words in a shared bank, or look up a term in the illustrated notebook.</p>
        <div class="actions"><a class="primary" href="#matching">${icon('list')}Start word bank quiz</a><a class="secondary" href="#vocabulary">${icon('book')}Open word list</a></div>
      </div>
      <figure class="hero-figure">
        <img src="caravel.webp" alt="An illustrated caravel with triangular sails on the open sea" width="1100" height="733" fetchpriority="high">
        <figcaption>Caravel <span>·</span> Atlantic exploration</figcaption>
      </figure>
    </section>
    ${window.EmpiresPractice.hasSaved() ? '<div class="resume-box"><div><strong>You have a saved round.</strong><p>Pick up at your last question.</p></div><a class="secondary" href="#practice/resume">Resume round</a></div>' : ''}
    <section class="practice-section" aria-labelledby="modes-title">
      <div class="section-title"><h2 id="modes-title">Ways to practice</h2><span>5 study modes</span></div>
      <div class="modes">${modes.map(([key,name,copy,glyph])=>`<a class="mode-card" href="#practice/${key}"><span class="mode-icon">${icon(glyph)}</span><strong>${name}</strong><span class="mode-copy">${copy}</span></a>`).join('')}</div>
    </section>
    <section class="progress-card" aria-label="Unit progress">
      <div><div class="eyebrow">Your progress</div><h2>${seen} of ${terms.length} terms practiced</h2><progress aria-label="Terms practiced" value="${seen}" max="${terms.length}"></progress></div>
      <a class="secondary" href="#review">${icon('bookmark')}${remaining ? 'Review '+remaining+' '+(remaining===1?'term':'terms') : 'My review list'}</a>
    </section>`;
  }
  function definitionsHTML(item) {
    const texts = [item.simple, item.detailed, item.alternate];
    const labels = item.definitionLabels || ['Meaning', 'Details', 'Context'];
    return '<div class="definition-list">' + texts.map((text, i) =>
      '<div><b>' + esc(labels[i]) + '</b><p>' + esc(text) + '</p></div>'
    ).join('') + '</div>';
  }
  function detail(item) {
    const name = item.term, id = slug(name), pos = terms.indexOf(item), saved = state.saved.includes(name);
    return `<article class="entry" id="term-${id}">
      <div class="entry-head"><div><p class="eyebrow">Worksheet term ${pos+1} of ${terms.length}</p><h2>${esc(name)}</h2></div>
        <div class="entry-tools"><button data-read="${id}" class="icon-button" aria-label="Hear ${esc(name)}" title="Hear term">${icon('sound')}</button><button data-save="${id}" class="icon-button" aria-pressed="${saved}" aria-label="${saved?'Remove bookmark for':'Bookmark'} ${esc(name)}" title="${saved?'Remove bookmark':'Bookmark term'}">${icon('bookmark')}</button></div></div>
      <p id="entry-audio-status" role="status"></p><h3>Definitions</h3>${definitionsHTML(item)}
      <h3>Example sentence</h3><p class="example">${esc(item.example)}</p>
      <div class="draw-area"><figure>${sketch(name)}</figure><div><h3>Easy drawing</h3><p>${esc(item.draw)}</p><h3>Why the drawing fits</h3><p>${esc(item.why)}</p></div></div>
      ${item.scenarios?.length ? '<details class="situations"><summary>Practice situations ('+item.scenarios.length+')</summary><ol>'+item.scenarios.map(text=>'<li>'+esc(text)+'</li>').join('')+'</ol></details>' : ''}
      <div class="stepper">${pos>0?`<a href="#vocabulary/${slug(terms[pos-1].term)}" aria-label="Previous term, ${esc(terms[pos-1].term)}">${icon('prev')}Previous term</a>`:'<span></span>'}${pos<terms.length-1?`<a href="#vocabulary/${slug(terms[pos+1].term)}" aria-label="Next term, ${esc(terms[pos+1].term)}">Next term${icon('next')}</a>`:'<a href="#practice/choice">Try the meaning quiz</a>'}</div>
    </article>`;
  }
  function filtered() {
    const search = normalize(query);
    return terms.filter(item => normalize([item.term,item.simple,item.detailed,item.alternate].join(' ')).includes(search));
  }
  function renderWordList(selected) {
    const list = filtered();
    const chosen = list.find(item => item===selected) || list[0];
    get('term-count').textContent=list.length+' of '+terms.length+' terms';
    get('term-list').innerHTML = list.map(item=>`<a href="#vocabulary/${slug(item.term)}" ${item===chosen?'aria-current="true"':''}>${esc(item.term)}${item===chosen?icon('next'):''}</a>`).join('');
    get('entry-wrap').innerHTML=chosen ? detail(chosen) : '<div class="empty"><h2>No matching terms</h2><p>Try a different term or a word from its definition.</p><button class="secondary" id="clear-query">Clear search</button></div>';
  }
  function library(termId) {
    const chosen = bySlug.get(termId);
    if (chosen && !filtered().includes(chosen)) query='';
    get('library-view').innerHTML = crumbs('Word list')+`<div class="page-title"><div class="eyebrow">20 worksheet terms</div><h1>Vocabulary notebook</h1><p>Choose a term to see three definitions, an example, and a drawing you can copy.</p><a class="primary notebook-quiz" href="#matching">${icon('list')}Start word bank quiz</a></div>
    <div class="notebook"><aside class="index"><label class="search-box">${icon('search')}<input id="term-search" type="search" placeholder="Search words or definitions" aria-label="Search words or definitions" value="${esc(query)}"></label><p class="list-count" id="term-count" aria-live="polite"></p><nav id="term-list" aria-label="Worksheet terms"></nav></aside><div id="entry-wrap"></div></div>`;
    renderWordList(chosen);
  }
  function showReview() {
    const items = review();
    get('review-view').innerHTML=crumbs('My review')+`<div class="page-title"><div class="eyebrow">Personal practice</div><h1>My review list</h1><p>Bookmarked terms and missed answers appear here for another round.</p></div>
    ${items.length ? `<div class="section-title"><h2>${items.length} ${items.length===1?'term':'terms'} to revisit</h2><button class="primary" id="review-round">${icon('stack')}Practice these terms</button></div><div class="review-grid">${items.map(item=>`<article><div class="review-head"><a href="#vocabulary/${slug(item.term)}">${esc(item.term)}</a><button class="small-link" data-remove="${slug(item.term)}" aria-label="Remove ${esc(item.term)} from review">Remove</button></div><p>${esc(item.simple)}</p></article>`).join('')}</div>` : `<div class="empty"><div class="mode-icon">${icon('bookmark')}</div><h2>Your list is ready for its first term</h2><p>Use the bookmark beside a word in the notebook, or try a quiz to find terms to revisit.</p><a class="primary" href="#vocabulary">Open word list</a></div>`}`;
  }
  function route() {
    const [page,arg] = location.hash.slice(1).split('/');
    const view = page==='vocabulary' ? 'library' : ids.includes(page) ? page : 'matching';
    if (lastRoute==='practice') window.EmpiresPractice.leave();
    stopSpeech();
    ids.forEach(id => {get(id+'-view').hidden=id!==view;});
    document.querySelectorAll('[data-nav]').forEach(link=>{
      if(link.dataset.nav===(view==='library'?'vocabulary':view)) link.setAttribute('aria-current','page');else link.removeAttribute('aria-current');
    });
    if (view==='matching') window.EmpiresMatching.open();
    else if (view==='library') library(arg);
    else if (view==='review') showReview();
    else if (view==='practice') {
      if (arg==='resume' && window.EmpiresPractice.hasSaved()) window.EmpiresPractice.resume();
      else window.EmpiresPractice.open(modes.some(m=>m[0]===arg)?arg:'flash',pendingSubset);
      pendingSubset=null;
    } else overview();
    lastRoute=view;
    updateNav();
    if (view!=='practice') get('main').focus({preventScroll:true});
    if (view==='library' && arg && window.matchMedia('(max-width: 750px)').matches) get('entry-wrap').scrollIntoView({block:'start'});
    else window.scrollTo(0,0);
  }
  document.addEventListener('click',event=>{
    const b=event.target.closest('button,a');
    if (!b) return;
    if(b.classList.contains('skip')) {event.preventDefault();get('main').focus();return;}
    if(b.id==='sound') {state.sound=!state.sound;persist();if(state.sound)playFeedback(true);}
    if(b.dataset.save) {
      const item=bySlug.get(b.dataset.save), value=!state.saved.includes(item.term);
      updateSet('saved',item.term,value);persist();
      b.setAttribute('aria-pressed',String(value));b.setAttribute('aria-label',(value?'Remove bookmark for ':'Bookmark ')+item.term);
      b.title=value?'Remove bookmark':'Bookmark term';
      get('status').textContent=item.term+(value?' bookmarked.':' bookmark removed.');
    }
    if(b.dataset.read) {const item=bySlug.get(b.dataset.read); say(item.term+'. '+item.simple, ok=>{if(!ok){get('entry-audio-status').textContent='Pronunciation is unavailable. Check your device’s English voice and try again.';}});}
    if(b.dataset.remove) {const item=bySlug.get(b.dataset.remove);updateSet('saved',item.term,false);updateSet('missed',item.term,false);persist();showReview();}
    if(b.id==='clear-query') {query='';get('term-search').value='';get('term-search').focus();renderWordList();}
    if(b.id==='review-round') {pendingSubset=review().map(item=>item.term);location.hash='practice/choice';}
  });
  document.addEventListener('input',event=>{
    if(event.target.id==='term-search') {query=event.target.value;renderWordList(bySlug.get(location.hash.split('/')[1]));}
  });
  document.querySelectorAll('[data-icon]').forEach(el=>el.innerHTML=icon(el.dataset.icon));
  window.Empires={report, sketch, definitionsHTML, playFeedback, say, home:()=>{location.hash='overview';}};
  window.addEventListener('hashchange',route);
  route();
  if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'}).catch(()=>{});
})();
