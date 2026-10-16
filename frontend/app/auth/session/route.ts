import {NextRequest,NextResponse} from "next/server";
export async function POST(request:NextRequest){
 if(request.headers.get("Origin")!==(process.env.NOVA_PUBLIC_ORIGIN??"http://localhost:3000"))return NextResponse.json({error:"Origin required"},{status:403});
 if(Number(request.headers.get("content-length")??0)>12000)return NextResponse.json({error:"Token too large"},{status:413});
 const reader=request.body?.getReader();let raw="";let size=0;const decoder=new TextDecoder();
 if(reader)while(true){const chunk=await reader.read();if(chunk.done)break;size+=chunk.value.length;if(size>12000){await reader.cancel();return NextResponse.json({error:"Token too large"},{status:413});}raw+=decoder.decode(chunk.value,{stream:true});}raw+=decoder.decode();
 let token:string;try{token=JSON.parse(raw).token;if(typeof token!=="string"||token.length>11000)throw Error();}catch{return NextResponse.json({error:"Invalid token"},{status:422});}
 try{const response=await fetch(`${process.env.API_INTERNAL_URL??"http://localhost:8000"}/api/v1/auth/me`,{headers:{Authorization:`Bearer ${token}`},cache:"no-store",signal:AbortSignal.timeout(3000)});
 if(!response.ok)return NextResponse.json({error:"Authentication refused"},{status:401});
 const identity=await response.json();if(identity.mode==="demo")return NextResponse.json({error:"Local replay mode needs no session. Enable local or OIDC authentication first."},{status:409});
 const result=NextResponse.json({authenticated:true});result.cookies.set("nova_session",token,{httpOnly:true,sameSite:"strict",secure:request.nextUrl.protocol==="https:",maxAge:3600,path:"/"});return result;
 }catch{return NextResponse.json({error:"Authentication unavailable"},{status:503});}
}
export async function DELETE(request:NextRequest){if(request.headers.get("Origin")!==(process.env.NOVA_PUBLIC_ORIGIN??"http://localhost:3000"))return NextResponse.json({error:"Origin required"},{status:403});const result=NextResponse.json({authenticated:false});result.cookies.delete("nova_session");return result;}
