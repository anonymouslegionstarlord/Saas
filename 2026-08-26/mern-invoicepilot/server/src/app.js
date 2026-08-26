import express from 'express';
import cors from 'cors';
import { config } from './config.js';
import { requireAuth } from './auth.js';
import { authRouter } from './routes/auth.js';
import { clientRouter } from './routes/clients.js';
import { invoiceRouter } from './routes/invoices.js';

export const app = express();
app.use(cors({ origin: config.clientOrigin }));
app.use(express.json({ limit: '100kb' }));
app.get('/api/health', (_req,res) => res.json({ status: 'ok' }));
app.use('/api/auth', authRouter);
app.use('/api/clients', requireAuth, clientRouter);
app.use('/api/invoices', requireAuth, invoiceRouter);
app.use((_req,res) => res.status(404).json({ error: 'Route not found' }));
app.use((error,_req,res,_next) => { console.error(error); res.status(error.name === 'CastError' ? 400 : 500).json({ error: error.name === 'CastError' ? 'Invalid identifier' : 'Unexpected server error' }); });

