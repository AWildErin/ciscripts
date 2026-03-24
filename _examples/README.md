# Examples
Here lies various examples from my in-development SCP:CB UE5 remake and my custom UE5 fork.

## Usage
This repo is expected to be a submodule *next* to your ci scripts. For example, SCP/Scripts/CI/ciscripts.

The examples also contain my current GitLab CI pipelines, showcasing how they're designed to work.

### Git
Our Git repositories used to be separated into separate repos for Unreal, and one per project. Included are our workflows we used for that.

### Perforce
Our Perforce setup is all games are in one depot, and use GitLab CI to handle all automation tasks. All our scripts exist in a root UnrealEngine repository.

## Notes

> [!NOTE] 
> Our UE5 CI pipeline relies on my custom [Sccache](https://github.com/AWildErin/sccache/tree/awe-changes) fork, to speed up compliation times, and SccacheExector which is accessible via the patch in the UnrealEngine folder. This has only been tested with UE5.3!
> All changes in both the patch and the supplied given BuildGraph scripts will be marked with AWE_CHANGES_[BEGIN/END] to clearly denote what changes I made.
