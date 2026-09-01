import mongoose from 'mongoose';
import bcrypt from 'bcryptjs';
import { config } from './config.js';
import { ContentItem, User } from './models.js';

await mongoose.connect(config.mongoUri);
const email = 'demo@contentlane.local';
let user = await User.findOne({ email });
if (!user) user = await User.create({ tenantId: new mongoose.Types.ObjectId(), name: 'Demo Owner', email, passwordHash: await bcrypt.hash('DemoPass123!', 12) });
await ContentItem.deleteMany({ tenantId: user.tenantId });
await ContentItem.insertMany([
  { tenantId: user.tenantId, title: 'September customer story', channel: 'blog', owner: 'Ava', dueDate: new Date('2026-09-08'), status: 'draft', brief: 'Interview and outcomes.' },
  { tenantId: user.tenantId, title: 'Product digest', channel: 'email', owner: 'Ravi', dueDate: new Date('2026-09-04'), status: 'review', brief: 'Monthly product updates.' }
]);
console.log('Seeded demo@contentlane.local / DemoPass123! (local demo only)');
await mongoose.disconnect();

