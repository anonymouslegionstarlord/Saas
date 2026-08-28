import test from 'node:test';import assert from 'node:assert/strict';import {normalizeFields,validateAnswers} from '../src/validation.js';
test('normalizes form fields and generates keys',()=>assert.deepEqual(normalizeFields([{label:'Work Email',type:'email',required:true}])[0],{key:'work_email',label:'Work Email',type:'email',required:true,order:0}));
test('rejects duplicate field keys',()=>assert.throws(()=>normalizeFields([{key:'name',label:'A'},{key:'name',label:'B'}]),/unique key/));
test('validates required, email, and number answers',()=>assert.deepEqual(validateAnswers([{key:'email',type:'email',required:true},{key:'score',type:'number',required:true}],{email:'bad',score:'x'}),['email must be an email','score must be a number']));
