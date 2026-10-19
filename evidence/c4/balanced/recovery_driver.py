"""Finish the matched study, then retry only unanswered transient-provider cases."""
import hashlib,json,shutil,time,traceback
from pathlib import Path
status=Path('final-study-status.json')
status.write_text(json.dumps({'state':'waiting_for_primary'}))
try:
    started=time.monotonic()
    while True:
        main=json.loads(Path('balanced-status.json').read_text())
        if main['state']=='complete':break
        if main['state']=='error':raise RuntimeError(main['error'])
        if time.monotonic()-started>3600:raise TimeoutError('Primary run did not finish within the watcher window.')
        time.sleep(5)
    time.sleep(13)
    # The primary's own snapshot is complete before this driver update.
    Path('experiments.py').write_text(Path('experiments_recovery_source.py').read_text())
    from experiments import run_experiments,transient_failure_pairs
    directories=[Path(main['directory'])]
    for round_no in range(1,3):
        csvs=[p/'comparison.csv' for p in directories]
        pairs=transient_failure_pairs(csvs)
        if not pairs:break
        status.write_text(json.dumps({'state':'recovering_provider_errors','round':round_no,'pending':len(pairs),'directories':[str(p) for p in directories]}))
        print('Recovery round',round_no,'unanswered provider-error pairs',len(pairs),flush=True)
        result=run_experiments(balanced=True,workers=3,case_pairs=pairs)
        source=result/'source';source.mkdir()
        for name in ['agent_core.py','experiments.py','requirements.txt']:
            shutil.copy2(name,source/name)
        (result/'source_sha256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()},indent=2))
        (result/'recovery_selection.json').write_text(json.dumps({'round':round_no,'source_csvs':[str(p) for p in csvs],
            'pairs':sorted(pairs),'selection':'Only 503/504 cases without any returned answer. Behavioral failures are retained and not rerun.'},indent=2))
        directories.append(result)
    pending=transient_failure_pairs([p/'comparison.csv' for p in directories])
    status.write_text(json.dumps({'state':'complete','directories':[str(p) for p in directories],
        'remaining_provider_pairs':sorted(pending),'initial_sequential_directory':Path('balanced-initial-directory.txt').read_text()},indent=2))
    print(status.read_text(),flush=True)
except Exception:
    status.write_text(json.dumps({'state':'error','error':traceback.format_exc()}))
    raise
