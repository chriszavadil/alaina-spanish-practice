'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {grade,normalize,withoutVowelMarks,acceptedAnswers,makeRound,shuffle,escapeHTML} = require('../src/core.js');
const data=JSON.parse(fs.readFileSync(require('node:path').join(__dirname, '../src/data.json'),'utf8'));
const find=id=>data.cards.find(c=>c.id===id);

test('All 147 printed entries are accounted for in seven categories',()=>{
  assert.equal(data.cards.length,147);
  assert.equal(new Set(data.cards.map(c=>c.id)).size,147);
  assert.deepEqual(Object.fromEntries(data.categories.map(c=>[c.id,c.count])),{numbers:55,personal:7,greetings:4,courtesy:5,occupations:13,nationalities:35,languages:28});
  for(const c of data.categories)assert.equal(data.cards.filter(x=>x.category===c.id).length,c.count);
  assert.deepEqual(Object.fromEntries(['photo-1','photo-2','photo-3','photo-4','photo-5'].map(id=>[id,data.cards.filter(c=>c.source===id).length])),{'photo-1':23,'photo-2':32,'photo-3':30,'photo-4':35,'photo-5':27});
});
test('Numbers are exactly the printed 1–50 plus 60,70,80,90,100',()=>{
  assert.deepEqual(data.cards.filter(c=>c.category==='numbers').map(c=>c.number),[...Array.from({length:50},(_,i)=>i+1),60,70,80,90,100]);
  assert.equal(find('number-16').forms[0],'dieciséis');assert.equal(find('number-22').forms[0],'veintidós');
  assert.equal(find('number-23').forms[0],'veintitrés');assert.equal(find('number-26').forms[0],'veintiséis');
  assert.equal(find('number-31').forms[0],'treinta y uno');assert.equal(find('number-40').forms[0],'cuarenta');
});
test('Every displayed form and deliberate alternative is accepted, including without el/la',()=>{
  for(const card of data.cards){
    assert.ok(card.en.length>0);assert.ok(card.forms.length>0);
    for(const form of [...card.forms,...(card.alternatives||[])]){
      assert.equal(grade(card,form).status,'correct',`${card.id}: ${form}`);
      assert.equal(grade(card,'  '+form.toLocaleUpperCase('es').replaceAll(' ','   ')+'!  ').status,'correct',`${card.id}: uppercase/spacing`);
      assert.equal(grade(card,form.normalize('NFD')).status,'correct',`${card.id}: decomposed Unicode`);
      if(/^(el|la) /.test(form)) assert.equal(grade(card,form.replace(/^(el|la) /,'')).status,'correct',`${card.id}: bare noun`);
    }
    assert.equal(grade(card,'incorrect answer xyz').status,'incorrect');
    assert.equal(grade(card,'   ').status,'empty');
  }
});
test('Accents are required and explained, never silently graded as correct',()=>{
  for(const [id,input] of [['number-16','dieciseis'],['number-22','veintidos'],['personal-country','pais'],['nationality-nicaraguan','nicaraguense'],['personal-email','correo electronico']])assert.equal(grade(find(id),input).status,'accent');
  assert.equal(grade(find('personal-birthday'),'cumpleanos').status,'incorrect');
  assert.equal(grade(find('nationality-spanish'),'espanol').status,'incorrect');
  assert.notEqual(withoutVowelMarks('señor'),withoutVowelMarks('senor'));
});
test('Articles are optional, but wrong genders are not stripped or excused',()=>{
  assert.equal(grade(find('job-actor'),'la actor').status,'incorrect');
  assert.equal(grade(find('job-actor'),'el actriz').status,'incorrect');
  assert.equal(grade(find('personal-age'),'el edad').status,'incorrect');
  assert.equal(grade(find('job-student'),'la estudiante').status,'correct');
  assert.equal(grade(find('language-french'),'francesa').status,'incorrect');
  assert.equal(grade(find('nationality-french'),'francesa').status,'correct');
});
test('Worksheet alternatives are explicit and correct',()=>{
  for(const value of ['encantado','encantada','mucho gusto'])assert.equal(grade(find('courtesy-nice-to-meet'),value).status,'correct');
  for(const value of ['el aymara','aymara','el aimara','aimara'])assert.equal(grade(find('language-aymara'),value).status,'correct');
  for(const value of ['guineano','guineana','ecuatoguineano','ecuatoguineana'])assert.equal(grade(find('nationality-equatorial-guinean'),value).status,'correct');
  assert.equal(grade(find('job-judge'),'la juez').status,'correct');
  assert.equal(grade(find('courtesy-don-dona'),'doña Ana y don Roberto').status,'correct');
});
test('Shuffle preserves cards and makes no duplicates; repeated order is avoided',()=>{
  const pool=data.cards.slice(0,20),before=[...pool];
  for(let n=0;n<50;n++){
    const round=makeRound(pool,'10');assert.equal(round.length,10);assert.equal(new Set(round.map(c=>c.id)).size,10);
  }
  assert.deepEqual(pool,before);
  const ordered=makeRound(pool,'all',[],()=>0.99999);
  assert.deepEqual(ordered,pool);
  const again=makeRound(pool,'all',ordered.map(c=>c.id),()=>0.99999);
  assert.notDeepEqual(again.map(c=>c.id),ordered.map(c=>c.id));
  assert.deepEqual(new Set(again),new Set(pool));
  assert.equal(makeRound(pool,'all').length,20);
  assert.equal(makeRound(pool.slice(0,4),'10').length,4);
  assert.deepEqual(makeRound([],'all'),[]);
  assert.deepEqual(makeRound(pool.slice(0,1),'10', [pool[0].id]),pool.slice(0,1));
});
test('Search and results cannot inject markup from typed answers',()=>{
  assert.equal(escapeHTML('<img src=x onerror="alert(1)">'), '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;');
  assert.equal(normalize('  ¿EL   NOMBRE?  '),'el nombre');
});
