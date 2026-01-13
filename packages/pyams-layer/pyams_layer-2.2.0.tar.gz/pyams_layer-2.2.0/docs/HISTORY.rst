Changelog
=========

2.2.0
-----
 - removed skins with empty label from user's skins vocabulary

2.1.1
-----
 - replaced datetime.utcnow() with datetime.now(timezone.utc)
 - reduced method complexity

2.1.0
-----
 - added deleters to files properties
 - added support for Python 3.11 and 3.12

2.0.0
-----
 - migrated to Pyramid 2.0

1.3.1
-----
 - small updates in resources management
 - *PyAMS_security* package interfaces refactoring
 - added support for Python 3.10

1.3.0
-----
 - renamed "container_class" TALES extension to "skin_container_extension"
 - removed default 'container' class on custom skin container CSS class (default value should
   be handled by layout template)

1.2.2
-----
 - updated translation

1.2.1
-----
 - check base classes before patching BaseSiteRoot

1.2.0
-----
 - added skin management permission
 - added container class to skin properties
 - added default resources adapter

1.1.1
-----
 - packaging mismatch

1.1.0
-----
 - removed support for Python < 3.5

1.0.5
-----
 - updated Gitlab-CI configuration

1.0.4
-----
 - updated Gitlab-CI configuration
 - removed Travis-CI configuration

1.0.3
-----
 - updated "adapter_config" decorator arguments names

1.0.2
-----
 - updated doctests

1.0.1
-----
 - small update in code used to apply a skin

1.0.0
-----
 - initial release
