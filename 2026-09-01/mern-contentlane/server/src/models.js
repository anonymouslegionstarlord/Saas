import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true },
  name: { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true, trim: true },
  passwordHash: { type: String, required: true },
  role: { type: String, enum: ['owner', 'editor'], default: 'owner' }
}, { timestamps: true });

const contentSchema = new mongoose.Schema({
  tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true },
  title: { type: String, required: true, trim: true },
  channel: { type: String, enum: ['blog', 'email', 'social', 'video'], required: true },
  owner: { type: String, required: true, trim: true },
  dueDate: { type: Date, required: true },
  status: { type: String, enum: ['idea', 'draft', 'review', 'approved', 'published'], default: 'idea' },
  brief: { type: String, default: '', maxlength: 2000 },
  reviewerNote: { type: String, default: '', maxlength: 1000 }
}, { timestamps: true });
contentSchema.index({ tenantId: 1, title: 1 }, { unique: true });

export const User = mongoose.model('User', userSchema);
export const ContentItem = mongoose.model('ContentItem', contentSchema);

