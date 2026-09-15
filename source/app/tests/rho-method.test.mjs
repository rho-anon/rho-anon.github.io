import test from 'node:test';import assert from 'node:assert/strict';
import {candidates,frontier,accepts,gateOutcome,teachingBatch,breadthDemo,workload} from '../src/lib/rho-method.mjs';
test('coverage can be redundant across multiple survivors without a single dominator',()=>{const f=frontier(candidates.slice(0,3));assert.deepEqual([...f.alive].sort(),['A','B']);assert.equal(f.probability.A,.5);assert.equal(f.probability.E,0);});
test('a new unique best survives, and terminal choice uses mean',()=>{const f=frontier(candidates.slice(0,4));assert.deepEqual([...f.alive].sort(),['A','B','C']);assert.equal(f.selected.id,'C');assert.equal(Object.values(f.probability).reduce((a,b)=>a+b,0),1);});
test('combined coverage prunes redundant specialists',()=>{assert.deepEqual([...frontier(candidates).alive],['D']);});
test('train gate compares totals, not improvement on every instance',()=>{assert.equal(accepts([.3,.7],[.8,.3]),true);assert.equal(accepts([.3,.7],[.5,.5]),false);assert.equal(accepts([.3,.7],[.5,.5],true),true);});
test('stage and perfect-score branches',()=>{assert.equal(gateOutcome([1,1],[1,1]),'skip');assert.equal(gateOutcome([.3,.7],[.8,.3],{stageChild:[.2,.3]}),'reject-stage');assert.equal(gateOutcome([.3,.7],[.8,.3],{staged:false,stageChild:[.2,.3]}),'full-validation');assert.equal(gateOutcome([.3,.7],[.1,.1]),'reject-train');});

test('objective keys change survivors without changing scalar scoring',()=>{const f=frontier(candidates.slice(0,4),'objective');assert.deepEqual([...f.alive].sort(),['B','C']);assert.equal(f.selected.id,'C');});
test('group and example settings determine unique stratified examples',()=>{for(let g=1;g<=3;g++)for(let e=1;e<=3;e++){const batch=teachingBatch(g,e,2);assert.equal(batch.length,g*e);assert.equal(new Set(batch).size,g*e);assert.equal(new Set(batch.map(id=>id.split('-')[0])).size,g);}});

test('same toy evaluations yield twelve instance parents versus two objective parents',()=>{const d=breadthDemo();assert.equal(d.instance.alive.size,12);assert.equal(d.objective.alive.size,2);});

test('work illustration keeps generations independent of feedback size',()=>{const a=workload(),b=workload({batch:9});assert.equal(a.generations,b.generations);assert.equal(a.totalPairedRollouts,400);assert.equal(b.totalPairedRollouts,1800);assert.equal(b.feedbackRecords,9);});
