/* History-only pure functions. Does not read or write another app's storage. */
(function(root){'use strict';
function normalize(value){return String(value??'').normalize('NFKC').toLocaleLowerCase('en-US').replace(/[\u2010-\u2015-]/gu,' ').replace(/^[\s.,!?]+|[\s.,!?]+$/gu,'').replace(/\s+/gu,' ').trim();}
function grade(card,value,mode='type'){const answer=normalize(value);if(!answer)return 'empty';const forms=mode==='listen'?[card.term]:[card.term,...(card.aliases||[])];return forms.some(x=>normalize(x)===answer)?'correct':'incorrect';}
function shuffle(items,random=Math.random){const a=[...items];for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function deck(pool,size,last=[]){let a=shuffle(pool);const n=size==='all'?a.length:Math.min(a.length,Number(size)||5);if(n>1&&last.length===n&&a.slice(0,n).every((x,i)=>x===last[i]))a.push(a.shift());return a.slice(0,n);}
function options(card,all){const other=shuffle(all.filter(x=>x.id!==card.id)).slice(0,3).map(x=>x.id);return shuffle([card.id,...other]);}
function escapeHTML(s){return String(s??'').replace(/[&<>"']/gu,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));}
const api={normalize,grade,shuffle,deck,options,escapeHTML};root.HistoryCore=api;if(typeof module!=='undefined')module.exports=api;
})(typeof globalThis==='undefined'?this:globalThis);
