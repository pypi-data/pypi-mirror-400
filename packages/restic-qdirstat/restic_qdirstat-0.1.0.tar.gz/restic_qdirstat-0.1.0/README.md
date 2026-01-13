# restic-qdirstat

Analyze the size of restic snapshots using QDirStat.

## Usage

Install using `pipx` (or `uvx`):

```sh
pipx install restic-qdirstat
```

Then, run:

```sh
restic ls -l latest | restic-qdirstat -o restic.cache.gz
```

Finally, you can open the generated `restic.cache.gz` archive in QDirStat (File -> Read Cache File) and inspect the snapshot.
