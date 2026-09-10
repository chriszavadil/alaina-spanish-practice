"""Read-only reproduction against the current public app; isolated browser data."""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];URL='https://chriszavadil.github.io/alaina-spanish-practice/?verify=martes'
with sync_playwright() as pw:
 for engine in ['webkit','chromium']:
  b=getattr(pw,engine).launch()
  for action in ['quiz-submit','quiz-skip']:
   ctx=b.new_context(viewport={'width':393,'height':852},is_mobile=True,has_touch=True,service_workers='block')
   ctx.add_init_script(path=str(ROOT/'tests/speech_stub.js'))
   ctx.add_init_script("localStorage.setItem('alaina-spanish-practice-v1',JSON.stringify({settings:{unit:'unit2',categories:['u2-days'],mode:'listening',length:'all'},progress:{items:{},rounds:0}}))")
   p=ctx.new_page();p.goto(URL);p.locator('[data-action=start]').tap();p.locator('[data-action=begin]').tap()
   for i in range(7):
    expect(p.locator('#quiz-submit')).to_be_enabled()
    heard=p.evaluate('__audio.calls.at(-1).text')
    if heard=='el martes':
     p.locator('#answer-input').fill('el martes');p.locator('#'+action).tap()
     print(engine,action,p.locator('.feedback-heading').inner_text(),p.evaluate("JSON.parse(localStorage.getItem('alaina-spanish-practice-v1')).progress.items['u2-day-tuesday']"),flush=True)
     assert ('correct' in (p.locator('.feedback').get_attribute('class') or ''))==(action=='quiz-submit')
     break
    p.locator('#quiz-skip').tap();p.locator('#quiz-submit').tap()
   ctx.close()
  b.close()
print('Reproduced: reveal path discards a correct typed answer; normal checking accepts el martes.')
