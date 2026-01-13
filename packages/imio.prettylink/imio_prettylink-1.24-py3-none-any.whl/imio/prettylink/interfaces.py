# -*- coding: utf-8 -*-

from zope.interface import Interface


class IPrettyLink(Interface):
    """ """

    def getLink(self):
        """Returns complete link to the element."""

    def CSSClasses(self):
        """Manage CSS classes to apply to the link.
        It depends on :
        - additionalCSSClasses : some arbitrary classes you can define;
        - showColors : will display a colored link depending on workflow state;
        - showContentIcon : will apply the class that displays the content icon."""

    def _icons(self):
        """Returns icons to prepend to the link."""

    def _leadingIcons(self):
        """Returns icons to prepend to icons returned by _icons."""

    def _trailingIcons(self):
        """Returns icons to append to icons returned by _icons."""
