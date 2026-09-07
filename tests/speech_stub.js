// Test-only speech double. Never loaded or shipped by the app.
window.__audio={calls:[],mode:'ok',current:null};
Object.defineProperty(window,'SpeechSynthesisUtterance',{configurable:true,value:class {
  constructor(text){this.text=text;this.lang='';this.rate=1;}
}});
Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{
  getVoices(){return [{lang:'es-MX',name:'Test Spanish',voiceURI:'test-es-MX'}];},
  addEventListener(){},resume(){},
  cancel(){const u=window.__audio.current;window.__audio.current=null;u?.onerror?.({error:'canceled'});},
  speak(u){
    const a=window.__audio,behavior=a.mode;
    a.calls.push({text:u.text,lang:u.lang,rate:u.rate});a.current=u;
    if(behavior==='throw')throw new Error('Test audio unavailable');
    if(behavior==='silent')return;
    queueMicrotask(()=>{
      if(a.current!==u)return;
      if(behavior==='fail-before'){a.current=null;u.onerror?.({error:'not-allowed'});return;}
      u.onstart?.({});
      if(behavior==='hold')return;
      setTimeout(()=>{
        if(a.current!==u)return;
        a.current=null;
        if(behavior==='fail-after')u.onerror?.({error:'audio-hardware'});
        else u.onend?.({});
      },40);
    });
  }
}});
