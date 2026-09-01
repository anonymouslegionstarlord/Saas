import jwt from 'jsonwebtoken';
import { config } from './config.js';

export function signToken(user) {
  return jwt.sign({ sub: user._id.toString(), tenantId: user.tenantId.toString(), role: user.role }, config.jwtSecret, { expiresIn: config.jwtExpiresIn });
}

export function requireAuth(req, res, next) {
  const token = req.headers.authorization?.replace(/^Bearer\s+/i, '');
  if (!token) return res.status(401).json({ error: 'Authentication required' });
  try {
    const claims = jwt.verify(token, config.jwtSecret);
    req.auth = { userId: claims.sub, tenantId: claims.tenantId, role: claims.role };
    next();
  } catch { res.status(401).json({ error: 'Invalid or expired token' }); }
}

