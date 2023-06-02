from deep_translator import GoogleTranslator

# අනූශට(anusha@gmail.com) කියන්න එයාගේ උපාධිය ගැන මම සතුටු වෙනවා කියලා. මැයි 29 වෙනිදා රාත්‍රියේ cinnamon හෝටලයේ සාදයකට ඔහුට ආරාධනා කරන්න. ඔහුට මේ සඳහා විද්‍යුත් තැපෑලක් එවන්න.
# sinhala_text = 'අනූශට කියන්න එයාගේ උපාධිය ගැන මම සතුටු වෙනවා කියලා. මැයි 29 වෙනිදා රාත්‍රියේ කුරුඳු හෝටලයේ සාදයකට ඔහුට ආරාධනා කරන්න. ඔහුට මේ සඳහා විද්‍යුත් තැපෑලක් එවන්න.'
# english_text = 'Tell anusha that I happy about his graduation. Invite him party on 29th May at the cinnamon hotel at night. send an email for this to him.'
# tamil_text = 'அனுஷா (anusha@gmail.com) பட்டப்படிப்பைப் பற்றி நான் மகிழ்ச்சியடைகிறேன் என்று சொல்லுங்கள். மே 29 அன்று இரவு சினமன் ஹோட்டலில் நடக்கும் விருந்துக்கு அவரை அழைக்கவும். இதற்காக அவருக்கு மின்னஞ்சல் அனுப்புங்கள்.'


def sinhala_to_english_translator(message):
    translator = GoogleTranslator(source='si', target='en')
    translated_text = translator.translate(text=message)
    return translated_text


def tamil_to_english_translator(message):
    translator = GoogleTranslator(source='ta', target='en')
    translated_text = translator.translate(text=message)
    return translated_text


def english_to_sinhala_translator(message):
    translator = GoogleTranslator(source='en', target='si')
    translated_text = translator.translate(text=message)
    return translated_text


def english_to_tamil_translator(message):
    translator = GoogleTranslator(source='en', target='ta')
    translated_text = translator.translate(text=message)
    return translated_text


'''
afrikaans: af
albanian: sq
amharic: am
arabic: ar
armenian: hy
assamese: as
aymara: ay
azerbaijani: az
bambara: bm
basque: eu
belarusian: be
bengali: bn
bhojpuri: bho
bosnian: bs
bulgarian: bg
catalan: ca
cebuano: ceb
chichewa: ny
chinese (simplified): zh-CN
chinese (traditional): zh-TW
corsican: co
croatian: hr
czech: cs
danish: da
dhivehi: dv
dogri: doi
dutch: nl
english: en
esperanto: eo
estonian: et
ewe: ee
filipino: tl
finnish: fi
french: fr
frisian: fy
galician: gl
georgian: ka
german: de
greek: el
guarani: gn
gujarati: gu
haitian creole: ht
hausa: ha
hawaiian: haw
hebrew: iw
hindi: hi
hmong: hmn
hungarian: hu
icelandic: is
igbo: ig
ilocano: ilo
indonesian: id
irish: ga
italian: it
japanese: ja
javanese: jw
kannada: kn
kazakh: kk
khmer: km
kinyarwanda: rw
konkani: gom
korean: ko
krio: kri
kurdish (kurmanji): ku
kurdish (sorani): ckb
kyrgyz: ky
lao: lo
latin: la
latvian: lv
lingala: ln
lithuanian: lt
luganda: lg
luxembourgish: lb
macedonian: mk
maithili: mai
malagasy: mg
malay: ms
malayalam: ml
maltese: mt
maori: mi
marathi: mr
meiteilon (manipuri): mni-Mtei
mizo: lus
mongolian: mn
myanmar: my
nepali: ne
norwegian: no
odia (oriya): or
oromo: om
pashto: ps
persian: fa
polish: pl
portuguese: pt
punjabi: pa
quechua: qu
romanian: ro
russian: ru
samoan: sm
sanskrit: sa
scots gaelic: gd
sepedi: nso
serbian: sr
sesotho: st
shona: sn
sindhi: sd
sinhala: si
slovak: sk
slovenian: sl
somali: so
spanish: es
sundanese: su
swahili: sw
swedish: sv
tajik: tg
tamil: ta
tatar: tt
telugu: te
thai: th
tigrinya: ti
tsonga: ts
turkish: tr
turkmen: tk
twi: ak
ukrainian: uk
urdu: ur
uyghur: ug
uzbek: uz
vietnamese: vi
welsh: cy
xhosa: xh
yiddish: yi
yoruba: yo
zulu: zu
'''
