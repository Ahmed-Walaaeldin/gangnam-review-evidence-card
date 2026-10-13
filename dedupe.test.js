const assert = require('node:assert/strict');
const { compare, triage } = require('./dedupe.js');

const a = { clinic: 'AB PS', date: '2026-04-13', procedure: 'rhinoplasty', summary: 'A third nose revision followed two unsatisfactory surgeries and a drooping tip. The surgeon explained prior failures. The early tip line looked good.' };
const b = { clinic: 'AB PS', date: '2026-04-13', procedure: 'rhinoplasty', summary: 'After two unsatisfactory nose surgeries with a drooping tip, a third revision looked promising early. The surgeon explained previous failures and the tip line looked good.' };
const c = { clinic: 'AB PS', date: '2026-04-13', procedure: 'eyelid surgery', summary: 'The eyelid result made makeup easier and recovery took two weeks.' };
const d = { ...b, clinic: 'Another clinic' };

assert.equal(compare(a, b).candidate, true, 'similar same-clinic records need review');
assert.equal(compare(a, c).candidate, false, 'different procedures stay separate');
assert.equal(compare(a, d).candidate, false, 'different clinics stay separate');
assert.equal(triage([a, b, c, d]).length, 1, 'only one pair enters the queue');
console.log('Duplicate triage checks passed');
