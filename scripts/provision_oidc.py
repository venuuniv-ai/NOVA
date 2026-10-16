"""Operator-only provisioning of a controlled local Keycloak account and NOVA subject grant."""
import json
import secrets
import subprocess
import urllib.parse
import urllib.request


def main():
    password=subprocess.check_output(['docker','compose','-f','compose.yaml','-f','compose.phase8.yaml','-f','compose.oidc.yaml','exec','-T','keycloak','cat','/opt/keycloak/data/operator.password'],text=True).strip()
    def request(path, payload=None, bearer=None, form=False, method=None):
        body=urllib.parse.urlencode(payload).encode() if form else json.dumps(payload).encode() if payload is not None else None
        headers={"Content-Type":"application/x-www-form-urlencoded" if form else "application/json"}
        if bearer:headers['Authorization']='Bearer '+bearer
        with urllib.request.urlopen(urllib.request.Request('http://localhost:8180'+path,data=body,headers=headers,method=method),timeout=10) as response:
            data=response.read();return json.loads(data) if data else None
    token=request('/realms/master/protocol/openid-connect/token',{'grant_type':'password','client_id':'admin-cli','username':'admin','password':password},form=True)['access_token']
    profile=request('/admin/realms/nova/users/profile',bearer=token)
    if not any(a.get('name')=='device_id' for a in profile['attributes']):
        profile['attributes'].append({'name':'device_id','displayName':'Simulated device context','permissions':{'view':['admin','user'],'edit':['admin']},'multivalued':False,'validations':{'length':{'min':36,'max':36}}})
        request('/admin/realms/nova/users/profile',profile,token,method='PUT')
    username='nova-local-fixture'
    users=request('/admin/realms/nova/users?username='+username,bearer=token)
    fixture_password=secrets.token_urlsafe(32)
    if not users:
        request('/admin/realms/nova/users',{'username':username,'enabled':True,'firstName':'Local','lastName':'Fixture','email':'fixture@localhost.invalid','emailVerified':True,'attributes':{'device_id':['00000000-0000-4000-8000-000000000010']}},token)
        users=request('/admin/realms/nova/users?username='+username,bearer=token)
    subject=users[0]['id']
    request('/admin/realms/nova/users/'+subject,{**users[0],'attributes':{'device_id':['00000000-0000-4000-8000-000000000010']}},token,method='PUT')
    request('/admin/realms/nova/users/'+subject+'/reset-password',{'type':'password','temporary':False,'value':fixture_password},token,method='PUT')
    subprocess.run(['docker','compose','exec','-T','backend','python','-m','app.security.cli','provision','--issuer','http://localhost:8180/realms/nova','--subject',subject,'--user-id','00000000-0000-4000-8000-000000000001','--output','/app/security/oidc-grant'],check=True)
    # Private runtime test credential, not stdout/repository or browser localStorage.
    from pathlib import Path
    directory=Path('.secrets');directory.mkdir(mode=0o700,exist_ok=True)
    target=directory/'oidc-fixture.password';target.write_text(fixture_password);target.chmod(0o600)
    print('Controlled local OIDC account provisioned; private credential stored in ignored .secrets.')


if __name__=='__main__':main()
