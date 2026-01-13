# Hamster Uploader

## Installation

Requires Python 3.13.

Install using `pip install --user jerkup`.

Make sure `PATH` is properly set.

Generate an [API key](https://hamster.is/settings/api) and provide it using the `--api-key` option on first invocation.

## Usage

Upload an image and get the URL:

```
jerkup image.jpg
```

Upload multiple images:

```
jerkup image1.jpg image2.jpg
```

Output to file:

```
jerkup image.jpg --output file.txt
```

Generate BBCode linked thumbnails:

```
jerkup image.jpg --format bbcode-thumbnail-linked
```

## Reference

Use `jerkup --help` to see the full documentation on options and output formats.
