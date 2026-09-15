/** Deterministic teaching examples, not experimental results. */
export const candidates = [
 {id:'A',name:'Lift specialist',objectives:[.75,.70,.35,.30],scores:[.90,.20,.80,.30]},
 {id:'B',name:'Place specialist',objectives:[.65,.65,.80,.85],scores:[.40,.90,.50,.80]},
 {id:'E',name:'Redundant coverage',objectives:[.75,.70,.80,.80],scores:[.90,.90,.60,.70]},
 {id:'C',name:'New best on instance 1',objectives:[.80,.72,.78,.80],scores:[.95,.90,.70,.70]},
 {id:'D',name:'Combines the strengths',objectives:[.80,.72,.80,.85],scores:[.95,.90,.80,.80]},
];
export const mean = xs => xs.reduce((a,b)=>a+b,0)/xs.length;
export function frontier(rows, mode="instance") {
 const values=r=>mode==="objective"?r.objectives:r.scores;
 const best=values(rows[0]).map((_,i)=>Math.max(...rows.map(r=>values(r)[i])));
 const keys=best.map((v,i)=>new Set(rows.filter(r=>Math.abs(values(r)[i]-v)<1e-9).map(r=>r.id)));
 const order=rows.filter(r=>keys.some(k=>k.has(r.id))).slice().sort((a,b)=>mean(a.scores)-mean(b.scores));
 const alive=new Set(order.map(r=>r.id));
 let changed=true;
 while(changed){changed=false;for(const r of order){if(!alive.has(r.id))continue;
  if(keys.filter(k=>k.has(r.id)).every(k=>[...k].some(id=>id!==r.id&&alive.has(id)))){alive.delete(r.id);changed=true;break;}
 }}
 const coverage=Object.fromEntries(rows.map(r=>[r.id,keys.filter(k=>k.has(r.id)&&alive.has(r.id)).length]));
 const total=Object.values(coverage).reduce((a,b)=>a+b,0);
 const selected=rows.filter(r=>alive.has(r.id)).sort((a,b)=>mean(b.scores)-mean(a.scores)||coverage[b.id]-coverage[a.id])[0];
 return {best,alive,coverage,probability:Object.fromEntries(rows.map(r=>[r.id,total?coverage[r.id]/total:0])),selected};
}
export function accepts(parent,child,equal=false){const p=parent.reduce((a,b)=>a+b,0),c=child.reduce((a,b)=>a+b,0);return equal?c+1e-9>=p:c>p+1e-9;}
export function gateOutcome(parent,child,{equal=false,staged=true,stageParent=[.6,.6],stageChild=[.7,.65]}={}){
 if(parent.every(v=>v>=1))return 'skip';
 if(!accepts(parent,child,equal))return 'reject-train';
 if(staged&&!accepts(stageParent,stageChild,equal))return 'reject-stage';
 return 'full-validation';
}

export function teachingBatch(groups,examples,draw=0,stratified=true){
 if(!Number.isInteger(groups)||groups<1||groups>3||!Number.isInteger(examples)||examples<1||examples>3)throw new RangeError('Teaching controls support 1–3 groups and examples.');
 const counts=[8,3,3];
 if(stratified)return Array.from({length:groups},(_,k)=>{const g=(draw+k)%3;return Array.from({length:examples},(_,j)=>`${g}-${(draw+j)%counts[g]}`);}).flat();
 const pool=counts.flatMap((n,g)=>Array.from({length:n},(_,j)=>`${g}-${j}`));
 return Array.from({length:groups*examples},(_,i)=>pool[(draw*5+i)%pool.length]);
}

export function breadthDemo(instanceCount=12,objectiveCount=2){
 const rows=Array.from({length:12},(_,c)=>{
  const tensor=Array.from({length:instanceCount},(_,i)=>Array.from({length:objectiveCount},(_,o)=>c===i%12?.98:c===o?.65:.20+c*.01));
  return {id:`R${c+1}`,scores:tensor.map(mean),objectives:Array.from({length:objectiveCount},(_,o)=>mean(tensor.map(row=>row[o])))};
 });return {rows,instance:frontier(rows,'instance'),objective:frontier(rows,'objective')};
}

export function workload({generations=100,batch=2}={}){
 return {generations,feedbackRecords:batch,pairedPerGeneration:2*batch,totalPairedRollouts:generations*2*batch};
}
