import test from 'node:test';import assert from 'node:assert/strict';import {validateCohort,validateEnrollment} from '../src/validation.js';
test('accepts a valid cohort',()=>assert.deepEqual(validateCohort({name:'FastAPI',topic:'APIs',instructor:'Asha',startDate:'2030-01-01',endDate:'2030-02-01',capacity:30}),[]));
test('rejects malformed cohort data',()=>assert.deepEqual(validateCohort({name:'',topic:'',instructor:'',startDate:'bad',endDate:'bad',capacity:0}),['name','topic','instructor','dates','capacity']));
test('validates learner enrollment',()=>{assert.deepEqual(validateEnrollment({cohortId:'abc',learnerName:'Alex',learnerEmail:'a@example.com'}),[]);assert.deepEqual(validateEnrollment({cohortId:'',learnerName:'',learnerEmail:'bad'}),['cohortId','learnerName','learnerEmail'])});
