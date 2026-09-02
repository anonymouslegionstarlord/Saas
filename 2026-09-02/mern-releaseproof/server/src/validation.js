import {z} from 'zod';
export const registerSchema=z.object({name:z.string().trim().min(2).max(80),workspace:z.string().trim().min(2).max(80),email:z.email(),password:z.string().min(8).max(128)});
export const loginSchema=z.object({email:z.email(),password:z.string().min(1)});
export const releaseSchema=z.object({name:z.string().trim().min(2).max(120),version:z.string().trim().min(1).max(40),targetDate:z.coerce.date(),owner:z.string().trim().min(2).max(80)});
export const checkSchema=z.object({title:z.string().trim().min(2).max(180),area:z.enum(['functional','regression','security','performance','deployment']),priority:z.enum(['low','medium','high','critical'])});
export const resultSchema=z.object({result:z.enum(['not_run','passed','failed','blocked']),evidence:z.string().trim().max(1000).default('')});
export function readiness(checks){if(!checks.length)return {score:0,ready:false};const passed=checks.filter(x=>x.result==='passed').length;const blockers=checks.filter(x=>x.result==='failed'&&['high','critical'].includes(x.priority)).length;return {score:Math.round(passed/checks.length*100),ready:passed===checks.length&&blockers===0};}

