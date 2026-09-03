import{z}from'zod';
export const registerSchema=z.object({name:z.string().trim().min(2).max(80),workspace:z.string().trim().min(2).max(80),email:z.email(),password:z.string().min(8).max(128)});
export const loginSchema=z.object({email:z.email(),password:z.string().min(1)});
export const clientSchema=z.object({company:z.string().trim().min(2).max(120),contactName:z.string().trim().min(2).max(100),contactEmail:z.email(),owner:z.string().trim().min(2).max(80),targetDate:z.coerce.date()});
export const taskSchema=z.object({title:z.string().trim().min(2).max(180),category:z.enum(['discovery','data','access','training','launch']),dueDate:z.coerce.date(),assignee:z.string().trim().min(2).max(80)});
export const statusSchema=z.object({status:z.enum(['todo','doing','blocked','done']),note:z.string().trim().max(1000).default('')});
export function progress(tasks){if(!tasks.length)return 0;return Math.round(tasks.filter(x=>x.status==='done').length/tasks.length*100)}

