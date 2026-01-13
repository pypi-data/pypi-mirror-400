Changelog
=========

2.1.0
-----
 - added automatic lazy loading to pictures

2.0.6
-----
 - updated Gitlab-CI for Python 3.11 and 3.12

2.0.5
-----
 - added check on file content-type to display editor action

2.0.4
-----
 - handle files without filename when getting thumbnails
 - replaced datetime.utcnow() with datetime.now(timezone.utc)

2.0.3
-----
 - added thumbnail ID in file input widget template

2.0.2
-----
 - added margin on content-type label in file input widget

2.0.1
-----
 - updated modal forms title

2.0.0
-----
 - upgraded to Pyramid 2.0

1.4.5
-----
 - renamed doctests interfaces and classes for last PyAMS_skin version
 - get Bootstrap devices icons from PyAMS_skin package
 - added support for Python 3.11

1.4.4
-----
 - small error in package requirements

1.4.3
-----
 - set widget as deletable if widget or field is not required
 - updated image preview template

1.4.2
-----
 - updated file widgets templates

1.4.1
-----
 - packaging version issue

1.4.0
-----
 - added support for Python 3.10
 - moved TALES extensions from *PyAMS_file* package

1.3.0
-----
 - added image preview

1.2.1
-----
 - added file modifier form mixin class to handle buttons selection in forms in display mode
 - updated language getter attribute in I18n file widget

1.2.0
-----
 - added base class for responsive selections forms
 - added frame border in images selection forms
 - updated order of selections forms actions

1.1.2
-----
 - added missing "context" argument to permission check

1.1.1
-----
 - packaging mismatch...

1.1.0
-----
 - removed support for Python < 3.7
 - added image size in crop and selection templates

1.0.2
-----
 - updated Gitlab-CI configuration
 - removed Travis-CI configuration

1.0.1
-----
 - updated "required" attribute of file input widgets

1.0.0
-----
 - initial release
