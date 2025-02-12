lz-string-python
================

LZ-based compression algorithm for Python 3

Based on the LZ-String javascript library (version 1.4.4)

http://pieroxy.net/blog/pages/lz-string/index.html


Example
-------

```python
>>> from lzstring import LZString
>>> string = "This is my compression test"
>>> compressed = LZString.compressToBase64(string)
>>> LZString.decompressFromBase64(compressed)
```
