import {randomBytes,createHash} from "node:crypto";
import {NextRequest,NextResponse} from "next/server";
export async function GET(request:NextRequest){
 const issuer=process.env.OIDC_PUBLIC_ISSUER; if(!issuer)return NextResponse.json({error:"OIDC provider not configured"},{status:503});
 const state=randomBytes(32).toString("base64url"),verifier=randomBytes(48).toString("base64url");
 const redirect=process.env.OIDC_REDIRECT_URI??"http://localhost:3000/auth/oidc/callback";
 const url=new URL(`${issuer}/protocol/openid-connect/auth`);url.search=new URLSearchParams({client_id:"nova-web",response_type:"code",scope:"openid",redirect_uri:redirect,state,code_challenge:createHash("sha256").update(verifier).digest("base64url"),code_challenge_method:"S256"}).toString();
 const result=NextResponse.redirect(url);result.cookies.set("nova_oidc_intent",JSON.stringify({state,verifier}),{httpOnly:true,sameSite:"lax",secure:request.nextUrl.protocol==="https:",maxAge:300,path:"/auth/oidc"});return result;
}
