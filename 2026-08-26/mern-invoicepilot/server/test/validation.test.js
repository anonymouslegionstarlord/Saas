import test from 'node:test';
import assert from 'node:assert/strict';
import { invoiceTotal, validEmail } from '../src/validation.js';

test('invoiceTotal calculates and rounds line items', () => assert.equal(invoiceTotal([{ description:'Design',quantity:2,rate:99.995 }]), 199.99));
test('invoiceTotal rejects invalid items', () => assert.throws(() => invoiceTotal([{ description:'',quantity:0,rate:-1 }]), /Every item/));
test('validEmail accepts normal addresses and rejects malformed values', () => { assert.equal(validEmail('owner@example.com'), true); assert.equal(validEmail('bad-address'), false); });

