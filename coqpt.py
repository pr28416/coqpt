"""
In terminal, start server by running:
```
python3 -m uvicorn coqpt:app --reload;
```
"""

from random import random
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")


class CoqCode(BaseModel):
    v: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


errorResponses = [
    "You didn't import Hammer correctly. The correct way to do this is: From Hammer Require Import Hammer."
]
errorMap = {
    "The reference sauto was not found in the current environment": [0],
    "Cannot find a physical path bound to logical path CoqHammer.Hammer.": [0],
    "Cannot find a physical path bound to logical path Hammer.Hammer": [0]
}

failedCode = set()


@app.post("/verify/")
async def verify(v: str):
    print(v)
    try:
        r = requests.post("https://coq.livecode.ch/check", data={'v': v})
        r.raise_for_status
        j = r.json()
        if j['status'] == 0:
            return {"status": "ok"}
        elif j['log']:

            res = re.search(r"line (\d+), characters (\d+)-(\d+)", j['log'])
            if res:
                lineNum, charStart, charEnd = map(int, res.groups())
                lines = v.split("\n")
                entireLine = lines[lineNum-1]
                subLine = entireLine[charStart:charEnd]
                j['log'] = j['log'][:res.start()] + j['log'][res.start():res.end()] + f' [statement `{subLine}` from line `{entireLine}`]' + j['log'][res.end():]

            # Get rid of repeated results
            if j['log'] in failedCode:
                return {"error": "Stop submitting the same error-filled code. Start the proof from scratch. It's all wrong."}
            
            failedCode.add(j['log'])

            possibleErrors = set()

            trigger = False
            for error in errorMap:
                if error in j['log']:
                    for k in errorMap[error]:
                        possibleErrors.add(k)
                        trigger = True
            
            if trigger:
                return {"error": " ".join(map(lambda i: errorResponses[i], possibleErrors))}

            if "sauto" in v:
                return {"error": j['log'] + " There is likely a way to fix the code by replacing parts of your casework with sauto, or by replacing casework entirely with hammer."}        
            
            return {"error": j['log']}
        elif j['out']:
            return {"recommendation": j['output']}
    except Exception as e:
        if "sauto" in v:
            return {"error": str(e) + " There is likely a way to fix the code by using hammer rather than sauto."}
        return {"error": e}


@app.get("/learnhammer/")
async def learnhammer():
    with open("coqhammer.txt") as f:
        return {"about": f.readlines()}
