import { Router } from 'express';
import mongoose from 'mongoose';
import { ContentItem } from '../models.js';
import { allowedTransition, itemSchema, transitionSchema } from '../validation.js';

export const itemRouter = Router();

itemRouter.get('/', async (req, res) => {
  const query = { tenantId: req.auth.tenantId };
  if (req.query.status) query.status = req.query.status;
  const items = await ContentItem.find(query).sort({ dueDate: 1 }).lean();
  const counts = await ContentItem.aggregate([{ $match: { tenantId: new mongoose.Types.ObjectId(req.auth.tenantId) } }, { $group: { _id: '$status', count: { $sum: 1 } } }]);
  res.json({ items, counts: Object.fromEntries(counts.map(x => [x._id, x.count])) });
});

itemRouter.post('/', async (req, res, next) => {
  try { const data = itemSchema.parse(req.body); res.status(201).json(await ContentItem.create({ ...data, tenantId: req.auth.tenantId })); }
  catch (error) { next(error); }
});

itemRouter.patch('/:id/transition', async (req, res, next) => {
  try {
    if (!mongoose.isValidObjectId(req.params.id)) return res.status(404).json({ error: 'Content item not found' });
    const data = transitionSchema.parse(req.body);
    const item = await ContentItem.findOne({ _id: req.params.id, tenantId: req.auth.tenantId });
    if (!item) return res.status(404).json({ error: 'Content item not found' });
    if (!allowedTransition(item.status, data.status)) return res.status(409).json({ error: `Cannot move from ${item.status} to ${data.status}` });
    item.status = data.status; item.reviewerNote = data.reviewerNote; await item.save(); res.json(item);
  } catch (error) { next(error); }
});

itemRouter.delete('/:id', async (req, res) => {
  if (!mongoose.isValidObjectId(req.params.id)) return res.status(404).json({ error: 'Content item not found' });
  const deleted = await ContentItem.findOneAndDelete({ _id: req.params.id, tenantId: req.auth.tenantId });
  if (!deleted) return res.status(404).json({ error: 'Content item not found' });
  res.status(204).end();
});

