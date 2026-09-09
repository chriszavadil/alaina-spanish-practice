"""Preserve selection without canceling touchscreen clicks on accent keys."""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
old_pointer="document.addEventListener('pointerdown',event=>{if(event.target.closest('.accent-key'))event.preventDefault();});"
new_pointer="""// Remember the text selection before a touch focuses an accent button.
let accentSelection=null;
document.addEventListener('pointerdown',event=>{
  accentSelection=null;
  const key=event.target.closest('.accent-key'),input=document.getElementById('answer-input');
  if(!key||key.disabled||!input||input.disabled)return;
  accentSelection={input,start:input.selectionStart??input.value.length,end:input.selectionEnd??input.value.length};
  // Do not cancel a touch pointerdown: some WebKit versions suppress its click.
  if(event.pointerType==='mouse')event.preventDefault();
});"""
old_action="""      input.focus({preventScroll:true});
      const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
      input.setRangeText(button.dataset.letter,start,end,'end');"""
new_action="""      const remembered=accentSelection?.input===input?accentSelection:null;
      accentSelection=null;
      const start=remembered?.start??input.selectionStart??input.value.length,end=remembered?.end??input.selectionEnd??start;
      input.focus({preventScroll:true});
      input.setRangeText(button.dataset.letter,start,end,'end');"""
for name in ['index.html','docs/index.html']:
 p=root/name;s=p.read_text(encoding='utf-8')
 if new_pointer in s:continue
 assert s.count(old_pointer)==1 and s.count(old_action)==1,'Unexpected input handlers; inspect before patching'
 s=s.replace(old_pointer,new_pointer).replace(old_action,new_action)
 p.write_text(s,encoding='utf-8')
assert (root/'index.html').read_bytes()==(root/'docs/index.html').read_bytes()
print('Touch selection patch applied; vocabulary and speech unchanged.')
print('HTML SHA256',hashlib.sha256((root/'index.html').read_bytes()).hexdigest())
