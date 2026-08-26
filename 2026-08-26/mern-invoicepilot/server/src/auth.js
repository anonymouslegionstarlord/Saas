import jwt from 'jsonwebtoken';
import { config } from './config.js';
import { User } from './models.js';

export function sign(user) { return jwt.sign({ sub: user.id, workspaceId: user.workspaceId.toString() }, config.jwtSecret, { expiresIn: '2h' }); }

export async function requireAuth(req, res, next) {
  try {
    const token = req.headers.authorization?.replace(/^Bearer\s+/i, '');
    const payload = jwt.verify(token, config.jwtSecret);
    const user = await User.findOne({ _id: payload.sub, workspaceId: payload.workspaceId }).select('-passwordHash');
    if (!user) return res.status(401).json({ error: 'Invalid session' });
    req.user = user;
    next();
  } catch { res.status(401).json({ error: 'Invalid or expired token' }); }
}

