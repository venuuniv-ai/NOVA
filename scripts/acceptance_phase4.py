"""Local Phase 4 routing, cache, budgets, and persistence acceptance without model downloads."""
import argparse
import json
import urllib.request
from uuid import uuid4


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',default='http://localhost:8000')
    parser.add_argument('--verify-task')
    args=parser.parse_args()
    def call(path,payload=None):
        req=urllib.request.Request(args.base_url+path,data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Content-Type':'application/json','X-Correlation-ID':str(uuid4())})
        with urllib.request.urlopen(req,timeout=25) as response:
            assert response.headers['X-Correlation-ID']
            return json.load(response)
    providers=call('/api/v1/model-router/providers')
    assert providers['local_runtime']=='LOCAL RUNTIME NOT CONFIGURED'
    budget=call('/api/v1/model-router/budget'); assert budget['paid_providers_enabled'] is False
    if args.verify_task:
        task_id=args.verify_task
    else:
        devices={d['type']:d['id'] for d in call('/api/v1/devices')}
        task=call('/api/v1/tasks',{'title':'Phase 4 model routing acceptance','origin_device_id':devices['DESKTOP']})
        task_id=task['id']
        for scenario in ['SIMPLE','SIMPLE','REASONING','PRIVACY','BUDGET','FAILURE']:
            result=call('/api/v1/model-router/evaluate',{'task_id':task_id,'request_id':str(uuid4()),'scenario':scenario})
            assert result['status']=='DONE' and result['provider']=='fixture'
            assert result['estimated_cost_usd'] in [0,'0']
            assert result['total_tokens'] is None
            if scenario=='PRIVACY': assert result['cache_status']=='BYPASS'
            if scenario=='BUDGET': assert 'BUDGET_DOWNGRADE' in result['decision']['reason_codes']
            if scenario=='FAILURE': assert 'FALLBACK_USED' in result['decision']['reason_codes']
    if not args.verify_task:
        draft=call('/api/v1/proactive/evaluate-routed',{'task_id':task_id,'idempotency_key':str(uuid4())})
        assert draft['status']=='SURFACED' and draft['proposal']['status']=='PENDING_APPROVAL'
        assert draft['proposal']['policy_decision']=='REQUIRE_APPROVAL'
    proposals=call(f'/api/v1/tasks/{task_id}/proposals')
    assert len(proposals)==1 and proposals[0]['status']=='PENDING_APPROVAL'
    detail=call(f"/api/v1/proposals/{proposals[0]['id']}")
    assert detail['approval'] is None and detail['execution'] is None
    history=call(f'/api/v1/tasks/{task_id}/model-calls')
    assert len(history)==7 and all(c['status']=='DONE' for c in history)
    assert all(c['response']['output'] is None for c in history)
    ordered=list(reversed(history))
    assert ordered[0]['response']['cache_status']=='MISS'
    assert ordered[1]['response']['cache_status']=='HIT'
    assert ordered[1]['attempts'][0]['invoked'] is False
    assert 'REASONING_REPLAY_LIMITATION' in ordered[2]['decision']['reason_codes']
    assert ordered[3]['decision']['privacy_class']=='SENSITIVE_LOCAL_ONLY'
    assert ordered[4]['response']['mode']=='POLICY_REPLAY'
    assert not any(a['provider']=='test-priced-probe' and a['invoked'] for a in ordered[4]['attempts'])
    assert ordered[5]['attempts'][0]['error']=='UNAVAILABLE'
    assert ordered[6]['purpose']=='COMMUNICATION' and ordered[6]['trace_id']==proposals[0]['trace_id']
    budget=call('/api/v1/model-router/budget')
    assert float(budget['consumed_usd'])==float(budget['reserved_usd'])==0
    print(json.dumps({'result':'PASS','task_id':task_id,'model_requests':len(history),'proposal_id':proposals[0]['id'],'proposal_status':'PENDING_APPROVAL',
        'request_ids':[c['request_id'] for c in ordered],'trace_ids':[c['trace_id'] for c in ordered],
        'cache':'MISS → HIT; no extra provider invocation','priced_provider_invocations':0,
        'local_runtime':providers['local_runtime'],'required_external_api_spend_usd':0,
        'restart_verification':bool(args.verify_task)},indent=2))


if __name__=='__main__': main()
