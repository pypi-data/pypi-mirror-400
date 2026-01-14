# Abstract

This is a CLI application that provides string replacement with JSON and YAML files.

Regular expressions are not supported.

Japanse document is [here](docs/README_JP.md).

# How To Install

`pip install simple-text-replacer`

## Package Dependencies

The following packages may not work properly if they are not installed:

- [PyYAML](https://pypi.org/project/PyYAML/): Most popular YAML parser for Python.


# Example

my_pet.txt:

```
I have one dog and one cat.
```

replacer.json:

```
{"dog":"wolf", "cat":"lion"}
```

```
> simrep replacer.json my_pet.txt
> cat my_pet.txt
I have one wolf and one lion.
```

## Sytax

`simrep <replacer> <text_file>`

`replacer` is in JSON or YAML format.

`replacer` must be written by key-value like `{original_word: replacement_word}`.

`text_file` can also be specified as a directory, but note that in this case, it will replace all files within that directory and its subdirectories.

If you prefer not to overwrite `text_file`, you can use the `-n` option to output to a new file or directory.


## Options

`[-h|--help]`

Show help message.

`[-v|--version]`

Show version message.

`[-n|--new]　<new file or new directory>`

Ouput as an anther file or directory.
