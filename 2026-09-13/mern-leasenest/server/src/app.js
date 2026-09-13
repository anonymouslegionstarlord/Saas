import cors from 'cors';
import express from 'express';
import { config } from './config.js';
import { router } from './routes.js';

export const app = express();
app.use(cors({ origin: config.clientOrigin }));
app.use(express.json({ limit: '100kb' }));
app.get('/api/health', (_req, res) => res.json({ status: 'ok' }));
app.use('/api', router);
app.use((req, res) => res.status(404).json({ error: 'Route not found' }));
app.use((err, _req, res, _next) => { console.error(err); if (err?.name === 'CastError') return res.status(404).json({ error: 'Record not found' }); res.status(500).json({ error: 'Internal server error' }); });

