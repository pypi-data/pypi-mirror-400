# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_6_AND_MORE
from imio.prettylink.interfaces import IPrettyLink
from imio.prettylink.testing import IntegrationTestCase
from plone import api
from plone.locking.interfaces import ILockable
from plone.memoize.interfaces import ICacheChooser
from zope.component import getUtility


class TestPrettyLinkAdapter(IntegrationTestCase):
    def invalidate_cache(self):
        cache = getUtility(ICacheChooser)("imio.prettylink.adapters.getLink")
        cache.ramcache.invalidate("imio.prettylink.adapters.getLink")

    def test_getLink_caching_modified(self):
        """Cache is invalidated when modified."""
        self.assertEqual(
            IPrettyLink(self.folder).getLink(),
            u"<a class='pretty_link' title='Folder' href='http://nohost/plone/folder' "
            u"target='_self'><span class='pretty_link_content state-private'>Folder</span></a>",
        )
        # change Title and do not notify modified
        self.folder.setTitle("Folder other title")
        self.assertTrue(" title='Folder' " in IPrettyLink(self.folder).getLink())
        # notify modified so cache is invalidated
        self.folder.notifyModified()
        self.assertTrue(" title='Folder other title' " in IPrettyLink(self.folder).getLink())

    def test_getLink_caching_context(self):
        """Cached by context so getLink on self.folder2 is correct."""
        self.assertEqual(
            IPrettyLink(self.folder).getLink(),
            u"<a class='pretty_link' title='Folder' href='http://nohost/plone/folder' "
            u"target='_self'><span class='pretty_link_content state-private'>Folder</span></a>",
        )
        self.assertEqual(
            IPrettyLink(self.folder2).getLink(),
            u"<a class='pretty_link' title='Folder2' href='http://nohost/plone/folder2' "
            u"target='_self'><span class='pretty_link_content state-private'>Folder2</span></a>",
        )

    def test_getLink_caching_locking(self):
        """Cache takes locking into account."""
        ILockable(self.folder).lock()
        self.assertTrue(u"lock_icon.png" in IPrettyLink(self.folder).getLink())
        ILockable(self.folder).unlock()
        self.assertFalse(u"lock_icon.png" in IPrettyLink(self.folder).getLink())

    def test_getLink_caching_review_state(self):
        """Cache takes 'review_state' into account."""
        self.assertTrue(u"<span class='pretty_link_content state-private'>" in IPrettyLink(self.folder).getLink())
        api.content.transition(self.folder, "publish")
        self.assertTrue(u"<span class='pretty_link_content state-published'>" in IPrettyLink(self.folder).getLink())

    def test_getLink_server_url(self):
        """Cache takes portal url (SERVER_URL) into account,
        this could change when accessing the portal thru different domains or so."""
        portal = api.portal.get()
        portal_url = portal.absolute_url()
        ANOTHER_HOST = "http://another_host"
        self.assertTrue(portal_url in IPrettyLink(self.folder).getLink())
        self.assertFalse(ANOTHER_HOST in IPrettyLink(self.folder).getLink())
        self.portal.REQUEST["SERVER_URL"] = ANOTHER_HOST
        self.assertTrue(ANOTHER_HOST in IPrettyLink(self.folder).getLink())

    def test_getLink_caching_showColors(self):
        """Cache takes the 'showColors' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertTrue(adapted.showColors)
        self.assertTrue(u"<span class='pretty_link_content state-private'" in adapted.getLink())
        adapted.showColors = False
        self.assertFalse(u"<span class='pretty_link_content state-private'" in adapted.getLink())

    def test_getLink_caching_showIcons(self):
        """Cache takes the 'showIcons' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertTrue(adapted.showIcons)
        ILockable(self.folder).lock()
        self.assertTrue(u"lock_icon.png" in adapted.getLink())
        adapted.showIcons = False
        self.assertFalse(u"lock_icon.png" in adapted.getLink())

    def test_getLink_caching_showContentIcon(self):
        """Cache takes the 'showContentIcon' parameter into account."""
        if HAS_PLONE_6_AND_MORE:
            pretty_link_marker = "<img title='Folder' src='http://nohost/plone/folder' style=\"width: 16px; height: 16px;\" /></span><span class='pretty_link_content state-private'>Folder</span>"
        else:
            pretty_link_marker = u"contenttype-Folder"
        adapted = IPrettyLink(self.folder)
        self.assertTrue(adapted.showIcons)
        self.assertFalse(adapted.showContentIcon)
        self.assertFalse(pretty_link_marker in adapted.getLink())
        adapted.showContentIcon = True
        self.assertTrue(pretty_link_marker in adapted.getLink())
        typeInfo = api.portal.get_tool("portal_types")["Folder"]
        # setting an icon
        self.invalidate_cache()
        typeInfo.icon_expr = "string:${portal_url}/myContentIcon.png"
        self.assertFalse(pretty_link_marker in adapted.getLink())
        self.assertTrue(u"plone/myContentIcon.png" in adapted.getLink())
        self.invalidate_cache()
        typeInfo.icon_expr = "string:${portal_url}/++resource++package/myContentIcon.png"
        self.assertFalse(pretty_link_marker in adapted.getLink())
        self.assertTrue(u"plone/++resource++package/myContentIcon.png" in adapted.getLink())
        self.invalidate_cache()
        # when typeInfo's title contains special characters
        # this does not work with AT without a monkey patch
        if HAS_PLONE_6_AND_MORE:
            typeInfo.title = 'h\xc3\xa9h\xc3\xa9'
            self.assertTrue(typeInfo.title in adapted.getLink())

    def test_getLink_caching_showLockedIcon(self):
        """Cache takes the 'showLockedIcon' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertTrue(adapted.showLockedIcon)
        ILockable(self.folder).lock()
        self.assertTrue(u"lock_icon.png" in adapted.getLink())
        adapted.showLockedIcon = False
        self.assertFalse(u"lock_icon.png" in adapted.getLink())

    def test_getLink_caching_contentValue(self):
        """Cache takes the 'contentValue' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertFalse(adapted.contentValue)
        self.assertTrue(u"<span class='pretty_link_content state-private'>Folder</span>" in adapted.getLink())
        adapted.contentValue = "Content value"
        self.assertFalse(u"<span class='pretty_link_content state-private'>Folder</span>" in adapted.getLink())
        self.assertTrue(u"<span class='pretty_link_content state-private'>Content value</span>" in adapted.getLink())

    def test_getLink_caching_tag_title(self):
        """Cache takes the 'tag_title' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertFalse(adapted.tag_title)
        self.assertTrue(u" title='Folder' " in adapted.getLink())
        adapted.tag_title = "Tag title"
        self.assertFalse(u" title='Folder' " in adapted.getLink())
        self.assertTrue(u" title='Tag title' " in adapted.getLink())

    def test_getLink_caching_maxLength(self):
        """Cache takes the 'maxLength' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertFalse(adapted.maxLength)
        self.assertTrue(u"<span class='pretty_link_content state-private'>Folder</span>" in adapted.getLink())
        adapted.maxLength = 2
        self.assertFalse(u"<span class='pretty_link_content state-private'>Folder</span>" in adapted.getLink())
        self.assertTrue(u"<span class='pretty_link_content state-private'>Fo...</span>" in adapted.getLink())

    def test_getLink_caching_target(self):
        """Cache takes the 'target' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertEqual(adapted.target, "_self")
        self.assertTrue(u" target='_self'>" in adapted.getLink())
        adapted.target = "_blank"
        self.assertFalse(u" target='_self'>" in adapted.getLink())
        self.assertTrue(u" target='_blank'>" in adapted.getLink())

    def test_getLink_caching_appendToUrl(self):
        """Cache takes the 'appendToUrl' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertFalse(adapted.appendToUrl)
        self.assertTrue(u" href='http://nohost/plone/folder' " in adapted.getLink())
        adapted.appendToUrl = "/@@append_to_url"
        self.assertTrue(u" href='http://nohost/plone/folder/@@append_to_url' " in adapted.getLink())

    def test_getLink_caching_additionalCSSClasses(self):
        """Cache takes the 'additionalCSSClasses' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertFalse(adapted.additionalCSSClasses)
        self.assertTrue(u"<span class='pretty_link_content state-private'>" in adapted.getLink())
        adapted.additionalCSSClasses = ["custom_css_class"]
        # additionalCSSClasses are set on the <a> tag
        # state related CSS class is set on the <span> tag
        self.assertEqual(
            adapted.getLink(),
            u"<a class='pretty_link custom_css_class' title='Folder' "
            u"href='http://nohost/plone/folder' target='_self'>"
            u"<span class='pretty_link_content state-private'>Folder</span></a>",
        )

    def test_getLink_caching_isViewable(self):
        """Cache takes the 'isViewable' parameter into account."""
        adapted = IPrettyLink(self.folder)
        self.assertTrue(adapted.isViewable)
        self.assertFalse(adapted.notViewableHelpMessage in adapted.getLink())
        adapted.isViewable = False
        self.assertTrue(adapted.notViewableHelpMessage in adapted.getLink())

    def test_getLink_caching_kwargs(self):
        """Cache takes the 'kwargs' parameter into account.
        By default it is used together with maxLength to define the ellipsis type."""
        adapted = IPrettyLink(self.folder)
        adapted.maxLength = 2
        self.assertFalse(adapted.kwargs)
        self.assertTrue(u"<span class='pretty_link_content state-private'>Fo...</span>" in adapted.getLink())
        adapted.kwargs["ellipsis"] = " [truncated]"
        self.assertFalse(u"<span class='pretty_link_content state-private'>Fo...</span>" in adapted.getLink())
        self.assertTrue(u"<span class='pretty_link_content state-private'>Fo [truncated]</span>" in adapted.getLink())

    def test_getLink_caching_not_breaking_when_no_workflow(self):
        """Caching also work when element has no workflow."""
        self.portal.portal_workflow.setDefaultChain("")
        no_wf_folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="no_wf_folder",
            title="No WF folder",
        )
        self.assertTrue(IPrettyLink(no_wf_folder).getLink())
        # and caching work, change folder title, link is still the same
        # until notifyModified
        no_wf_folder.setTitle("New title")
        self.assertFalse(no_wf_folder.Title() in IPrettyLink(no_wf_folder).getLink())
        no_wf_folder.notifyModified()
        self.assertTrue(no_wf_folder.Title() in IPrettyLink(no_wf_folder).getLink())

    def test_getLink_link_tooltip(self):
        """title attr is absent if display_tag_title is False."""
        pl = IPrettyLink(self.folder)
        self.assertEqual(
            pl.getLink(),
            u"<a class='pretty_link' title='Folder' href='http://nohost/plone/folder' "
            u"target='_self'><span class='pretty_link_content state-private'>Folder</span></a>",
        )
        pl.display_tag_title = False
        self.assertEqual(
            pl.getLink(),
            u"<a class='pretty_link' href='http://nohost/plone/folder' "
            u"target='_self'><span class='pretty_link_content state-private'>Folder</span></a>",
        )

    def test_getLink_escape_dangerous_characters(self):
        """As link is rendered, make sure we can not embed dangerous things."""
        self.folder.setTitle('Folder"><script>alert(document.domain)</script>')
        pl = IPrettyLink(self.folder)
        self.assertEqual(
            pl.getLink(),
            u"<a class='pretty_link' title='Folder&quot;&gt;&lt;script&gt;alert(document.domain)"
            u"&lt;/script&gt;' href='http://nohost/plone/folder' target='_self'><span "
            u"class='pretty_link_content state-private'>Folder&quot;&gt;&lt;script&gt;alert"
            u"(document.domain)&lt;/script&gt;</span></a>",
        )
        pl.tag_title = "tag_title<>"
        pl.contentValue = "contentValue<>"
        self.assertEqual(
            pl.getLink(),
            u"<a class='pretty_link' title='tag_title&lt;&gt;' href='http://nohost/plone/folder' "
            u"target='_self'><span class='pretty_link_content state-private'>contentValue&lt;&gt;</span></a>",
        )
