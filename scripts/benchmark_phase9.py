"""Explicit HTTP benchmark; no model downloads/runtime startup. Outputs safe measurements only."""
import argparse
import json
import os
import platform
import time
import urllib.request
from uuid import uuid4


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url',default='http://localhost:8080')
    p.add_argument('--task',required=True)
    p.add_argument('--mode',choices=['FIXTURE','LOCAL_REAL'],default='LOCAL_REAL')
    p.add_argument('--samples',type=int,default=3)
    args=p.parse_args()
    if not 1<=args.samples<=10: p.error('samples must be 1..10')
    if args.mode=='LOCAL_REAL' and os.environ.get('REAL_MODEL_TESTS')!='1':
        print(json.dumps({'state':'BLOCKED','reason':'REAL_MODEL_TESTS=1 and approved configured model required'}));return
    results=[]
    for index in range(args.samples):
        started=time.perf_counter()
        body={'task_id':args.task,'mode':args.mode,'operation':'STRUCTURED','benchmark_label':'SHORT' if index==0 else 'STRUCTURED','query':'Controlled benchmark: summarize an empty schedule.','request_id':str(uuid4())}
        req=urllib.request.Request(args.base_url+'/api/v1/inference/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ.get('NOVA_TOKEN_A','')})
        with urllib.request.urlopen(req,timeout=30) as response: row=json.load(response)
        results.append({'sample':index,'wall_ms':(time.perf_counter()-started)*1000,'state':row['state'],'error':row.get('error'),'model':row.get('model'),'input_tokens':row.get('input_tokens'),'output_tokens':row.get('output_tokens')})
        if row['state']!='DONE':break
    print(json.dumps({'mode':args.mode,'hardware':platform.machine(),'os':platform.platform(),'samples':results,'concurrency':1,'warmup':0,'load_time':None,'time_to_first_token':None,'memory':None,'boundary':'HTTP WALL TIME; no cold-load/TTFT/throughput claim'},indent=2))


if __name__=='__main__':main()
