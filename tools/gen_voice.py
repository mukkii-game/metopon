"""言葉の読み上げ音声を VOICEVOX（春日部つむぎ）で作る。

使い方：VOICEVOX エンジンを動かしておいて（例：docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-latest）
    python3 tools/gen_voice.py
で assets/voice/*.wav を書き出す。

エンジンが付ける高さはアクセントが崩れることがあるので、1語を1つのアクセント句にまとめ、
東京式アクセントの決まり（1拍目と2拍目は高さが違う、アクセント核の後で下がる）で高さを付け直している。
LIST の数字はアクセントの位置（0＝平板、1＝頭高、n＝n拍目の後で下がる）。
クレジット表記：VOICEVOX:春日部つむぎ
"""
import json,urllib.request,urllib.parse,sys
SP=8  # 春日部つむぎ ノーマル
def post(path,body=None,ctype='application/json'):
    req=urllib.request.Request('http://localhost:50021'+path,data=(json.dumps(body).encode() if body is not None else b''),method='POST',headers={'Content-Type':ctype})
    return urllib.request.urlopen(req).read()
def make(text,accent,out,speed=1.0,pitch=0.0):
    q=json.loads(post('/audio_query?speaker=%d&text=%s'%(SP,urllib.parse.quote(text))))
    ap=q['accent_phrases']
    # 1つのアクセント句にまとめて、アクセントの位置を指定（0＝平板はモーラ数で表す）
    moras=[m for a in ap for m in a['moras']]
    one={'moras':moras,'accent':accent if accent>0 else len(moras),'pause_mora':None,'is_interrogative':False}
    q['accent_phrases']=[one]
    q['accent_phrases']=json.loads(post('/mora_pitch?speaker=%d'%SP,q['accent_phrases']))
    # 東京式アクセントの決まりで高さを付け直す：1拍目と2拍目は高さが違う、アクセント核の後で下がる
    ms=q['accent_phrases'][0]['moras'];n=len(ms);acc=accent if accent>0 else 0
    vo=[m['pitch'] for m in ms if m['pitch']>0];base=sum(vo)/len(vo)
    for i,m in enumerate(ms,1):
        if acc==1: hi=(i==1)
        elif acc==0: hi=(i>=2)
        else: hi=(2<=i<=acc)
        if m['pitch']>0: m['pitch']=round(base+(0.32 if hi else -0.18)-0.025*i,3)
    q['speedScale']=speed;q['pitchScale']=pitch;q['intonationScale']=1.0;q['prePhonemeLength']=0.05;q['postPhonemeLength']=0.12
    q['outputSamplingRate']=24000
    open(out,'wb').write(post('/synthesis?speaker=%d'%SP,q))
    return ''.join(m['text'] for m in moras),[round(m['pitch'],2) for m in q['accent_phrases'][0]['moras']]
LIST="""
いぬ 2 inu.wav
ねこ 1 neko.wav
すいか 0 suika.wav
りんご 0 ringo.wav
さかな 0 sakana.wav
おにぎり 2 onigiri.wav
うんこ 1 unko.wav
うんち 0 unchi.wav
ちんちん 0 chinchin.wav
おちんちん 0 ochinchin.wav
ちんこ 1 chinko.wav
ツーコンボ 3 combo2.wav
スリーコンボ 4 combo3.wav
フォーコンボ 3 combo4.wav
ファイブコンボ 4 combo5.wav
シックスコンボ 5 combo6.wav
コンボ 1 combo.wav
"""
if __name__=='__main__':
    import os
    out=os.path.join(os.path.dirname(__file__),'..','assets','voice')
    for line in LIST.strip().splitlines():
        t,a,f=line.split()
        print(f,*make(t,int(a),os.path.join(out,f)))
