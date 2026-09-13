import mongoose from 'mongoose';

const options = { timestamps: true };
const tenantSchema = new mongoose.Schema({ name: { type: String, required: true, trim: true } }, options);
const userSchema = new mongoose.Schema({ tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true }, email: { type: String, required: true, unique: true, lowercase: true, trim: true }, passwordHash: { type: String, required: true } }, options);
const propertySchema = new mongoose.Schema({ tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true }, name: { type: String, required: true, trim: true }, address: { type: String, required: true, trim: true }, units: { type: Number, required: true, min: 1, max: 10000 } }, options);
const leaseSchema = new mongoose.Schema({
  tenantId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true }, propertyId: { type: mongoose.Schema.Types.ObjectId, required: true, ref: 'Property' },
  unitLabel: { type: String, required: true, trim: true }, residentName: { type: String, required: true, trim: true }, residentEmail: { type: String, required: true, lowercase: true, trim: true },
  monthlyRentCents: { type: Number, required: true, min: 1 }, depositCents: { type: Number, default: 0, min: 0 }, startDate: { type: Date, required: true }, endDate: { type: Date, required: true }, status: { type: String, enum: ['draft', 'active', 'ended'], default: 'draft' }
}, options);
leaseSchema.index({ tenantId: 1, propertyId: 1, unitLabel: 1, status: 1 });

export const Tenant = mongoose.model('Tenant', tenantSchema);
export const User = mongoose.model('User', userSchema);
export const Property = mongoose.model('Property', propertySchema);
export const Lease = mongoose.model('Lease', leaseSchema);

