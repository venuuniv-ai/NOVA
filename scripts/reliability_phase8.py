"""Operator-run local load/outage probe. Never run against a hosted/shared deployment."""
import argparse
import json
import math
import os
import subprocess
import time
import urllib.request
from statistics import median
from uuid import uuid4


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks',type=int,default=20)
    parser.add_argument('--outage',action='store_true')
    args=parser.parse_args()
    assert 1<=args.tasks<=50
    token=os.environ['NOVA_TOKEN_A']
    latency=[]
    def call(path,payload=None):
        start=time.perf_counter()
        req=urllib.request.Request('http://localhost:8080/api/v1'+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=20) as response:result=json.load(response)
        latency.append((time.perf_counter()-start)*1000);return result
    devices={d['type']:d['id'] for d in call('/devices')}
    identities=[];started=time.perf_counter()
    for i in range(args.tasks):
        task=call('/tasks',{'title':'Phase 8 controlled load '+str(i),'origin_device_id':devices['DESKTOP']});tid=task['id'];identities.append(tid)
        for source,target in [('DESKTOP','WEARABLE'),('WEARABLE','MOBILE')]:
            result=call('/tasks/'+tid+'/handoff',{'source_device_id':devices[source],'target_device_id':devices[target],'idempotency_key':str(uuid4())})
            assert result['task']['id']==tid and result['task']['current_device_id']==devices[target]
    request_latencies=list(latency);request_elapsed=time.perf_counter()-started
    deadline=time.monotonic()+120
    for tid in identities:
        while time.monotonic()<deadline:
            evidence=call('/operations/tasks/'+tid)
            if all(e['state']=='PUBLISHED' and set(e['consumers'])=={'projection','proactive','audit'} for e in evidence['events']):break
            time.sleep(.2)
        else:raise AssertionError('Consumers did not catch up')
        assert len(call('/tasks/'+tid+'/events'))==3
    catchup_elapsed=time.perf_counter()-started
    recovery=None
    compose=['docker','compose','-f','compose.yaml','-f','compose.phase8.yaml']
    if args.outage:
        subprocess.run(compose+['stop','kafka'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            tid=call('/tasks',{'title':'Phase 8 broker outage persistence','origin_device_id':devices['DESKTOP']})['id']
            evidence=call('/operations/tasks/'+tid)
            assert any(e['state']=='PENDING' for e in evidence['events'])
            assert call('/tasks/'+tid)['id']==tid
            outage_task=tid
        finally:
            restart=time.perf_counter()
            subprocess.run(compose+['up','-d','--wait','kafka'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            evidence=call('/operations/tasks/'+tid)
            if all(e['state']=='PUBLISHED' and set(e['consumers'])=={'projection','proactive','audit'} for e in evidence['events']):break
            time.sleep(.3)
        else:raise AssertionError('Broker recovery did not drain pending outbox')
        recovery={'task_id':outage_task,'seconds_from_restart_command':round(time.perf_counter()-restart,3),'events':len(evidence['events']),'same_task_persisted':True}
    elapsed=sorted(request_latencies)
    print(json.dumps({'scope':'LOCAL FIXTURE CONTINUITY LOAD / NOT PRODUCTION BENCHMARK','tasks':args.tasks,'http_samples':len(elapsed),'request_p50_ms':round(median(elapsed),3),'request_p95_ms':round(elapsed[math.ceil(.95*len(elapsed))-1],3),'workflow_request_seconds':round(request_elapsed,3),'all_consumers_caught_up_seconds':round(catchup_elapsed,3),'task_ids_preserved':True,'events_per_task':3,'broker_outage_recovery':recovery,'external_api_spend_usd':0},indent=2))


if __name__=='__main__':main()
