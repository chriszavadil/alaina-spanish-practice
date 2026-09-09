"""Transcription of the six supplied photos. No worksheet pictures or private notes shipped."""
from copy import deepcopy

def build_unit2(unit1):
    cats=[]; cards=[]
    def category(id,name,spanish,description,supplemental=False):
        cats.append(dict(id='u2-'+id,name=name,spanish=spanish,symbol='✦',description=description,unit='unit2',supplemental=supplemental))
    def add(cat,id,en,forms,source,note='',**extra):
        cards.append(dict(id='u2-'+id,category='u2-'+cat,en=en,forms=forms,source=source,note=note,punctuationOptional=True,**extra))
    category('greetings','Greetings & goodbyes','Saludos y despedidas','16 expressions, grouped by meaning')
    rows=[('hello','Hello',['¡Hola!']),('how-are-you','How are you?',['¿Qué tal?','¿Cómo estás?']),('how-going','How is it going?',['¿Cómo te va?']),('fine-and-you',"I’m fine, and you?",['Bien, ¿y tú?']),('fine-thanks',"I’m fine, thanks.",['Bien, gracias.']),('life',"How’s life treating you?",['¿Qué es de tu vida?']),('morning','Good morning',['Buenos días.']),('afternoon','Good afternoon',['Buenas tardes.']),('night','Good evening / Good night',['Buenas noches.']),('goodbye','Goodbye',['¡Adiós!','¡Chao!']),('tomorrow','See you tomorrow',['¡Hasta mañana!']),('soon','See you soon',['¡Hasta pronto!']),('later','See you later',['¡Hasta luego!','¡Nos vemos!'])]
    for id,en,forms in rows:add('greetings',id,en,forms,'IMG_2355.jpeg','Punctuation is optional in this practice quiz; accent marks still count.')
    category('days','Days of the week','Los días de la semana','All 7 days, including their accents')
    for en,es in [('Monday','lunes'),('Tuesday','martes'),('Wednesday','miércoles'),('Thursday','jueves'),('Friday','viernes'),('Saturday','sábado'),('Sunday','domingo')]:
        add('days','day-'+en.lower(),en,['el '+es],'IMG_2356.jpeg','Days are lowercase in Spanish. The article el is optional here.')
    category('numbers','Numbers 0–31','Los números','32 number cards; includes cero')
    old={c['number']:c for c in unit1['cards'] if 'number' in c}
    add('numbers','number-0','zero',['cero'],'IMG_2356.jpeg',number=0)
    for n in range(1,32):
        forms=deepcopy(old[n]['forms']);en=old[n]['en'];note=old[n].get('note','')
        if n==21:
            forms=['veintiuno','veintiuna','veintiún'];en='twenty-one (forms on the page)'
            note='The page lists three forms: veintiuno when counting, veintiuna before a feminine noun, and veintiún before a masculine noun. Choose one in the spelling quiz; in Listen & Spell, write the exact form spoken.'
        add('numbers','number-'+str(n),en,forms,'IMG_2356.jpeg',note,number=n)
    category('months','Months','Los meses','All 12 months')
    for en,es in [('January','enero'),('February','febrero'),('March','marzo'),('April','abril'),('May','mayo'),('June','junio'),('July','julio'),('August','agosto'),('September','septiembre'),('October','octubre'),('November','noviembre'),('December','diciembre')]:
        add('months','month-'+en.lower(),en,[es],'IMG_2357.jpeg','Months are lowercase in Spanish.')
    category('seasons','Seasons','Las estaciones','Winter, spring, summer & fall')
    for id,en,es in [('winter','winter','el invierno'),('spring','spring','la primavera'),('summer','summer','el verano'),('fall','fall / autumn','el otoño')]:add('seasons',id,en,[es],'IMG_2359.jpeg')
    category('weather','Weather','El tiempo','10 conditions + llover and nevar')
    weather=[('good-weather','The weather is nice.',['Hace buen tiempo.']),('bad-weather','The weather is bad.',['Hace mal tiempo.']),('hot','It is hot.',['Hace calor.']),('cold','It is cold.',['Hace frío.']),('sunny','It is sunny.',['Hace sol.','Está soleado.']),('snowing','It is snowing.',['Está nevando.']),('clear','The sky is clear.',['Está despejado.']),('cloudy','It is cloudy.',['Está nublado.']),('windy','It is windy.',['Hace viento.','Está ventoso.']),('raining','It is raining.',['Está lloviendo.']),('to-snow','to snow',['nevar']),('to-rain','to rain',['llover'])]
    for id,en,forms in weather:add('weather',id,en,forms,'IMG_2358.jpeg','Use the phrase from the page. Punctuation is optional; frío and está keep their accents.' if len(forms[0])>6 else 'This is the infinitive printed in parentheses, not the complete weather sentence.')
    category('classroom','Classroom objects','En el salón de clase','All 9 pictured objects')
    for id,en,es in [('pen','pen','el bolígrafo'),('notebook','notebook','el cuaderno'),('pencil-case','pencil case','el estuche'),('eraser','eraser','la goma'),('pencil','pencil','el lápiz'),('book','book','el libro'),('marker','marker / highlighter','el marcador'),('backpack','backpack','la mochila'),('scissors','scissors','las tijeras')]:
        note='The page uses the plural las tijeras. Write tijeras or las tijeras, not la tijeras.' if id=='scissors' else 'Use the word pictured on the page. The matching article is optional in this quiz.'
        add('classroom',id,en,[es],'IMG_2360.jpeg',note)
    category('phrases','Extra: dates & phrases','Fechas y preguntas','Optional: visible questions and sentence starters',True)
    extra=[('what-day','What day is it today?',['¿Qué día es hoy?'],'IMG_2356.jpeg',''),('favorite-month','My favorite month is…',['Mi mes favorito es'],'IMG_2357.jpeg','Sentence starter: practice just the printed words, without adding your own month.'),('birthday-in','My birthday is in…',['Mi cumpleaños es en'],'IMG_2357.jpeg','Sentence starter: practice just these words, without adding a month.'),('school-starts','School starts in…',['La escuela empieza en'],'IMG_2357.jpeg','Sentence starter: practice just these words, without adding a month.'),('today-is','Today is…',['Hoy es'],'IMG_2357.jpeg','Sentence starter from the speech bubbles.'),('december-31','Today is December 31.',['Hoy es treinta y uno de diciembre'],'IMG_2357.jpeg','The photo writes 31 as digits. For spelling practice, write the number in words.'),('year-end',"New Year’s Eve / year’s end",['Fin de Año'],'IMG_2357.jpeg','Event caption on the page; this quiz does not ask you to invent an unheard date.'),('veterans','Veterans Day',['Día de los Veteranos'],'IMG_2357.jpeg','Event caption on the page.'),('independence','Independence Day',['Día de la Independencia'],'IMG_2357.jpeg','Event caption on the page.'),('what-is-this','What is this?',['¿Qué es esto?'],'IMG_2360.jpeg','Question heading above the listening exercise.'),('this-is','This is a… (masculine)',['Esto es un'],'IMG_2360.jpeg','The printed sentence starter; stop before the missing object. Un is part of this phrase.'),('what-weather','What is the weather like?',['¿Qué tiempo hace?'],'IMG_2358.jpeg','Question heading at the top of the weather page.')]
    for id,en,forms,source,note in extra:add('phrases',id,en,forms,source,note,articleOptional=False)
    category('map','Extra: map labels','Los hemisferios','Optional: hemispheres, equator & oceans',True)
    for id,en,es in [('north','Northern Hemisphere','hemisferio norte'),('south','Southern Hemisphere','hemisferio sur'),('equator','equator','ecuador'),('pacific','Pacific Ocean','océano Pacífico'),('atlantic','Atlantic Ocean','océano Atlántico'),('arctic','Arctic Ocean','océano Ártico'),('indian','Indian Ocean','océano Índico'),('antarctic','Southern / Antarctic Ocean','océano Antártico')]:
        add('map','map-'+id,en,['el '+es],'IMG_2359.jpeg','Printed map label, with el added for noun practice; el is optional. Ecuador here means the equator, not the country.' if id=='equator' else 'Printed map label, with el added for noun practice; el is optional.')
    for cat in cats:cat['count']=sum(c['category']==cat['id'] for c in cards)
    assert len(cards)==109 and sum(c['count'] for c in cats if not c['supplemental'])==89
    return {'id':'unit2','name':'Unit 2','description':'Greetings, calendar, weather & classroom','source':'Six supplied textbook photos; app Unit 2 (book labels Unidad 0)','categories':cats,'cards':cards}
