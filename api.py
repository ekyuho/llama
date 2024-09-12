import time
from threading import Timer, Thread
from flask import Flask, request, jsonify, redirect
from langchain_ollama import OllamaLLM
from datetime import datetime

#MODEL='llama3.1'
MODEL='phi3'
llm = OllamaLLM(model=MODEL)
import time
import random

h=f'<a href=/chat>다시시작</a> <p>'
app = Flask(__name__)
Prompt={}
Retry={}
Output={}
History=[]
Elapsed={}

def run(text, key):
    global Output
    Output[key]=llm.invoke(text)


@app.route('/chat', methods=['GET','POST'])
def _chat():
    global Output, Retry, Prompt, History
    if not request.form.get('chat'):
        s=f'''{h}
            <H3>효돌 챗봇</H3>
            Ubuntu 8G Memory (no GPU)에서 실행되는 llama3.1 모델 테스트 드라이브입니다.<br>
            채팅기록을 같이 보여줍니다.
            <br>
            Using {MODEL}
            <form action=/chat method=POST enctype="multipart/form-data">
                <textArea cols=60 rows=5 name=chat> 갑자기 아랫배가 오른쪽이 쑥쑥 쑤시며 아픈데 병원에 가야할까?
                </textArea>
                <input type="submit" value="제출"></form>
        '''
        s+='<pre>'
        for x in History:
            s+=f'''<br><b>{x['time']} 소요시간={x['elapsed']} {x['prompt']}<br>{x['answer']}</b><br>'''
        s+='</pre>'
        return s

    text=request.form.get('chat')
    key = f'{random.randrange(1,1000000,1)}'
    Output[key]=''
    Retry[key]=600
    Prompt[key]=text
    Elapsed[key]=time.time()
    Thread(target=run, args=(text,key), daemon=True).start()
    return redirect(f"/screen?key={key}", code=302)

@app.route('/screen')
def screen():
    global Output, Retry, Prompt, History
    key=request.args.get('key','')
    if not key: return 'no key, check key=xxx'
    if key not in Output: return 'nothing is being done, seq error maybe'

    if Output[key]:
        History.append({'time':datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'prompt':Prompt[key],'answer':Output[key],'elapsed':f'{time.time()-Elapsed[key]:.1f}'})
        r=f'''{h}
        <H3>실행완료</H3>
        elapsed= {600-Retry[key]}초
        <pre>
        \n{Output[key]}
        '''
        del Retry[key]
        del Output[key]
        del Prompt[key]
        del Elapsed[key]
        return r

    if Retry[key]>0:
        elapsed= 600-Retry[key]
        r=f'''<head> <meta http-equiv=refresh content=5> </head>
        {h}
        <H3>출력을 기다리고 있습니다</H3>
        몇분 이상 걸릴 수 있습니다. 5초에 한번씩 체크합니다. 3분이상 걸리기도 합니다만... <br>
        이건 최종산출이 아니라, 1초이내의 응답으로 가는 중간 과정일 뿐입니다.<p>
        elapsed= {elapsed}초
        '''
        Retry[key] -= 5
    else:
        r=f"failed... {Retry[key]}"
        r+=f'<p>{h}'
        del Retry[key]
        del Output[key]
        del Prompt[key]
        del Elapsed[key]

    return r

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000)
