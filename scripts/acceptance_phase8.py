"""Authenticated local gateway/Kafka/HITL acceptance. Tokens are operator inputs, never report data."""
import argparse
import json
import os
import time
import urllib.error
import urllib.request
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--verify-task")
    parser.add_argument("--inject-duplicates",action="store_true")
    args = parser.parse_args()
    token = os.environ["NOVA_TOKEN_A"]
    other = os.environ["NOVA_TOKEN_B"]
    def call(path, data=None, credential=token, expected=200):
        req=urllib.request.Request(args.base_url+"/api/v1"+path,data=json.dumps(data).encode() if data is not None else None,headers={"Content-Type":"application/json",**({"Authorization":"Bearer "+credential} if credential else {})})
        try:
            with urllib.request.urlopen(req,timeout=20) as response:
                assert response.status==expected,(path,response.status,expected)
                return json.load(response)
        except urllib.error.HTTPError as error:
            assert error.code==expected,(path,error.code,expected)
            raw = error.read()
            return json.loads(raw) if raw else {}
    call("/tasks",credential="",expected=401)
    identity=call("/auth/me"); assert identity["mode"]=="local"
    devices={d["type"]:d["id"] for d in call("/devices")}
    if args.verify_task:
        tid=args.verify_task
    else:
        task=call("/tasks",{"title":"Phase 8 controlled event continuity acceptance","origin_device_id":devices["DESKTOP"]},expected=201)
        tid=task["id"]
        call("/operations/tasks/"+tid+"/subscribe",{})
        move={"source_device_id":devices["DESKTOP"],"target_device_id":devices["WEARABLE"],"idempotency_key":str(uuid4())}
        call("/tasks/"+tid+"/handoff",move)
        assert call("/tasks/"+tid+"/handoff",move)["replayed"]
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            operations=call("/operations/tasks/"+tid)
            if operations["jobs"] and all(j["state"]=="DONE" for j in operations["jobs"]):break
            time.sleep(.3)
        else:raise AssertionError("Kafka proactive draft did not complete")
        proposals=call("/tasks/"+tid+"/proposals")
        assert len(proposals)==1 and proposals[0]["status"]=="PENDING_APPROVAL"
        pid=proposals[0]["id"]
        detail=call("/proposals/"+pid);assert detail["approval"] is None and detail["execution"] is None
        call("/proposals/"+pid+"/execute",{"idempotency_key":str(uuid4())},expected=409)
        call("/proposals/"+pid+"/approve",{"idempotency_key":str(uuid4())})
        execution=call("/proposals/"+pid+"/execute",{"idempotency_key":str(uuid4())})
        assert execution["execution"]["receipt"]["external_message_sent"] is False
        call("/tasks/"+tid+"/handoff",{"source_device_id":devices["WEARABLE"],"target_device_id":devices["MOBILE"],"idempotency_key":str(uuid4())})
    call("/tasks/"+tid,credential=other,expected=404)
    task=call("/tasks/"+tid);assert task["id"]==tid and task["current_device_id"]==devices["MOBILE"]
    proposals=call("/tasks/"+tid+"/proposals");assert len(proposals)==1
    detail=call("/proposals/"+proposals[0]["id"])
    assert detail["approval"]["payload_hash"]==detail["proposal"]["payload_hash"]
    assert detail["execution"]["receipt"]["external_message_sent"] is False
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        operations=call("/operations/tasks/"+tid)
        if all(e["state"]=="PUBLISHED" and set(e["consumers"])=={"projection","proactive","audit"} for e in operations["events"]):break
        time.sleep(.3)
    else:raise AssertionError("Outbox or consumers failed to catch up")
    assert len(operations["jobs"])==1 and operations["jobs"][0]["state"]=="DONE"
    transport_probe="NOT_RUN"
    if args.inject_duplicates:
        import subprocess
        code="""
import sys,json,hashlib,time
from sqlalchemy import select,func
from kafka import KafkaProducer
from app.database import SessionLocal
from app.events.models import Outbox,DeadLetter
from app.events.pipeline import TOPIC,envelope
from uuid import UUID
with SessionLocal() as session:
 row=next(e for e in session.scalars(select(Outbox).where(Outbox.task_id==UUID(sys.argv[1]))) if e.payload.get('transition')=='HANDOFF_DESKTOP_TO_WEARABLE')
 data=envelope(row)
producer=KafkaProducer(bootstrap_servers='kafka:9092',acks='all')
key=sys.argv[1].encode()
for i in range(3):producer.send(TOPIC,key=key,value=json.dumps(data).encode()).get(timeout=10)
data['payload']['approval']=True
raw=json.dumps(data).encode();fingerprint=hashlib.sha256(raw).hexdigest()
producer.send(TOPIC,key=key,value=raw).get(timeout=10);producer.close()
deadline=time.monotonic()+30
while time.monotonic()<deadline:
 with SessionLocal() as session:
  count=session.scalar(select(func.count()).select_from(DeadLetter).where(DeadLetter.fingerprint==fingerprint))
 if count==3:break
 time.sleep(.2)
else:raise AssertionError('All consumer groups must reject the forged message')
"""
        subprocess.run(['docker','compose','exec','-T','backend','python','-c',code,tid],check=True)
        final=call("/operations/tasks/"+tid)
        assert len(final["jobs"])==1
        assert call("/proposals/"+proposals[0]["id"])["execution"]["id"]==detail["execution"]["id"]
        transport_probe="PASS / 3 DUPLICATES + FORGED APPROVAL / 3 DEAD LETTERS"
    print(json.dumps({"result":"PASS","task_id":tid,"same_task_id":True,"device":"MOBILE","outbox_events":len(operations["events"]),"consumer_groups":3,"proactive_jobs":1,"proposal_id":proposals[0]["id"],"approval_hash_bound":True,"execution":"SIMULATED / NOT SENT","auth":"LOCAL JWT / OWNED","restart_verification":bool(args.verify_task),"transport_probe":transport_probe},indent=2))


if __name__=="__main__":main()
