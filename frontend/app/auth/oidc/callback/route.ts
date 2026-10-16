import {timingSafeEqual} from "node:crypto";
import {NextRequest,NextResponse} from "next/server";
export async function GET(request:NextRequest){
 const failed=()=>{const result=NextResponse.json({error:"OIDC authentication refused"},{status:401});result.cookies.set("nova_oidc_intent","",{httpOnly:true,sameSite:"lax",maxAge:0,path:"/auth/oidc"});return result;};
 try{
 const intent=JSON.parse(request.cookies.get("nova_oidc_intent")?.value??"{}");const state=request.nextUrl.searchParams.get("state")??"",code=request.nextUrl.searchParams.get("code")??"";
 if(typeof intent.state!=="string"||typeof intent.verifier!=="string"||state.length!==intent.state.length||!timingSafeEqual(Buffer.from(state),Buffer.from(intent.state))||!code||code.length>4096)return failed();
 const issuer=process.env.OIDC_INTERNAL_ISSUER;if(!issuer)return failed();
 const exchange=await fetch(`${issuer}/protocol/openid-connect/token`,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:new URLSearchParams({grant_type:"authorization_code",client_id:"nova-web",redirect_uri:process.env.OIDC_REDIRECT_URI??"http://localhost:3000/auth/oidc/callback",code,code_verifier:intent.verifier}),redirect:"error",signal:AbortSignal.timeout(5000),cache:"no-store"});
 if(!exchange.ok)return failed();const payload=await exchange.json();const token=payload.access_token;if(typeof token!=="string"||token.length>11000)return failed();
 const verified=await fetch(`${process.env.API_INTERNAL_URL??"http://localhost:8000"}/api/v1/auth/me`,{headers:{Authorization:`Bearer ${token}`},redirect:"error",signal:AbortSignal.timeout(3000),cache:"no-store"});if(!verified.ok||(await verified.json()).mode!=="oidc")return failed();
 const result=NextResponse.redirect(new URL("/",process.env.NOVA_PUBLIC_ORIGIN??"http://localhost:3000"));result.cookies.set("nova_session",token,{httpOnly:true,sameSite:"strict",secure:request.nextUrl.protocol==="https:",maxAge:Math.min(Number(payload.expires_in)||300,3600),path:"/"});result.cookies.set("nova_oidc_intent","",{httpOnly:true,sameSite:"lax",maxAge:0,path:"/auth/oidc"});return result;
 }catch{return failed();}
}
