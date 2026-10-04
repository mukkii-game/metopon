"""言葉の読み上げ音声を VOICEVOX（春日部つむぎ）で作る。

使い方：VOICEVOX エンジンを動かしておいて（例：docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest）
    python3 tools/gen_voice.py
で assets/voice/*.wav を書き出す。

エンジンが付ける高さはアクセントが崩れることがあるので、1語を1つのアクセント句にまとめ、
東京式アクセントの決まり（1拍目と2拍目は高さが違う、アクセント核の後で下がる）で高さを付け直している。
LIST の数字はアクセントの位置（0＝平板、1＝頭高、n＝n拍目の後で下がる）。
クレジット表記：VOICEVOX:春日部つむぎ、VOICEVOX:青山龍星（ボス）
"""
import json,urllib.request,urllib.parse,sys
SP=8  # 春日部つむぎ ノーマル
def post(path,body=None,ctype='application/json'):
    req=urllib.request.Request('http://localhost:50021'+path,data=(json.dumps(body).encode() if body is not None else b''),method='POST',headers={'Content-Type':ctype})
    return urllib.request.urlopen(req).read()
def phrase(text,accent,down=0.0):
    """1つのアクセント句を作り、東京式の決まりで高さを付け直す（down＝後ろの句ほど少し低く）"""
    q=json.loads(post('/audio_query?speaker=%d&text=%s'%(SP,urllib.parse.quote(text))))
    moras=[m for a in q['accent_phrases'] for m in a['moras']]
    ap=[{'moras':moras,'accent':accent if accent>0 else len(moras),'pause_mora':None,'is_interrogative':False}]
    ap=json.loads(post('/mora_pitch?speaker=%d'%SP,ap))
    ms=ap[0]['moras'];vo=[m['pitch'] for m in ms if m['pitch']>0];base=sum(vo)/len(vo)-down
    for i,m in enumerate(ms,1):
        if accent==1: hi=(i==1)
        elif accent==0: hi=(i>=2)
        else: hi=(2<=i<=accent)
        if m['pitch']>0: m['pitch']=round(base+(0.32 if hi else -0.18)-0.025*i,3)
    # 2拍目が「ン・ッ・ー」の時は、1拍目はあまり下がらない（ウンチ は ほぼ平らに少し上がるだけ）
    if accent!=1 and len(ms)>1 and ms[1]['text'] in ('ン','ッ','ー') and ms[0]['pitch']>0:
        ms[0]['pitch']=round(ms[1]['pitch']-0.08,3)
    return q,ap[0]
def make(text,accent,out,speed=1.0,pitch=0.0):
    """text は「なすの|ちじょうえ」のように | で句に分けられる（accent も 1|3 のように）"""
    texts=text.split('|');accs=[int(x) for x in str(accent).split('|')]
    q=None;aps=[]
    for k,(t,a) in enumerate(zip(texts,accs)):
        qq,ap=phrase(t,a,down=0.12*k);q=q or qq;aps.append(ap)
    q['accent_phrases']=aps
    q['speedScale']=speed;q['pitchScale']=pitch;q['intonationScale']=1.0;q['prePhonemeLength']=0.05;q['postPhonemeLength']=0.12
    q['outputSamplingRate']=24000
    open(out,'wb').write(post('/synthesis?speaker=%d'%SP,q))
    return '/'.join(''.join(m['text'] for m in ap['moras']) for ap in aps),[[round(m['pitch'],2) for m in ap['moras']] for ap in aps]
def excite(out):
    """伝説の攻撃：「ナスの地上絵よォォッ！」を興奮した声で。語尾の よォォッ を高く上げて伸ばす"""
    q1,a1=phrase('なすの',1);q2,a2=phrase('ちじょうえよおお',3,down=0.0)
    ms=a2['moras'];base=max(m['pitch'] for m in ms if m['pitch']>0)
    for k,m in enumerate(ms[4:]):                     # よ・お・お：どんどん上がって長く
        m['pitch']=round(base+0.25+0.18*k,3);m['vowel_length']=m['vowel_length']*(1.6+0.6*k)
    for m in a1['moras']+ms[:4]:
        if m['pitch']>0:m['pitch']=round(m['pitch']+0.12,3)
    q1['accent_phrases']=[a1,a2]
    q1['speedScale']=1.18;q1['pitchScale']=0.06;q1['intonationScale']=1.5;q1['volumeScale']=1.3
    q1['prePhonemeLength']=0.05;q1['postPhonemeLength']=0.15;q1['outputSamplingRate']=24000
    open(out,'wb').write(post('/synthesis?speaker=%d'%SP,q1))
