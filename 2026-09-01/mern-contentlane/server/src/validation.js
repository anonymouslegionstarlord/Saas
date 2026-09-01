import { z } from 'zod';

export const registerSchema = z.object({ name: z.string().trim().min(2).max(80), workspace: z.string().trim().min(2).max(80), email: z.email(), password: z.string().min(8).max(128) });
export const loginSchema = z.object({ email: z.email(), password: z.string().min(1) });
export const itemSchema = z.object({
  title: z.string().trim().min(2).max(140), channel: z.enum(['blog', 'email', 'social', 'video']),
  owner: z.string().trim().min(2).max(80), dueDate: z.coerce.date(), brief: z.string().trim().max(2000).default('')
});
export const transitionSchema = z.object({ status: z.enum(['idea', 'draft', 'review', 'approved', 'published']), reviewerNote: z.string().trim().max(1000).default('') });

export const allowedTransition = (from, to) => {
  const order = ['idea', 'draft', 'review', 'approved', 'published'];
  const a = order.indexOf(from), b = order.indexOf(to);
  return b === a + 1 || (from === 'review' && to === 'draft');
};

