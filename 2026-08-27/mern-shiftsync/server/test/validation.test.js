import test from 'node:test';import assert from 'node:assert/strict';import {validDate,validTime,validateShift} from '../src/validation.js';
test('accepts a complete shift',()=>assert.deepEqual(validateShift({employeeName:'Asha',employeeEmail:'a@example.com',date:'2026-08-27',start:'09:00',end:'17:00',role:'Support'}),[]));
test('rejects reverse times and malformed data',()=>assert.deepEqual(validateShift({employeeName:'',employeeEmail:'bad',date:'no',start:'18:00',end:'09:00',role:''}),['employeeName','employeeEmail','date','time','role']));
test('time and date helpers reject impossible formats',()=>{assert.equal(validTime('24:00'),false);assert.equal(validDate('not-a-date'),false)});
