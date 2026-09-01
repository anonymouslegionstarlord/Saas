import { Router } from 'express';
import bcrypt from 'bcryptjs';
import mongoose from 'mongoose';
import { User } from '../models.js';
import { loginSchema, registerSchema } from '../validation.js';
import { signToken } from '../auth.js';

export const authRouter = Router();

authRouter.post('/register', async (req, res, next) => {
  try {
    const data = registerSchema.parse(req.body);
    if (await User.exists({ email: data.email.toLowerCase() })) return res.status(409).json({ error: 'Email already registered' });
    const tenantId = new mongoose.Types.ObjectId();
    const user = await User.create({ tenantId, name: data.name, email: data.email, passwordHash: await bcrypt.hash(data.password, 12) });
    res.status(201).json({ token: signToken(user), user: { name: user.name, workspace: data.workspace } });
  } catch (error) { next(error); }
});

authRouter.post('/login', async (req, res, next) => {
  try {
    const data = loginSchema.parse(req.body);
    const user = await User.findOne({ email: data.email.toLowerCase() });
    if (!user || !await bcrypt.compare(data.password, user.passwordHash)) return res.status(401).json({ error: 'Invalid credentials' });
    res.json({ token: signToken(user), user: { name: user.name } });
  } catch (error) { next(error); }
});

