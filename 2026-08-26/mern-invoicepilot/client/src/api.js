const base=import.meta.env.VITE_API_URL||'http://localhost:4000/api';
export async function api(path,options={}){const response=await fetch(base+path,{...options,headers:{'Content-Type':'application/json',...(localStorage.getItem('invoicepilot_token')?{Authorization:`Bearer ${localStorage.getItem('invoicepilot_token')}`}:{})}});if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.error||'Request failed')}return response.status===204?null:response.json()}

