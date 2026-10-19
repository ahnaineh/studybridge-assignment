"""Curate real results without replacing original rows or selecting better answers."""
import csv,json
from pathlib import Path
repo=Path(__file__).resolve().parent
base=repo/'evidence/c4'
paths=sorted((base/'balanced').glob('*/case_results.jsonl'))
records=[]
for p in paths:
 for line in p.read_text().splitlines():
  r=json.loads(line);r['source_run']=p.parent.name;records.append(r)
# CSV annotations are written separately; raw comparison.csv/JSONL remain unchanged.
criteria=['grounded_0_2','helpful_0_2','natural_0_2','instruction_following_0_2']
overrides=json.loads((base/'balanced_review_notes.json').read_text())
scored=[]
for r in records:
 row=dict(r['row']); row['source_run']=r['source_run']
 key=r['setup']+' :: '+r['case']
 if row['error']:
  row['notes']='Provider failure; quality unscored. Partial actions may precede a generation failure; inspect synthetic logs.'
 else:
  assert key in overrides, 'Unreviewed returned answer: '+key
  rating=overrides[key]
  for c,v in zip(criteria,rating['scores']):row[c]=v
  row['notes']=rating['notes']
 scored.append(row)
fields=list(scored[0])
with (base/'balanced_scored_all_attempts.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(scored)
# First returned answer per setup/case. Behavior failures are never replaced by
# a later better answer. Provider-only recovery attempts stay in the all-attempts CSV.
chosen={}
for row in scored:
 pair=(row['setup'],row['case'])
 if pair not in chosen or (chosen[pair]['error'] and not row['error']):chosen[pair]=row
with (base/'balanced_selected.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(chosen.values())
summary=[]
for setup in dict.fromkeys(r['setup'] for r in scored):
 group=[r for r in chosen.values() if r['setup']==setup]
 returned=[r for r in group if not r['error']]
 common=[r for r in returned if r['case'] in ['recommendation','missing_email','unknown_policy']]
 attempts=[r for r in scored if r['setup']==setup]
 summary.append({'setup':setup,'attempted':len(group),'total_attempts':len(attempts),
 'responses':len(returned),'provider_errors':sum(bool(r['error']) for r in attempts),
 'tool_passes':sum(int(r['tool_check']) for r in returned),
 'mean_quality_out_of_8':round(sum(sum(int(r[c]) for c in criteria) for r in returned)/len(returned),2) if returned else None,
 'common_case_responses':len(common),
 'common_case_tool_passes':sum(int(r['tool_check']) for r in common),
 'common_case_mean_quality_out_of_8':round(sum(sum(int(r[c]) for c in criteria) for r in common)/len(common),2) if common else None})
(base/'balanced_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'total_attempts':len(scored),'returned_attempts':sum(not r['error'] for r in scored),
 'unique_pairs':len(chosen),'selected_returned':sum(not r['error'] for r in chosen.values()),
 'tool_passes_selected':sum(int(r['tool_check']) for r in chosen.values() if not r['error']),
 'summary':summary},indent=2))
