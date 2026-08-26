import mongoose from 'mongoose';

const options = { timestamps: true };
const workspaceSchema = new mongoose.Schema({ name: { type: String, required: true, trim: true, maxlength: 80 } }, options);
const userSchema = new mongoose.Schema({ workspaceId: { type: mongoose.Schema.Types.ObjectId, ref: 'Workspace', required: true, index: true }, name: { type: String, required: true, trim: true }, email: { type: String, required: true, unique: true, lowercase: true, trim: true }, passwordHash: { type: String, required: true } }, options);
const clientSchema = new mongoose.Schema({ workspaceId: { type: mongoose.Schema.Types.ObjectId, ref: 'Workspace', required: true, index: true }, name: { type: String, required: true, trim: true, maxlength: 100 }, email: { type: String, required: true, trim: true, lowercase: true }, company: { type: String, trim: true, maxlength: 100, default: '' } }, options);
const itemSchema = new mongoose.Schema({ description: { type: String, required: true, trim: true, maxlength: 160 }, quantity: { type: Number, required: true, min: 0.01 }, rate: { type: Number, required: true, min: 0 } }, { _id: false });
const invoiceSchema = new mongoose.Schema({ workspaceId: { type: mongoose.Schema.Types.ObjectId, ref: 'Workspace', required: true, index: true }, clientId: { type: mongoose.Schema.Types.ObjectId, ref: 'Client', required: true }, number: { type: String, required: true, trim: true }, dueDate: { type: Date, required: true }, status: { type: String, enum: ['draft','sent','paid'], default: 'draft' }, items: { type: [itemSchema], validate: value => value.length > 0 }, total: { type: Number, required: true, min: 0 } }, options);
invoiceSchema.index({ workspaceId: 1, number: 1 }, { unique: true });

export const Workspace = mongoose.model('Workspace', workspaceSchema);
export const User = mongoose.model('User', userSchema);
export const Client = mongoose.model('Client', clientSchema);
export const Invoice = mongoose.model('Invoice', invoiceSchema);

