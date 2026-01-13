<div align="center">

# whatenc

<div>
   <a href="https://pypi.org/project/whatenc/"><img src="https://img.shields.io/pypi/v/whatenc.svg" alt="PyPI"></a>
   <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</div>

<a href="https://https://heyjeremy.vercel.app/blog/classifying-encoded-text"><img src="https://img.shields.io/badge/blog-how%20can%20a%20program%20recognize%20encoded%20text%20without%20decoding%20it%3F-blue" alt="Blog"></a>

Text encoding type classifier.

</div>

`whatenc` is a command-line tool that identifies the encoding or transformation of a given string or file.

The model is trained on text samples from the English, Greek, Russian, Hebrew, and Arabic Wikipedia corpora, chosen to represent a diverse set of writing systems (Latin, Greek, Cyrillic, Hebrew, and Arabic scripts). Each line is encoded using multiple encoding schemes to generate labeled examples.

## How It Works

`whatenc` uses a character-level 1D Convolutional Neural Network trained directly on bigram token sequences. 

Each training sample is represented as:
- bigram of characters, padded to a fixed maximum length
- a true length scalar feature, allowing the network to learn relative string lengths

This neural approach achieves near-perfect classification accuracy after only a few epochs.

### Supported Encodings

`whatenc` currently recognizes the following formats and transformations:

| Category | Encodings |
| :------- | :-------- |
| Base encodings | `base32`, `base64`, `base85`, `hex`, `url` |
| Text ciphers | `morse` |
| Compression | `gzip64` |
| Hash digests | `md5`, `sha1`, `sha224`, `sha256`, `sha384`, `sha512` |

## Installation

You can install `whatenc` using [pipx](https://pypa.github.io/pipx):

```bash
pipx install whatenc
```

## Usage

### API

```python
from whatenc import Classifier

classifier = Classifier()
print(classifier.predict("hello, world!")) # returns: [('plain', 1.0), ('md5', 7.686760500681856e-26), ('base85', 2.864714171264974e-35)]
```

### CLI

```bash
whatenc hello
whatenc samples.txt
```

#### Examples

```bash
[+] input: ZW5jb2RlIHRvIGJhc2U2NCBmb3JtYXQ=
   [~] top guess   = base64
      [=] base64   = 1.000
      [=] base85   = 0.000
      [=] plain    = 0.000

[+] input: hello
   [~] top guess   = plain
      [=] plain    = 1.000
      [=] md5      = 0.000
      [=] base64   = 0.000

[*] loading model
[+] input: האקדמיה ללשון העברית
   [~] top guess   = plain
      [=] plain    = 1.000
      [=] base64   = 0.000
      [=] base85   = 0.000

[*] loading model
[+] input: bfa99df33b137bc8fb5f5407d7e58da8
   [~] top guess   = md5
      [=] md5      = 0.999
      [=] sha1     = 0.001
      [=] sha224   = 0.000
```