import math
import random
import shutil
from pathlib import Path


def run(args):
    source_dir_fullpath: Path = args.source_dir_path.absolute()
    files_portion_size: int = args.files_portion_size

    source_dir_name = source_dir_fullpath.stem

    for dest_dir_path in [
        x
        for x in source_dir_fullpath.parent.glob(f"{source_dir_name} # *")
        if x.is_dir()
    ]:
        for file_path in dest_dir_path.iterdir():
            shutil.move(file_path, source_dir_fullpath)

        shutil.rmtree(dest_dir_path)

    file_paths = [
        x for x in source_dir_fullpath.iterdir() if x.is_file() and x.suffix == ".mp3"
    ]

    files_len = len(file_paths)

    dirs_len = math.ceil(
        files_len / files_portion_size,
    )

    files_to_move_len = files_len

    dir_lens = []

    for k in range(dirs_len):
        dirs_to_move_to = dirs_len - k

        files_to_move_to_dir_len = math.ceil(files_to_move_len / dirs_to_move_to)

        dir_lens.append(files_to_move_to_dir_len)

        files_to_move_len -= files_to_move_to_dir_len

    artists_dir_lens = {}

    for file_path in file_paths:
        artist = file_path.stem.split(" - ")[0]

        if artist not in artists_dir_lens:
            artists_dir_lens[artist] = {
                dir_indices: 0 for dir_indices in range(dirs_len)
            }

        artist_dir_lens: dict = artists_dir_lens[artist]

        artist_dir_lens_in_use = {
            index: artist_dir_len
            for index, artist_dir_len in artist_dir_lens.items()
            if dir_lens[index] > 0
        }

        min_len_dir_indices = [
            index
            for index, artist_dir_len in artist_dir_lens_in_use.items()
            if artist_dir_len == min(artist_dir_lens_in_use.values())
        ]

        random_dir_index = random.choice(min_len_dir_indices)

        dest_dir_path = (
            source_dir_fullpath.parent / f"{source_dir_name} # {random_dir_index + 1}"
        )
        dest_dir_path.mkdir(exist_ok=True)

        shutil.move(file_path, dest_dir_path)

        artist_dir_lens[random_dir_index] = artist_dir_lens[random_dir_index] + 1
        dir_lens[random_dir_index] = dir_lens[random_dir_index] - 1
