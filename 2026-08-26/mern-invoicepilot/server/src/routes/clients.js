import { Router } from 'express';
import { Client } from '../models.js';
import { requiredStrings, validEmail } from '../validation.js';

export const clientRouter = Router();
clientRouter.get('/', async (req, res) => res.json(await Client.find({ workspaceId: req.user.workspaceId }).sort({ createdAt: -1 })));
clientRouter.post('/', async (req, res) => {
  if (requiredStrings(req.body, ['name','email']).length || !validEmail(req.body.email)) return res.status(422).json({ error: 'A client name and valid email are required' });
  res.status(201).json(await Client.create({ workspaceId: req.user.workspaceId, name: req.body.name, email: req.body.email, company: req.body.company || '' }));
});
clientRouter.delete('/:id', async (req, res) => {
  const result = await Client.deleteOne({ _id: req.params.id, workspaceId: req.user.workspaceId });
  if (!result.deletedCount) return res.status(404).json({ error: 'Client not found' });
  res.status(204).end();
});

