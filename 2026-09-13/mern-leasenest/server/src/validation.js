import { z } from 'zod';

export const registerSchema = z.object({ organization: z.string().trim().min(2).max(80), email: z.email(), password: z.string().min(8).max(128) });
export const loginSchema = z.object({ email: z.email(), password: z.string().min(1) });
export const propertySchema = z.object({ name: z.string().trim().min(2).max(100), address: z.string().trim().min(5).max(200), units: z.coerce.number().int().min(1).max(10000) });
export const leaseSchema = z.object({ propertyId: z.string().regex(/^[a-f\d]{24}$/i), unitLabel: z.string().trim().min(1).max(30), residentName: z.string().trim().min(2).max(100), residentEmail: z.email(), monthlyRentCents: z.coerce.number().int().positive().max(100000000), depositCents: z.coerce.number().int().nonnegative().max(100000000).default(0), startDate: z.coerce.date(), endDate: z.coerce.date(), status: z.enum(['draft', 'active', 'ended']).default('draft') }).refine(x => x.endDate > x.startDate, { message: 'End date must be after start date', path: ['endDate'] });

export function occupancyMetrics(properties, leases, now = new Date()) {
  const active = leases.filter(x => x.status === 'active');
  const totalUnits = properties.reduce((sum, x) => sum + Number(x.units), 0);
  const expiringSoon = active.filter(x => { const end = new Date(x.endDate); return end >= now && end <= new Date(now.getTime() + 30 * 86400000); }).length;
  return { properties: properties.length, totalUnits, occupiedUnits: active.length, occupancyPercent: totalUnits ? Math.round(active.length / totalUnits * 100) : 0, monthlyRentCents: active.reduce((sum, x) => sum + Number(x.monthlyRentCents), 0), expiringSoon };
}

