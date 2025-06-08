# Gallery readme

Min lilla galleri static site generator.

I have randomly produced a few "wallpaper" worthy images every now and then in whichever way, but i never knew what to do with them. Blah blah this is a static gallery generator that is meant to be very minimal but also easy to extend for whatever little usecase one comes up with. 

Let me tell you upfront about the hassles with my offering:

- requires a bit of a setup if youre new to python development. it's not too hard but there's a bit of it. i will try to explain.
- you will have to write image descriptions in the json mines
- you will have to run a few commands each time to update file knowledge + generate html
- you have to incidentally host the script, or change build directory, because i set the default for my specific use case (y)(a)
- binga bonga bing

In return, how about:

- automatic thumbnail generation
- os agnostic win/linux/mac and probably more but i have tried these
- extendable versioned json "database" with metadata, where human changes are persisted
  - easy to extend with python
  - possible to extend with external tools
  - "schema" key definition take lambdas for values - `"md5": lambda current, old: current.get("md5")`
    - this makes a library rescan automatically populate these fields retroactively
    - immediately usable in the templates for the entire library
- permissive license. who give a shit.

Dependencies:

- _jinja2_ for templating,
- _pillow_ for image stuff.

Rember i love you ^.^

## Install python shit so you can run. This is portable don't worry

True as of 2025-06-07.

First step is clone this with git to your computer. This looks like `$ git clone https://git.awblawdl bla bla`.

Github gives you the right command from the clone button up there ↖️⬆️↗️ idk where it is

### Installing pyenv

We're using _pyenv_, a command-line tool for managing lots of separate python installations on your computer, switching between them for different situations or projects. It's very nice. Another tool is _conda_ but for this, we've used pyenv.

It allows you to switch between different (installed) versions of python by running `$ pyenv use {version}`. You can use `$ pyenv versions` to list what's available. Versions are isolated and run different installations of pip, etc.

Another reason for using this is that OS:es or linux distros are sometimes a bit weird with which version of python they give you, and when they give you updates. This lets you be explicit about it. Tell them how it is yeah.

- Install pyenv. For windows there is _pyenv-win_.
- Install a pyenv version.
  - A way to find what's latest at the time is `pyenv latest -k 3`. (`-k` means check online and not on your computer, 3 is the version)
  - You should install this and use it as default. `$ pyenv install 3.13.3` använde jag här inne så den får det bli i exempel
  - Maybe you can do `$ pyenv install 3`? i dont know
  - Use `$ pyenv global 3.13.3` för att sätta "master" global variant
- Install the correct python version
  - Since this is a _pdm_ project, there is probably a specific version intended. We can check the `pyproject.toml` for information.
  - At the time of writing, the .toml file says `requires-python = ">=3.13"`. This means anything above this is probably fine.
  - I don't know if there should ever be a reason to not install the newest, but im a bit naive and good hearted.

In any case, once some version is decided and installed, we can:

- Tell pyenv which Python version to use for _this_ directory only: `$ pyenv local 3.13.3`
- This creates a `.python-version` file. Now, whenever you're in this folder, your shell will automatically use Python 3.11.5.

### Installing pdm

Now, bring in _pdm_. This is a package manager what does some strange things also. It keeps a copy of a clean python environment in the `.venv` directory which is a bit interesting. It should not be commited, hence putting it in the `.gitignore`.

The reason for doing this is that it allows plugins (like pillow, that we want to use for generating thumbnails) to be installed only in this project. If you are doing multiple things, they often end up requiring different versions of plugins, and it can become weird. This way, all projects are isolated from each other.

- måste install han `$ pip install pdm`
- run `$ pdm install` för att få allt jox.
- pdm will see that pyenv has activated python 3.13.3, and it will create its virtual environment (.venv) using that specific version.
- then it will check `pyproject.toml` for what plugins and versions that are required for the project, and download + install them into the .venv.

> **There is a danger here**: That penultimate list point, did you notice it? pdm will create its .venv using _the version pyenv was set to at the time_. If you later do `$ pyenv local 3.15.0`, pdm will still use that old 3.13.3 installation.
> 
> This will cause some shit probably. What to do is to then _tell this to pdm_, and it will figure all this out for you no problem. But you have to instruct it to do so. The command is `$ pdm use 3.13.3`, after which you will have to re-run `$ pdm install`.

## Running the generator

This is a _static site generator_. It reads some files and produces html and stuff that is entirely without scripts.

It is operated via a few (mostly two) `pdm run` commands. These are just aliases for `$ python {some_file.py}`. (These are arbitrary and defined in the `pyproject.toml` file.)

### On the model, and scanning it

Images are grouped as "series". To create a series, gather some images and put them in a subfolder to `wallpapers`. An example can be `wallpapers/my_cat/sniling.jpg`. If i also have a `wallpapers/my_cat/scrunge.png`, they will both belong to the series _my_cat_.

Once you've placed some images in your library, you will want to "scan" them and populate the generators' knowledge about your stuff. The result of this action shall be a json file in the folder `states/`.

```
$ pdm run scan
```

Once this is done, you can find a new timestamped json in `states/`. Some fields should be populated already. By default, you can safely edit this file. Now would be a good time to add some descriptions, for example.

Thumbnails are also generated at this step, as is any key/function you extend the base schema with. More about this later, however.

### Generating html

When you are satisfied with the state of your json file, it's time to generate the html.

```
$ pdm run html
```

This uses the jinja template in `templates/index.html` to completely overwrite the `index.html` in the project root.

Now you can host the entire dang project and it will just work. It will also expose a bunch of build artifacts but that's your problem. I know it's unfortunate and i am working on some way of solving this.



## Gallery design

A templating engine called _jinja2_ is used to generate the html from a _template_, in our case `templates/index.html`. This is basically a regular html file, but with some special commands that allow you to access the metadata of an image or series (these concepts are discussed above). By building this file to be an example of a single image in a single series, the `pdm run html` step repeats that example using the metadata from the latest json file in `states/`.

## Adding new metadata types

The key to this is the `IMAGE_SCHEMA` in `src/schema.py`. It is a sort of schema where each key is a function.

When `$pdm run scan` is called, for each image, first a "context" object is created with the image and its metadata. Then, for each field in the schema, it is called with both that context, and the previous object. The results are coalesced the new entry for that image.

### Example

Let's say `width` wasn't defaultly available (it is!) and i wanted to implement it. I would edit `IMAGE_SCHEMA`:

```python
IMAGE_SCHEMA = {
    "name": lambda context, old_metadata: context.get("name"),
    "md5": lambda context, old_metadata: context.get("md5"),
    "comments": lambda context, old_metadata: old_metadata.get("comments", "") if old_metadata else "",
    "tags": lambda context, old_metadata: old_metadata.get("tags", []) if old_metadata else [],
    
    # Grab the width from the Image object directly, as the context exposes it
    "width": lambda context, old_metadata: current.img.width,
```

Now, as soon as i run `$pdm run scan`, the `width` is added to the metadata json for each image in the library. It is now visible in the template. 

### External tools

Templating will respect whatever's in the json. This means it can be edited by completely external tools. In this case, it is your responsibility that these tools not overwrite existing data.







## All commands

### - `pdm run scan`

Scans the `wallpapers/` folder for new or changed images. Also repopulates old images with new metadata.

### - `pdm run html`

Uses the latest json in `states/` to generate a html site.

### - `pdm run rescan`

Same as scan, but regenerates thumbnails.


