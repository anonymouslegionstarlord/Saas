import jwt from 'jsonwebtoken';
import { config } from './config.js';

export function tokenFor(user) { return jwt.sign({ sub: user._id.toString(), tenantId: user.tenantId.toString() }, config.jwtSecret, { expiresIn: '8h' }); }
export function requireAuth(req, res, next) {
  const value = req.headers.authorization || '';
  if (!value.startsWith('Bearer ')) return res.status(401).json({ error: 'Missing bearer token' });
  try { req.auth = jwt.verify(value.slice(7), config.jwtSecret); next(); }
  catch { res.status(401).json({ error: 'Invalid or expired token' }); }
}

