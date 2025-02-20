# {{SWIKI}}

Make a wiki with backlinking from Markdown fast.

## Installation

* Clone the repo.
* Install requirements with pip: `pip install -r requirements.txt`

## Usage

The Swiki takes in any folder of markdown files and a `frame.html` file to build a flat-file wiki system. Here's what you'll need:

### `_swiki` Directory

Create a directory named `_swiki` in your input directory. This is where you will put the following files.

### Frame

A `frame.html` file in the `_swiki` directory with all of your markdown files. This accepts `{{title}}`, `{{description}}`, and `{{content}}` tags, to fill in the title and description from the page's front matter and the content of the page. A sitemap will also be rendered at `index.html`, so you can link to that, too.

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <meta name="description" content="{{description}}">
    <title>{{title}}</title>
    <style>
        html, body {
          margin: auto;
          max-width: 38rem;
          padding: 2rem;
        }
    </style>
</head>
<body>
    {{content}}

    <footer>
        <a href="index.html">Sitemap</a>
    </footer>
</body>
</html>
```

#### CSS File

Instead of using a `<style>` tag in your frame file for styling, you can also link in a CSS file. If you include a CSS file in the `_swiki` folder, it will be copied over to the root of your output folder. For instance, if you had a file named `styles.css` in your `_swiki` folder, you could replace your `<style>...</style>` tags with a `<link rel="stylesheet" href="./styles.css">`.

### Index/Sitemap

By default, `index.html` will be rendered in your wiki with a title of "Sitemap". The sitemap is organized by the structure of your markdown pages and which folders they reside in (e.g. a file in the root folder will be in a different section than a file in a subfolder). Any page that is linked to but does not yet exist will be in its own section at the bottom of the sitemap as a "stub".

To customize the title, description, and basic content preceding the sitemap, a file named `index.md` can be used.

```markdown
---
title: Website Title
description: This will become the meta description.
---

This will be prepended to the sitemap/index of your wiki.
```

### Fatfile

A `fatfile.html` will be created when making your wiki. This fatfile contains all of your page contents compiled into one huge file for easy searching and stumbling on new content. 

### Pages

The necessary format for your pages are [Markdown](https://spec.commonmark.org/0.29/) files with [YAML/Jekyll front matter](https://jekyllrb.com/docs/front-matter/).

* The front matter currently uses the `title` and `description` fields. Note that these are case sensitive.
* Wiki-style links use `{{double curly braces}}` and are case insensitive. They can be made two ways (note that they reference the *title* in the front matter, not the *filename*):
    * `{{example}}` - Displays the text 'example' and goes to the page whose title is 'example'.
    * `{{shown text|example}}` - Displays the text 'shown text' and goes to the page whose title is 'example'.

#### Ignoring Files and Folders

Any files or folders with a preceding underscore will be ignored in the rendering process.

### Rendering

To render your wiki, run the script with the following syntax:

```bash
python3 swiki.py input_folder output_folder [flags]
```

Flag | Effect
--- | ---
--delete-current-html | Non-recursively delete all existing HTML files in the build directory
--no-fatfile | Do not create [fatfile](#fatfile) on build 

#### Example



```markdown
---
title: Rendering A Page
description: This will become the meta description.
---

This is the content of the {{Markdown}} file. This {{Markdown reference|markdown}} doesn't exist, but the {{page}} will.
```

This would render out five files, all using the frame:

* `index.html` - The index and sitemap, containing the rendered contents of `index.md` and a sitemap of all three above pages.
* `fatfile.html` - The [fatfile](#fatfile).
* `rendering-a-page.html` - The file you see above.
* `markdown.html` - This file exists with only backlinks, as no file with a title of 'Markdown' exists.
* `page.html` - This file exists with only backlinks, for the same reason.

## Future Improvements

- Handle special characters in links and in backlinks. E.g. `{{async/await}}` throws because it resolves to `href="async/await.html"`. Replace `/` with something else, like `:`? Also when a paren etc. is in the title, it just uses that. Should replace with something like the colon.
