from pathlib import Path
import shutil
import os
from hashlib import sha256


ROOT = Path(__file__).parent.parent
EXERCISES = ROOT / 'exercises'
SOLUTIONS = ROOT / 'solutions'

INGORED_FILENAMES = (
    '__pycache__'
)

IGNORED_EXTENSIONS = (
    '.pyc',
    '.egg-info',
)

FOLDER_RENAMINGS = {
    "tmclass_solutions": "tmclass_exercises"
}
FOLDER_RENAMINGS_REVERSED = {v: k for k, v in FOLDER_RENAMINGS.items()}


def should_ignore(path):
    if path.name.startswith('.'):
        return True
    if path.name in INGORED_FILENAMES:
        return True
    if path.name.endswith(IGNORED_EXTENSIONS):
        return True
    return False


def hash_file(path):
    with open(path, 'rb') as f:
        return sha256(f.read()).hexdigest()


def hash_text(text):
    return sha256(text.encode('utf-8')).hexdigest()


def sync_file(source, target_parent):
    assert source.is_file()
    assert target_parent.is_dir()
    target = target_parent / source.name
    if (source.name not in ('__init__.py', 'setup.py', 'utils.py')
            and source.name.endswith('.py')
            and not source.name.startswith('test_')):
        # This is a Python module with empty template and exercise
        # instructions: it is not meant to be synchronized automatically.
        return

    elif source.name.endswith('.py'):
        with open(source, mode='r', encoding="utf-8") as f:
            original_text = f.read()
        rewritten_text = original_text.replace("text-mining-class-solutions",
                                               "text-mining-class-exercises")
        rewritten_text = rewritten_text.replace("tmclass_solutions",
                                                "tmclass_exercises")
        if (not target.exists()
                or hash_text(rewritten_text) != hash_file(target)):
            print(f"Synchronizing {source} to {target}")
            target.write_text(rewritten_text, encoding='utf-8')

    elif not target.exists() or hash_file(source) != hash_file(target):
        print(f"Copying {source} to {target}")
        shutil.copyfile(source, target)


def sync_folder(source, target_parent, target_name=None):
    assert source.is_dir()
    assert target_parent.is_dir()

    if target_name is None:
        target_name = FOLDER_RENAMINGS.get(source.name, source.name)

    target = target_parent / target_name
    if not target.exists():
        print(f"Creating directory {target}")
        target.mkdir()

    source_filenames = set(s.name for s in source.iterdir())
    for target_child in sorted(target.iterdir()):
        if should_ignore(target_child):
            continue

        renamed_child_name = FOLDER_RENAMINGS_REVERSED.get(
            target_child.name, target_child.name)
        if renamed_child_name not in source_filenames:
            print(f"Deleting {target_child}")
            if target_child.is_dir():
                shutil.rmtree(target_child)
            else:
                os.unlink(target_child)

    for source_child in sorted(source.iterdir()):
        if should_ignore(source_child):
            continue

        if source_child.is_dir():
            sync_folder(source_child, target)
        elif source_child.is_file():
            sync_file(source_child, target)
        else:
            raise NotImplementedError(f"Unsuported file: {source_child}")


if __name__ == "__main__":
    sync_folder(SOLUTIONS, ROOT, target_name='exercises')
