import express from 'express';
import cors from 'cors';
import { ZodError } from 'zod';
import { config } from './config.js';
import { requireAuth } from './auth.js';
import { authRouter } from './routes/auth.js';
import { itemRouter } from './routes/items.js';

export const app = express();
app.use(cors({ origin: config.clientOrigin }));
app.use(express.json({ limit: '100kb' }));
app.get('/api/health', (_, res) => res.json({ ok: true }));
app.use('/api/auth', authRouter);
app.use('/api/items', requireAuth, itemRouter);
app.use((error, _req, res, _next) => {
  if (error instanceof ZodError) return res.status(422).json({ error: 'Validation failed', details: error.issues });
  if (error?.code === 11000) return res.status(409).json({ error: 'A content item with this title already exists' });
  console.error(error); res.status(500).json({ error: 'Unexpected server error' });
});

