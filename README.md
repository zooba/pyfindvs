pyfindvs
========

Python client library for locating Visual Studio 2017.

Usage
=====

The basic functions are `findall`, `findwithall` and `findwithany`.

Calling `findall` will return a (potentially cached) list of currently installed copies of
Visual Studio 2017. Each list item is a `VisualStudioInstance` object with attributes for
`name`, `version`, `version_info` (numeric parts of `version` as a tuple), `path` and
`packages` (a set of the installed components).

Calling `findwithall` or `findwithany` will only return instances of Visual Studio where
all/any of the specified package names are installed.

For example:

```
>>> pyfindvs.findall()
[<VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\Community>, 
 <VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]

>>> pyfindvs.findwithall('Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                         'Microsoft.VisualStudio.Component.Windows10SDK.10586')
[<VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]

>>> pyfindvs.findwithany('Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                         'Microsoft.VisualStudio.Component.Windows10SDK.10586')
[<VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\Community>, 
 <VisualStudioInstance at C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools>]
```
