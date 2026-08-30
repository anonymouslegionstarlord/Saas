import test from 'node:test';import assert from 'node:assert/strict';import {validateDesk,validateBooking} from '../src/validation.js';
test('accepts a valid desk',()=>assert.deepEqual(validateDesk({code:'DL-101',location:'Delhi Hub',floor:'1'}),[]));
test('rejects malformed desks',()=>assert.deepEqual(validateDesk({code:'!',location:'',floor:''}),['code','location','floor']));
test('validates booking identity and date',()=>{assert.deepEqual(validateBooking({deskId:'abc',date:'2030-01-01',employeeName:'Alex',employeeEmail:'a@example.com'}),[]);assert.deepEqual(validateBooking({deskId:'',date:'bad',employeeName:'',employeeEmail:'bad'}),['deskId','date','employeeName','employeeEmail'])});
