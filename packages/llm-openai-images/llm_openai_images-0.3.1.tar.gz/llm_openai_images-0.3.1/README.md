# llm-openai-images

[![PyPI](https://img.shields.io/pypi/v/llm-openai-images.svg)](https://pypi.org/project/llm-openai-images/)

An [LLM](https://llm.datasette.io/) plugin providing access to OpenAI's `gpt-image-1.5` and Google's Nano Banana models for image generation and editing.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-openai-images
```

## API Key Setup

You will need API keys for the providers you want to use.

OpenAI:

```bash
llm keys set openai
```
Enter your key when prompted. You can obtain a key from the [OpenAI Platform](https://platform.openai.com/api-keys).

Google (Gemini API):

```bash
llm keys set gemini
```

Enter your key when prompted. You can obtain a key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Output Files

The plugin writes images to files and prints the output path. By default, files are written to the current working directory using this naming scheme:

```
<model>_<timestamp>.png
```

To override the output path, use `-o output`:

```bash
llm -m openai/gpt-image-1.5 "Prompt..." -o output path/to/file.png
```

## Usage

This plugin adds the following models to LLM:

- `openai/gpt-image-1.5`
- `google/nano-banana`
- `google/nano-banana-pro`

### Basic Image Generation

To generate an image from a text prompt:

```bash
llm -m openai/gpt-image-1.5 "A cat wearing sunglasses, riding a skateboard"
```

### Generation Options

You can control the image size and quality using options (`-o`):

*   `-o size <value>`: Set the image dimensions.
    *   `square` (default): 1024x1024
    *   `portrait`: 1024x1536
    *   `landscape`: 1536x1024
*   `-o quality <value>`: Set the image quality/detail.
    *   `high`: ~$0.26
    *   `medium` (default): ~$0.06
    *   `low`: ~$0.015

These options apply to `openai/gpt-image-1.5` only. Google Nano Banana models currently ignore them.

For Google Nano Banana models, you can set:

*   `-o aspect_ratio <value>`: Set the image aspect ratio (default: `1:1`).
    *   `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`

Example with options:

```bash
llm -m openai/gpt-image-1.5 "Impressionist painting of a harbor at sunset" \
  -o size landscape -o quality high \
  -o output harbor_sunset_hd_landscape.png
```

### Editing an Image

To edit an existing image, provide the image file as an attachment using the `-a` or `--attach` flag. The prompt should describe the desired *changes* or additions to the image.

```bash
# First, generate an image or use an existing one (e.g., cat_skateboard.png from above)

# Now, edit it:
llm -m openai/gpt-image-1.5 "Add a small blue bird perched on the cat's head" \
  -a cat_skateboard.png \
  -o output cat_skateboard_with_bird.png
```

### Combining Multiple Images

```bash
llm -m openai/gpt-image-1.5 "A photo of me dressed in these pants and top" \
  -a maison-martin-margiela-ss16-blouse.jpg \
  -a dior-homme-19cm-mij.jpg \
  -a me.jpg \
  -o output my_fabulous_self.png
```

### Nano Banana (Google) Examples

```bash
llm -m google/nano-banana "A kitten with prominent purple-and-green fur."
```

```bash
llm -m google/nano-banana-pro "A cinematic portrait of a hummingbird" \
  -o output hummingbird.png
```

## Development

To set up this plugin locally, first checkout the code. Then install it in editable mode:

```bash
cd llm-openai-images
llm install -e .
```

See the [LLM plugin documentation](https://llm.datasette.io/en/stable/plugins/) for more details on plugin development.
