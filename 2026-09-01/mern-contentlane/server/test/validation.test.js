import test from 'node:test';
import assert from 'node:assert/strict';
import { allowedTransition, itemSchema, registerSchema } from '../src/validation.js';

test('validates registration and rejects weak passwords', () => {
  assert.equal(registerSchema.safeParse({ name:'Owner', workspace:'Acme', email:'owner@acme.test', password:'password1' }).success, true);
  assert.equal(registerSchema.safeParse({ name:'O', workspace:'A', email:'bad', password:'x' }).success, false);
});
test('validates content input', () => {
  assert.equal(itemSchema.safeParse({ title:'Launch story', channel:'blog', owner:'Mira', dueDate:'2026-09-12', brief:'' }).success, true);
  assert.equal(itemSchema.safeParse({ title:'X', channel:'podcast', owner:'', dueDate:'never' }).success, false);
});
test('enforces editorial state transitions', () => {
  assert.equal(allowedTransition('draft', 'review'), true);
  assert.equal(allowedTransition('review', 'draft'), true);
  assert.equal(allowedTransition('idea', 'published'), false);
});

