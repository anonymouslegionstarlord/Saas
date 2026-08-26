import { Router } from 'express';
import { Client, Invoice } from '../models.js';
import { invoiceTotal, requiredStrings } from '../validation.js';

export const invoiceRouter = Router();
invoiceRouter.get('/', async (req, res) => res.json(await Invoice.find({ workspaceId: req.user.workspaceId }).populate('clientId','name company email').sort({ createdAt: -1 })));
invoiceRouter.post('/', async (req, res) => {
  if (requiredStrings(req.body, ['clientId','number','dueDate']).length) return res.status(422).json({ error: 'Client, invoice number, and due date are required' });
  const client = await Client.findOne({ _id: req.body.clientId, workspaceId: req.user.workspaceId });
  if (!client) return res.status(404).json({ error: 'Client not found' });
  try {
    const invoice = await Invoice.create({ workspaceId: req.user.workspaceId, clientId: client.id, number: req.body.number, dueDate: req.body.dueDate, items: req.body.items, total: invoiceTotal(req.body.items) });
    res.status(201).json(await invoice.populate('clientId','name company email'));
  } catch (error) { if (error.code === 11000) return res.status(409).json({ error: 'Invoice number already exists' }); if (error.message.startsWith('At least') || error.message.startsWith('Every')) return res.status(422).json({ error: error.message }); throw error; }
});
invoiceRouter.patch('/:id/status', async (req, res) => {
  if (!['draft','sent','paid'].includes(req.body.status)) return res.status(422).json({ error: 'Status must be draft, sent, or paid' });
  const invoice = await Invoice.findOneAndUpdate({ _id: req.params.id, workspaceId: req.user.workspaceId }, { status: req.body.status }, { new: true });
  if (!invoice) return res.status(404).json({ error: 'Invoice not found' });
  res.json(invoice);
});

