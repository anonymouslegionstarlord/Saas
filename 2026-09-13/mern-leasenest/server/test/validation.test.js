import test from 'node:test';
import assert from 'node:assert/strict';
import { leaseSchema, occupancyMetrics, propertySchema } from '../src/validation.js';

test('validates property and lease dates', () => {
  assert.equal(propertySchema.safeParse({ name: 'Harbor', address: '14 Lake Avenue', units: 8 }).success, true);
  const bad = leaseSchema.safeParse({ propertyId: 'a'.repeat(24), unitLabel: '2B', residentName: 'Jordan Lee', residentEmail: 'j@example.com', monthlyRentCents: 100000, depositCents: 0, startDate: '2026-09-01', endDate: '2026-08-01', status: 'active' });
  assert.equal(bad.success, false);
});

test('calculates occupancy and rental metrics', () => {
  const now = new Date('2026-09-01T00:00:00Z');
  const result = occupancyMetrics([{ units: 4 }, { units: 6 }], [{ status: 'active', monthlyRentCents: 125000, endDate: '2026-09-20' }, { status: 'active', monthlyRentCents: 175000, endDate: '2027-01-01' }, { status: 'ended', monthlyRentCents: 90000, endDate: '2026-08-01' }], now);
  assert.deepEqual(result, { properties: 2, totalUnits: 10, occupiedUnits: 2, occupancyPercent: 20, monthlyRentCents: 300000, expiringSoon: 1 });
});

test('rejects invalid money and email input', () => {
  const result = leaseSchema.safeParse({ propertyId: 'x', unitLabel: '', residentName: 'A', residentEmail: 'bad', monthlyRentCents: -1, startDate: 'bad', endDate: 'bad' });
  assert.equal(result.success, false);
  assert.ok(result.error.issues.length >= 5);
});

