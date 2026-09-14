import {z} from 'zod';
export const registerSchema=z.object({organization:z.string().trim().min(2).max(80),email:z.email(),password:z.string().min(8).max(128)});
export const loginSchema=z.object({email:z.email(),password:z.string().min(1)});
export const eventSchema=z.object({name:z.string().trim().min(2).max(120),venue:z.string().trim().min(2).max(180),startsAt:z.coerce.date(),capacity:z.coerce.number().int().min(1).max(100000),status:z.enum(['draft','open','closed']).default('draft')});
export const attendeeSchema=z.object({eventId:z.string().regex(/^[a-f\d]{24}$/i),name:z.string().trim().min(2).max(100),email:z.email(),ticketType:z.enum(['general','vip','staff']).default('general')});
export function eventMetrics(event,attendees){const total=attendees.length,checkedIn=attendees.filter(x=>x.checkedInAt).length;return{registered:total,checkedIn,remaining:Math.max(0,event.capacity-total),capacity:event.capacity,fillPercent:event.capacity?Math.round(total/event.capacity*100):0,checkInPercent:total?Math.round(checkedIn/total*100):0};}

