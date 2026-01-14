# Hatch plugins for tgzr.pipeline.asset packaging

> NOTE\
>    It's likely that this system will end up being a full-fledged builder
>    instead of a simple metadata_hook. All this README will then be 
>    obsolete. 

# Usage:

In your pyproject.toml, configure the build-system to include `tgzr.pipeline`:
```
[build-system]
requires = ["hatchling", "tgzr-pipeline"]
build-backend = "hatchling.build"
```

Then build: `hatch build -t wheel`

> !!! KNOWN BUG !!! \
>   If you don't specify a build target (`-t wheel`), you will build several
>   target, and bump the asset version several times !!!\
>   We're looking into solving this.  


# WARNING

Building directly in the local PI folder like:

`hatch build -t sdist /path/to/local/PI` 

or with a configured build directory in pyproject.toml:
```
[tool.hatch.build]
directory = "/path/to/local/PI"
```
will overwrite an existing package with the same number.

It means that if the PI folder is shared by many users, someone can 
overwrite someone else's asset !

!!! EVEN WORST !!!

If someone builds with `--clean` option, all other versions of the asset in the PI folder will be deleted !!!

So you **MUST** build in a tmp folder **and then** publish the asset package to the local PI **ONLY IF** that file doesn't exist there yet.

## SOLUTION:

Build locally and use the `tgzr-pipeline-asset` publisher provided by `tgzr.pipeline`:
```
hatch build -t sdist --clean
hatch publish -p tgzr-pipeline-asset dist/*
``` 

If you don't want to polute your asset folder with dist files, just give a path to another folder:
(using `--clean` allow to give path/* to publish command)
```
hatch build -t sdist --clean /path/to/dist/folder
hatch publish -p tgzr-pipeline-asset /path/to/dict/folder/*
``` 

The `tgzr-pipeline-asset` publisher can define targets in the asset pyproject.toml:
```
[tool.hatch.publish.tgzr-pipeline-asset]
blessed="path/to/the/blessed/folder"
review="path/to/the/review/folder"
target="review"
```
With this config, the default is to publish to "review" folder.
You can override the target like this:
`hatch publish -p tgzr-pipeline-asset -o target=blessed dist/*`


# Dev Usage

While developing the builder/hooks, you must tell python to use your code 
instead of the published package's code. But installing in edit mode will
not work since the build is done in isolation from your venv.

You need to specify the dependency like this in your pyproject.toml:
```
[build-system]
requires = ["hatchling", "hatch-tgzr-asset @ file:///path/to/your/folder/tgzr.pipeline"]
build-backend = "hatchling.build"

```

But this is not enough! 
Hatch caches the build dependency to avoid reinstalling them for each build.
So in order to see your code changes, your need to do remove the venv with build dependencies.

This should work: `hatch env remove hatch-build` \
But in doesn't, so nuke them all: `hatch env prune`\
And then: `hatch build -t sdist`