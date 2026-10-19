import hashlib,json,shutil,traceback
from pathlib import Path
from experiments import run_experiments,transient_failure_pairs
status=Path('final-study-status.json')
previous=json.loads(status.read_text())
directories=[Path(p) for p in previous['directories']]
try:
    for round_no in range(1,3):
        csvs=[p/'comparison.csv' for p in directories]
        pairs=transient_failure_pairs(csvs)
        if not pairs:break
        status.write_text(json.dumps({**previous,'state':'recovering_remaining_provider_error','pending':sorted(pairs),'round':round_no,'directories':[str(p) for p in directories]}))
        print('Retry unanswered provider-error pairs:',sorted(pairs),flush=True)
        result=run_experiments(balanced=True,workers=3,case_pairs=pairs)
        source=result/'source';source.mkdir()
        for name in ['agent_core.py','experiments.py','requirements.txt']:shutil.copy2(name,source/name)
        (result/'source_sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},indent=2))
        (result/'recovery_selection.json').write_text(json.dumps({'source_csvs':[str(p) for p in csvs],
            'pairs':sorted(pairs),'selection':'Unanswered provider 500/503/504 cases only. Previously returned behavior is not retried.'},indent=2))
        directories.append(result)
    previous.update(state='complete',directories=[str(p) for p in directories],
                    remaining_provider_pairs=sorted(transient_failure_pairs([p/'comparison.csv' for p in directories])))
    status.write_text(json.dumps(previous,indent=2))
    print(status.read_text(),flush=True)
except Exception:
    status.write_text(json.dumps({**previous,'state':'error','error':traceback.format_exc()}))
    raise
