jspp
======

C-like JavaScript Preprocessor Parser.
It enables to include other file into JavaScript file, like C preprocessor `#include`.
And can combine multiple JavaScript files into one easily.

## Requires

* [Python](https://www.python.org/) (2.7 or 3.2 or 3.3 or 3.4)

## How to use

`//#include "filename"` will be replaced with the target filename.

base.js
```js
a = 1;
//#include "other.js"
b = 2;
```

other.js
```js
x = 1;
y = 2;
```

python jspp.py \<base.js
```js
a = 1;
x = 1;
y = 2;
b = 2;
```

## Command line options

* `-i <input-filename>`, `--input <input-filename>`

Specify input filename.
If omitted, stdin will be used.

* `-o <output-filename>`, `--output <output-filename>`

Specify output filename.
If omitted, stdout will be used.
