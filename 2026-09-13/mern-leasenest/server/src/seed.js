import bcrypt from 'bcryptjs';
import mongoose from 'mongoose';
import { config } from './config.js';
import { Lease, Property, Tenant, User } from './models.js';

await mongoose.connect(config.mongoUri);
await Promise.all([Lease.deleteMany({}), Property.deleteMany({}), User.deleteMany({}), Tenant.deleteMany({})]);
const tenant = await Tenant.create({ name: 'Harbor Homes Demo' });
await User.create({ tenantId: tenant._id, email: 'owner@demo.local', passwordHash: await bcrypt.hash('demo-pass-123', 12) });
const property = await Property.create({ tenantId: tenant._id, name: 'Harbor Court', address: '14 Lake Avenue', units: 8 });
await Lease.create({ tenantId: tenant._id, propertyId: property._id, unitLabel: '2B', residentName: 'Jordan Lee', residentEmail: 'jordan@demo.local', monthlyRentCents: 185000, depositCents: 185000, startDate: new Date('2026-01-01'), endDate: new Date('2026-12-31'), status: 'active' });
console.log('Seeded owner@demo.local / demo-pass-123');
await mongoose.disconnect();

