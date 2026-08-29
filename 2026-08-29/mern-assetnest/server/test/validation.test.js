import test from 'node:test';import assert from 'node:assert/strict';import {validateAsset,validateCheckout} from '../src/validation.js';
test('accepts valid inventory input',()=>assert.deepEqual(validateAsset({tag:'LAP-001',name:'Laptop',category:'Computer',purchaseCost:1200}),[]));
test('rejects malformed inventory input',()=>assert.deepEqual(validateAsset({tag:'!',name:'',category:'x',purchaseCost:-1}),['tag','name','category','purchaseCost']));
test('validates checkout assignee and date',()=>{assert.deepEqual(validateCheckout({assignedTo:'Alex',dueDate:'2030-01-01'}),[]);assert.deepEqual(validateCheckout({assignedTo:'',dueDate:'bad'}),['assignedTo','dueDate'])});
