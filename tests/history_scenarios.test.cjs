const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),d=require('../history-src/data.json'),scenarios=require('../history-src/scenarios.json');
test('All 15 worksheet terms have four distinct situations and explanations',()=>{
 assert.equal(d.version,'1.1.1');assert.equal(d.cards.length,15);assert.deepEqual(Object.keys(scenarios).sort(),d.cards.map(c=>c.id).sort());const prompts=[];
 for(const c of d.cards){assert.deepEqual(c.scenarios,scenarios[c.id]);assert.equal(c.scenarios.length,4);for(const s of c.scenarios){assert.ok(s.text.length>80&&s.why.length>50);assert.ok(!s.text.toLowerCase().includes(c.term.toLowerCase()),'Prompt gives away '+c.term);prompts.push(s.text);}}
 assert.equal(new Set(prompts).size,60);
});
test('Rendered source includes distinct scenario entry point and preserved local storage',()=>{
 const h=fs.readFileSync(path.join(root,'history/index.html'),'utf8');assert.ok(h.includes("['scenario','Scenario Practice'"));assert.ok(h.includes('Why this term fits'));assert.ok(h.includes('Scenario examples'));assert.ok(h.includes("STORE='alaina-history-studio-v1'"));assert.ok(!h.includes('alaina-spanish-practice-v1'));
 assert.equal(h,fs.readFileSync(path.join(root,'docs/history/index.html'),'utf8'));
 for(const [,attrs,s] of h.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g))if(!attrs.includes('application/json'))new vm.Script(s);
 for(const p of ['history/sw.js','docs/history/sw.js'])assert.ok(fs.readFileSync(path.join(root,p),'utf8').includes('v1.1.1'));
});
