import{z}from'zod';
export const registerSchema=z.object({name:z.string().trim().min(2).max(80),workspace:z.string().trim().min(2).max(80),email:z.email(),password:z.string().min(8).max(128)});
export const loginSchema=z.object({email:z.email(),password:z.string().min(1)});
export const warrantySchema=z.object({customerName:z.string().trim().min(2).max(100),customerEmail:z.email(),product:z.string().trim().min(2).max(140),serialNumber:z.string().trim().min(2).max(100),purchasedOn:z.coerce.date(),expiresOn:z.coerce.date()}).refine(x=>x.expiresOn>x.purchasedOn,{message:'expiry must be after purchase',path:['expiresOn']});
export const claimSchema=z.object({issue:z.string().trim().min(5).max(1000),priority:z.enum(['low','normal','high','urgent'])});
export const claimUpdateSchema=z.object({status:z.enum(['submitted','approved','repairing','resolved','rejected']),resolution:z.string().trim().max(1000).default('')});
export function coverage(warranty,on=new Date()){return warranty.status==='active'&&new Date(warranty.expiresOn)>=on}

