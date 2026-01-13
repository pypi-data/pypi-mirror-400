# -*- coding: utf-8 -*-
from imio.helpers.cache import obj_modified
from plone import api
from plone.memoize import ram
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.i18n import translate
from zope.i18nmessageid import Message

import html


try:
    from plone.base.utils import base_hasattr
    from plone.base.utils import safe_text
except ImportError:
    from Products.CMFPlone.utils import base_hasattr
    from Products.CMFPlone.utils import safe_unicode as safe_text


class PrettyLinkAdapter(object):
    """Adapter that manage rendering the pretty link."""

    def __init__(
        self,
        context,
        showColors=True,
        showIcons=True,
        showContentIcon=False,
        showLockedIcon=True,
        contentValue="",
        display_tag_title=True,
        tag_title="",
        maxLength=0,
        target="_self",
        appendToUrl="",
        additionalCSSClasses=[],
        isViewable=True,
        link_pattern=u"<div class='pretty_link'{0}>{1}<span class='pretty_link_content{2}'>{3}</span></div>",
        **kwargs
    ):
        self.context = context
        self.request = self.context.REQUEST
        self.portal_url = api.portal.get().absolute_url()
        # we set parameters in the init so it it reusable across every methods
        self.showColors = showColors
        self.showIcons = showIcons
        self.showContentIcon = showContentIcon
        self.showLockedIcon = showLockedIcon
        # value to use for the link, if not given, object's title will be used
        self.contentValue = contentValue
        # arbitrary tag_title
        self.tag_title = tag_title
        self.display_tag_title = display_tag_title
        # truncate link content to given maxLength if any
        self.maxLength = maxLength
        # target of the link : _blank, _self, ...
        self.target = target
        # append arbitrary to the rendered URL
        self.appendToUrl = appendToUrl
        # arbitrary css classes
        self.additionalCSSClasses = additionalCSSClasses
        self.kwargs = kwargs
        # we also manage the fact that we want to display an element that is
        # actually not reachable by current user...  In this case, we display
        # a <div> to the element with a help message...
        self.isViewable = isViewable
        # we may force isViewable to False even if user has the 'View' permission
        # on it, but if isViewable is True, we check if target is really viewable
        if isViewable:
            if not _checkPermission(View, self.context):
                self.isViewable = False
        self.notViewableHelpMessage = translate(
            "can_not_access_this_element",
            domain="imio.prettylink",
            context=self.request,
            default=u"<span class='discreet no_access'>(You can not access this element)</span>",
        )
        self.link_pattern = link_pattern

    def getLink_cachekey(method, self):
        """cachekey method for self.getLink."""
        is_locked = self._show_lock_icon()
        review_state = api.content.get_state(self.context, None)
        server_url = self.request.get("SERVER_URL", None)
        # cache by context, until modified, is_locked, state changed or server_url is different
        # + every parameters passed in __init__
        return (
            self.context.UID(),
            obj_modified(self.context, asdatetime=False),
            is_locked,
            review_state,
            server_url,
            self.showColors,
            self.showIcons,
            self.showContentIcon,
            self.showLockedIcon,
            self.contentValue,
            self.tag_title,
            self.display_tag_title,
            self.maxLength,
            self.target,
            self.appendToUrl,
            self.additionalCSSClasses,
            self.isViewable,
            self.kwargs,
        )

    @ram.cache(getLink_cachekey)
    def getLink(self):
        """See docstring in interfaces.py."""
        return self._getLink()

    def _getLink(self):
        """Private method that does the link computation without the cachekey,
        this is done so it is possible to override the cachekey."""
        completeContent = safe_text(self.contentValue or self.context.Title())
        content = completeContent
        if self.maxLength:
            plone_view = self.context.restrictedTraverse("@@plone")
            ellipsis = self.kwargs.get("ellipsis", "...")
            content = plone_view.cropText(completeContent, self.maxLength, ellipsis)
        icons = self.showIcons and self._icons() or ""
        title = safe_text(self.tag_title or completeContent)
        icons_tag = icons and u"<span class='pretty_link_icons'>{0}</span>".format(icons) or ""
        # as link is rendered using "structure", escape various texts
        content = html.escape(content)
        title = html.escape(title).replace("'", "&apos;")
        self.target = html.escape(self.target)
        if self.isViewable:
            url = self._get_url()
            css_classes = self.CSSClasses()
            return (
                u"<a class='pretty_link{0}'{1} href='{2}' target='{3}'>{4}"
                u"<span class='pretty_link_content{5}'>{6}</span></a>".format(
                    css_classes.get("a"),
                    self.display_tag_title and u" title='{0}'".format(title) or "",
                    url,
                    self.target,
                    icons_tag,
                    css_classes.get("span"),
                    safe_text(content),
                )
            )
        else:
            # append the notViewableHelpMessage
            content = u"{0} {1}".format(content, self.notViewableHelpMessage)
            return self.link_pattern.format(
                self.display_tag_title and u" title='{0}'".format(title) or "",
                icons_tag,
                self.CSSClasses()["span"],
                safe_text(content),
            )

    def _get_url(self):
        """Compute the url to the content."""
        url = self.context.absolute_url()
        # add @@download to url if necessary, it is the case for dexterity files
        try:
            primary_field_info = IPrimaryFieldInfo(self.context)
            primary_field = getattr(self.context, primary_field_info.fieldname)
            if base_hasattr(primary_field, "filename"):
                url = u"{0}/@@download".format(url)
        except TypeError:
            pass
        return url + self.appendToUrl

    def CSSClasses(self):
        """See docstring in interfaces.py."""
        css_classes = {"a": [], "span": []}
        css_classes["a"] += list(self.additionalCSSClasses)
        if self.showColors:
            wft = api.portal.get_tool("portal_workflow")
            try:
                css_classes["span"].append("state-{0}".format(wft.getInfoFor(self.context, "review_state")))
            except WorkflowException:
                # if self.context does not have a workflow, just pass
                pass
        # in case the contentIcon must be shown and it the icon
        # is shown by the generated contentttype-xxx class
        if self.showContentIcon:
            type_info = api.portal.get_tool("portal_types")[self.context.portal_type]
            if not type_info.icon_expr:
                css_classes["span"].append("contenttype-{0}".format(type_info.getId()))
        if css_classes["a"]:
            css_classes["a"].insert(0, "")
        css_classes["a"] = " ".join(css_classes["a"])
        if css_classes["span"]:
            css_classes["span"].insert(0, "")
        css_classes["span"] = " ".join(css_classes["span"])
        return css_classes

    def _icons(self, **kwargs):
        """See docstring in interfaces.py."""
        icons = []

        # manage icons we want to be displayed before managed icons
        icons = icons + self._leadingIcons()

        # display the icon that shows that an element is currently locked by another user
        if self._show_lock_icon():
            icons.append(
                (
                    "lock_icon.png",
                    translate("Locked", domain="plone", context=self.request),
                )
            )

        # in case the contentIcon must be shown, the icon url is defined on the type_info
        if self.showContentIcon:
            type_info = api.portal.get_tool("portal_types")[self.context.portal_type]
            if type_info.icon_expr:
                # we assume that stored icon_expr is like string:${portal_url}/myContentIcon.png
                # or like string:${portal_url}/++resource++package/myContentIcon.png
                # we skip first part
                contentIcon = "/".join(type_info.icon_expr.split("/")[1:])
                # title will return an i18n msgid or a string if portal_type
                # does not have a i18n_domain
                type_info_title = type_info.Title()
                if isinstance(type_info_title, Message):
                    type_info_title = translate(type_info_title, context=self.request)
                icons.append((contentIcon, type_info_title))

        # manage icons we want to be displayed after managed icons
        icons = icons + self._trailingIcons()
        return " ".join(
            [
                u"<img title='{0}' src='{1}' style=\"width: 16px; height: 16px;\" />".format(
                    safe_text(icon[1]).replace("'", "&apos;"),
                    u"{0}/{1}".format(self.portal_url, icon[0]),
                )
                for icon in icons
            ]
        )

    def _show_lock_icon(self):
        """ """
        return self.showLockedIcon and self.context.wl_isLocked()

    def _leadingIcons(self):
        """See docstring in interfaces.py."""
        return []

    def _trailingIcons(self):
        """See docstring in interfaces.py."""
        return []
