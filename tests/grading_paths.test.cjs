const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const core=require('../src/core.js');
const html=fs.readFileSync(require('node:path').join(__dirname,'../index.html'),'utf8');
const cards=JSON.parse(html.match(/<script id="vocabulary-data" type="application\/json">([\s\S]*?)<\/script>/)[1]).cards;
const martes=cards.find(c=>c.id==='u2-day-tuesday');
test('el martes screenshot: correct answer on normal and reveal paths',()=>{
 for(const value of ['el martes','martes',' EL MARTES. ','el\u00a0martes','el  martes\n'])for(const reveal of [true,false])assert.equal(core.gradeSubmission(martes,value,reveal).status,'correct');
});
test('All 263 cards and every accepted alternative survive either submission path',()=>{
 assert.equal(cards.length,263);
 for(const card of cards)for(const value of core.acceptedAnswers(card))for(const reveal of [false,true]){
  assert.equal(core.gradeSubmission(card,value,reveal).status,'correct',card.id+': '+value);
  assert.equal(core.gradeSubmission(card,value.normalize('NFD'),reveal).status,'correct',card.id);
 }
});
test('Reveal is ungraded only when input is empty; wrong and accent errors still checked',()=>{
 assert.equal(core.gradeSubmission(martes,'',true).status,'skipped');assert.equal(core.gradeSubmission(martes,'',false).status,'empty');
 assert.equal(core.gradeSubmission(martes,'\n \t',true).status,'skipped');assert.equal(core.gradeSubmission(martes,'lunes',true).status,'incorrect');
 const pais=cards.find(c=>c.id==='u2-place-country');assert.equal(core.gradeSubmission(pais,'pais',true).status,'accent');
 const manana=cards.find(c=>c.id==='u2-tomorrow');assert.equal(core.gradeSubmission(manana,'hasta manana',true).status,'incorrect');
});
test('Event-like arguments do not accidentally request skipping; heard forms stay exact',()=>{
 assert.equal(core.gradeSubmission(martes,'',{}).status,'empty');
 for(const card of cards.filter(c=>c.forms.length>1)){
  const heard={...card,forms:[card.forms[0]],alternatives:[]};
  assert.equal(core.gradeSubmission(heard,card.forms[0],true).status,'correct');
  if(!core.acceptedAnswers(heard).includes(core.normalize(card.forms[1])))assert.notEqual(core.gradeSubmission(heard,card.forms[1],true).status,'correct',card.id);
 }
});
