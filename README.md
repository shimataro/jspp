jspp
======

C-like JavaScript Preprocessor.
It can combine multiple JavaScript files into one easily.

## Requires

* [Python](https://www.python.org/) (2.7 or 3.2 or 3.3 or 3.4)

## How to use

### `//#include "filename"` will be replaced with the target filename.

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

### `//#if(n)def SYMBOL` - `//#endif` will remain if `SYMBOL` is (not) defined by `-d` option.

base.js
```js
a = 1;
//#ifdef ABC
b = 2;
//#endif
c = 3;
```

python jspp.py \<base.js
```js
a = 1;
c = 3;
```

python jspp.py \<base.js -d ABC
```js
a = 1;
b = 2;
c = 3;
```

## Command line options

* `-s`, `--semicolon`

Add semicolon after include-file.

* `-d <symbol>`, `--define <symbol>`

Define symbol for `//#ifdef` or `//#ifndef`.

* `-i <input-filename>`, `--input <input-filename>`

Specify input filename.
If omitted, stdin will be used.

* `-o <output-filename>`, `--output <output-filename>`

Specify output filename.
If omitted, stdout will be used.
