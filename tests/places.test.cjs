const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const root=path.join(__dirname,'..'),core=require('../src/core.js'),u2=require('../src/unit2.json');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');const data=JSON.parse(html.match(/<script id="vocabulary-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const additions=u2.cards.filter(c=>c.introduced==='1.4.1');
test('Exactly the six places and one printed sentence; no heading-only or handwritten cards',()=>{
 assert.deepEqual(additions.map(c=>[c.en,c.forms[0]]),[['neighborhood','el barrio'],['capital','la capital'],['city','la ciudad'],['state','el estado'],['country','el país'],['town / village','el pueblo'],['I am of Mexican origin.','Soy de origen mexicano.']]);
 assert.equal(u2.cards.length,116);assert.equal(data.cards.length,263);assert.equal(new Set(data.cards.map(c=>c.id)).size,263);
 assert.equal(u2.categories.filter(c=>!c.supplemental).reduce((n,c)=>n+c.count,0),96);
});
test('Country retains its accent and correct article; origin requires the complete printed phrase',()=>{
 const country=additions.find(c=>c.id==='u2-place-country'),origin=additions.find(c=>c.id==='u2-origin-mexican');
 for(const value of ['el país','país'])assert.equal(core.grade(country,value).status,'correct');
 assert.equal(core.grade(country,'pais').status,'accent');assert.equal(core.grade(country,'la país').status,'incorrect');
 for(const value of ['Soy de origen mexicano.','soy de origen mexicano'])assert.equal(core.grade(origin,value).status,'correct');
 for(const value of ['origen','soy mexicano','soy de origen mexicana'])assert.equal(core.grade(origin,value).status,'incorrect');
 assert.ok(data.cards.some(c=>c.id==='personal-country'&&c.forms[0]==='el país'));
});
test('Single-file app, hosted copy and Spanish core agree; both service workers share the new version',()=>{
 assert.equal(html,fs.readFileSync(path.join(root,'docs/index.html'),'utf8'));
 assert.ok(html.includes(fs.readFileSync(path.join(root,'src/core.js'),'utf8').trim()));
 for(const f of ['sw.js','docs/sw.js'])assert.ok(fs.readFileSync(path.join(root,f),'utf8').includes("'v1.4.2'"));
 assert.ok(html.includes("const STORE = 'alaina-spanish-practice-v1'"));
});
