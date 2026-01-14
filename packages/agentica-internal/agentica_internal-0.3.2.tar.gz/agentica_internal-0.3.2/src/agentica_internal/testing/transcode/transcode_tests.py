# fmt: off

from rich import print

from agentica_internal.core.print import *
from pathlib import Path

from agentica_internal.core.debug import enable_rich_tracebacks
from agentica_internal.warpc_transcode.transcript import TranscriptFile



enable_rich_tracebacks()

TRANSCRIPTS_DIR = Path(__file__).parent / "transcripts"


def load_transcript(name: str) -> TranscriptFile:
    path = TRANSCRIPTS_DIR / name
    return TranscriptFile(path)


def generate_combined():

    glob = list(TRANSCRIPTS_DIR.glob("*"))

    for j, path in enumerate(glob):
        print(j, path)
        if not path.is_dir():
            continue
        transcript = TranscriptFile(path)
        transcript.recompute(False)
        if problem := transcript.problems():
            print(problem)
            transcript.pprint(width=80)
            break


def run_combined():
    files = list(TRANSCRIPTS_DIR.glob("*.jsonl"))

    for j, path in enumerate(files):
        # if 'demo_fiddler' not in path.name:
        #     continue
        print(j, path)
        if 'agent' in path.name:
            continue
        if not path.is_file():
            continue
        transcript = TranscriptFile(path)
        transcript.recompute(False)
        problems = transcript.problems()
        if problems:
            print(problems)
            transcript.pprint(width=120)


if __name__ == '__main__':
    generate_combined()
    # run_combined()