def boss_line(out):
    """ボスの名乗り（男の声：VOICEVOX 青山龍星）。文はエンジンのアクセントを使い、借りねば だけ カリネ＼バ に直す"""
    BOSS=13
    q=json.loads(post('/audio_query?speaker=%d&text=%s'%(BOSS,urllib.parse.quote('わしの名は、インドアジェネシス。地上絵の力を借りねば、わしは倒せんぞ。'))))
    for ap in q['accent_phrases']:
        if ''.join(m['text'] for m in ap['moras'])=='カリネバ':ap['accent']=3
    q['accent_phrases']=json.loads(post('/mora_pitch?speaker=%d'%BOSS,q['accent_phrases']))
    q['speedScale']=0.88;q['pitchScale']=-0.06;q['intonationScale']=1.25;q['volumeScale']=1.2
    q['prePhonemeLength']=0.1;q['postPhonemeLength']=0.2;q['outputSamplingRate']=24000
    open(out,'wb').write(post('/synthesis?speaker=%d'%BOSS,q))
def sentence(text,out,sp=SP,speed=1.0,pitch=0.0,inton=1.2,vol=1.0,acc0=None,accs=None):
    """文をそのまま読む（アクセントはエンジン任せ。acc0＝最初の句のアクセントだけ直す。おかしい所はユーザーが耳で確かめて直す）"""
    q=json.loads(post('/audio_query?speaker=%d&text=%s'%(sp,urllib.parse.quote(text))))
    accs=dict(accs or {})              # 句の番号 → アクセント（0＝平板は句の長さにする）
    if acc0 is not None: accs[0]=acc0
    for k,a in accs.items():
        ap=q['accent_phrases'][k];ap['accent']=a if a>0 else len(ap['moras'])
    if accs:
        q['accent_phrases']=json.loads(post('/mora_pitch?speaker=%d'%sp,q['accent_phrases']))
    q['speedScale']=speed;q['pitchScale']=pitch;q['intonationScale']=inton;q['volumeScale']=vol
    q['prePhonemeLength']=0.05;q['postPhonemeLength']=0.15;q['outputSamplingRate']=24000
    open(out,'wb').write(post('/synthesis?speaker=%d'%sp,q))
# 役割の説明（女の子：春日部つむぎ）。xemetous/index.html の ROLE と同じ中身。後ろの数字＝最初の言葉のアクセント直し（うんち＝頭高）
TIPS="""
gorira ごりらは、がんじょうなんだよ！
dog こいぬは、ちょこまか動くんだよ！
iruka いるかは、ホーミングするよ！
onigiri おにぎりは、みんなを元気にするよ！
suika すいかは、割れて、まわりも壊すよ！
ringo りんごは、びゅーんと速いよ！
sakana さかなは、弾を広く消すよ！
cat こねこは、地面の敵を壊すよ！
kirin きりんは、首で上の弾も消すよ！
unko うんこは、ボスにすっごく効くよ！
unchi うんちも、ボスによく効くよ！ 1
chin ちんちんは、弾を広く消すよ！
chinL おちんちんは、弾を広く消すよ！
ouchi おうちは、いちどだけ守ってくれるよ！
"""
BOSS_SP=13  # 青山龍星
LIST="""
こいぬ 0 koinu.wav
こねこ 0 koneko.wav
すいか 0 suika.wav
りんご 0 ringo.wav
さかな 0 sakana.wav
おさかな 0 osakana.wav
おにぎり 2 onigiri.wav
ごりら 1 gorira.wav
きりん 0 kirin.wav
いるか 0 iruka.wav
うんこ 1 unko.wav
うんち 1 unchi.wav
ちんちん 1 chinchin.wav
おちんちん 2 ochinchin.wav
ちんこ 1 chinko.wav
おちんこ 2 ochinko.wav
おうち 0 ouchi.wav
ツーコンボ 3 combo2.wav
スリーコンボ 4 combo3.wav
フォーコンボ 3 combo4.wav
ファイブコンボ 4 combo5.wav
シックスコンボ 5 combo6.wav
コンボ 1 combo.wav
なす 1 nasu.wav
"""
if __name__=='__main__':
    import os
    out=os.path.join(os.path.dirname(__file__),'..','assets','voice')
    for line in LIST.strip().splitlines():
        t,a,f=line.split()
        print(f,*make(t,a,os.path.join(out,f)))
    excite(os.path.join(out,'legend.wav'));print('legend.wav ナスの地上絵よォォッ！')
    boss_line(os.path.join(out,'boss_intro.wav'));print('boss_intro.wav わしの名は…（青山龍星）')
    for line in TIPS.strip().splitlines():
        k,t,*a=line.split(' ');sentence(t,os.path.join(out,'tip_%s.wav'%k),speed=1.1,inton=1.3,acc0=int(a[0]) if a else None);print('tip_%s.wav'%k,t)
    # ボスの泣き言：少し高く、抑揚を大きく（涙目）
    sentence('きちゃないの、いや〜！！',os.path.join(out,'boss_yuck.wav'),BOSS_SP,speed=1.05,pitch=0.06,inton=1.7,vol=1.2);print('boss_yuck.wav')
    sentence('インドア派なんで、おうちに帰る〜！',os.path.join(out,'boss_cry.wav'),BOSS_SP,speed=1.0,pitch=0.05,inton=1.6,vol=1.2,accs={1:0,2:1});print('boss_cry.wav')   # おうちに＝平板、かえる＝頭高
