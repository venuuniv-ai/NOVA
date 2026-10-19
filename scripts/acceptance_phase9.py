"""Authenticated fixture inference acceptance; no inference runtime or download commands."""
import argparse
import json
import os
import time
import urllib.request
from uuid import uuid4


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://localhost:8080')
    parser.add_argument('--verify-run')
    args=parser.parse_args()
    def call(path,data=None):
        req=urllib.request.Request(args.base_url+'/api/v1'+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json','Authorization':'Bearer '+os.environ['NOVA_TOKEN_A']})
        with urllib.request.urlopen(req,timeout=60) as response:return json.load(response)
    assert call('/auth/me')['mode']=='local'
    if args.verify_run:
        row=call('/inference/runs/'+args.verify_run)
        assert row['state']=='DONE' and row['simulation']
        print(json.dumps({'result':'PASS','restart_run':args.verify_run,'real_inference':'NOT_EXECUTED'}));return
    devices={d['type']:d['id'] for d in call('/devices')}
    # Stable fixture content, no real personal information.
    task=call('/tasks',{'title':'Phase 9 controlled grounding acceptance','origin_device_id':devices['DESKTOP']})
    call('/operations/tasks/'+task['id']+'/subscribe',{})
    payload={'task_id':task['id'],'mode':'FIXTURE','operation':'RAG','query':'Italian','request_id':str(uuid4())}
    run=call('/inference/generate',payload);assert run['state']=='DONE' and run['simulation'],run
    assert all(c['evidence_id'] in run['citation_ids'] for c in run['output']['claims'])
    assert call('/inference/generate',payload)['replayed']
    blocked=call('/inference/generate',{**payload,'request_id':str(uuid4()),'mode':'LOCAL_REAL'})
    assert blocked['state']=='FAILED' and blocked['output'] is None
    disabled=call('/inference/generate',{**payload,'request_id':str(uuid4()),'mode':'DISABLED'})
    assert disabled['error']=='INFERENCE_DISABLED'
    agents=call('/inference/agents',{'task_id':task['id'],'mode':'FIXTURE','request_id':str(uuid4())})
    assert agents['execution']['status']=='DONE'
    job=call('/inference/reindex',{'task_id':task['id']})
    while job['state']=='READY':job=call('/inference/reindex/'+job['id']+'/step',{})
    assert job['state']=='DONE'
    proposal_id=None
    for source,target in [('DESKTOP','WEARABLE'),('WEARABLE','MOBILE')]:
        call('/tasks/'+task['id']+'/handoff',{'source_device_id':devices[source],'target_device_id':devices[target],'idempotency_key':str(uuid4())})
        if target=='WEARABLE':
            deadline=time.monotonic()+60
            while time.monotonic()<deadline:
                proposals=call('/tasks/'+task['id']+'/proposals')
                if proposals:break
                time.sleep(.2)
            else:raise AssertionError('No fixture draft prepared')
            proposal_id=proposals[0]['id']
            before=call('/proposals/'+proposal_id)
            assert before['approval'] is None and before['execution'] is None
            call('/proposals/'+proposal_id+'/approve',{'idempotency_key':str(uuid4())})
            executed=call('/proposals/'+proposal_id+'/execute',{'idempotency_key':str(uuid4())})
            assert executed['approval']['payload_hash']==executed['proposal']['payload_hash']
            assert executed['execution']['receipt']['external_message_sent'] is False
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        events=call('/operations/tasks/'+task['id'])['events']
        if all(e['state']=='PUBLISHED' and len(e['consumers'])==3 for e in events):break
        time.sleep(.2)
    else:raise AssertionError('Event delivery incomplete')
    assert call('/tasks/'+task['id'])['id']==task['id']
    print(json.dumps({'result':'PASS','run_id':run['id'],'task_id':task['id'],'reindex':job,'proposal_id':proposal_id,'agent_status':agents['execution']['status'],'kafka_events':len(events),'payload_bound_approval':True,'external_message_sent':False,'trace_id':run['trace_id'],'real_inference':'NOT_EXECUTED','real_judge':'NOT_CONFIGURED','scope':'EXTRACTIVE FIXTURE GROUNDING; phase8 acceptance separately covers approval/Kafka'},indent=2))


if __name__=='__main__':main()
