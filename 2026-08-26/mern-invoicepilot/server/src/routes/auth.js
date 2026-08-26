import { Router } from 'express';
import bcrypt from 'bcryptjs';
import { User, Workspace } from '../models.js';
import { requireAuth, sign } from '../auth.js';
import { requiredStrings, validEmail } from '../validation.js';

export const authRouter = Router();
authRouter.post('/register', async (req, res, next) => {
  const missing = requiredStrings(req.body, ['workspace','name','email','password']);
  if (missing.length || !validEmail(req.body.email) || req.body.password.length < 8) return res.status(422).json({ error: 'Workspace, name, valid email, and password of 8+ characters are required' });
  try {
    if (await User.exists({ email: req.body.email.toLowerCase() })) return res.status(409).json({ error: 'Email is already registered' });
    const workspace = await Workspace.create({ name: req.body.workspace });
    try {
      const user = await User.create({ workspaceId: workspace.id, name: req.body.name, email: req.body.email, passwordHash: await bcrypt.hash(req.body.password, 12) });
      res.status(201).json({ token: sign(user), user: { id: user.id, name: user.name, email: user.email, workspaceId: workspace.id, workspace: workspace.name } });
    } catch (error) { await Workspace.deleteOne({ _id: workspace.id }); throw error; }
  } catch (error) { if (error.code === 11000) return res.status(409).json({ error: 'Email is already registered' }); next(error); }
});
authRouter.post('/login', async (req, res) => {
  const user = await User.findOne({ email: String(req.body.email || '').toLowerCase() }).populate('workspaceId');
  if (!user || !await bcrypt.compare(req.body.password || '', user.passwordHash)) return res.status(401).json({ error: 'Invalid email or password' });
  res.json({ token: sign(user), user: { id: user.id, name: user.name, email: user.email, workspaceId: user.workspaceId.id, workspace: user.workspaceId.name } });
});
authRouter.get('/me', requireAuth, (req, res) => res.json(req.user));
