import test from'node:test';import assert from'node:assert/strict';import{attendeeSchema,eventMetrics,eventSchema}from'../src/validation.js';
test('validates events and attendees',()=>{assert.equal(eventSchema.safeParse({name:'Meetup',venue:'Main Hall',startsAt:'2026-11-01',capacity:100,status:'open'}).success,true);assert.equal(attendeeSchema.safeParse({eventId:'bad',name:'A',email:'wrong',ticketType:'other'}).success,false)});
test('calculates capacity and check-in metrics',()=>{const r=eventMetrics({capacity:5},[{checkedInAt:new Date()},{checkedInAt:null}]);assert.deepEqual(r,{registered:2,checkedIn:1,remaining:3,capacity:5,fillPercent:40,checkInPercent:50})});
test('prevents invalid capacity',()=>{assert.equal(eventSchema.safeParse({name:'Meetup',venue:'Hall',startsAt:'2026-11-01',capacity:0}).success,false)});

