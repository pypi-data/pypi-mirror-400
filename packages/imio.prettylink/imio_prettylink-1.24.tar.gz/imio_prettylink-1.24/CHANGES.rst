Changelog
=========

1.24 (2026-01-05)
-----------------

- Addd Plone 6.1 compatibility.
  [chris-adam]
- Make sure `contentIcon` title HTML attribute contains translated version
  of portal_type's title.
  [gbastien]

1.23 (2025-06-06)
-----------------

- Fixed tag title displaying `&apos;` because `html.escape` was done after
  replacing `'` by `&apos;`, now quote management is done after `html.escape`.
  [gbastien]

1.22 (2024-02-08)
-----------------

- When displaying `contentIcon`, use `typeInfo.Title` method instead translating
  the `typeInfo.title` as `typeInfo.Title` manages various case where title is
  `unicode`, `string` or else.
  [gbastien]

1.21 (2023-08-24)
-----------------

- Adapted call to `imio.helpers.cache.obj_modified` as parameter `asstring=False`
  was removed, we just use the default result type that is `float`.
  [gbastien]

1.20 (2022-06-14)
-----------------

- Escape link content to avoid malicious behaviour.
  [gbastien]

1.19 (2022-01-12)
-----------------

- Used now `imio.helpers.cache.obj_modified` in `getLink_cachekey` to include
  annotation change in modification date.
  [sgeulette]
- Updated git fetch url
  [sgeulette]

1.18 (2021-03-08)
-----------------

- Improve check for file when adding `@@download` in url.
  [laz, boulch]

1.17 (2020-10-06)
-----------------

- Set icons `<img>` tag `width=16px` and `height=16px` to make `tooltipster`
  happy (computed area to display depends on displayed content).
  [gbaastien]

1.16 (2020-01-10)
-----------------

- While generating not viewable URL, avoid double blank before tag title.
  [gbastien]
- Adapted `PrettyLinkAdapter.CSSClasses` to manage `<a>` tag CSS classes and
  `<span>` tag CSS classes. `additionalCSSClasses` are set on the `<a>` tag.
  [gbastien]

1.15 (2019-11-26)
-----------------

- Removed `unittest2`.
  [gbastien]
- Moved the state related CSS class from the `<a>/<div>` tag to the `<span>`
  inner tag, this way it is easier to define CSS compatible for
  `imio.prettylink` and `imio.history`.
  [gbastien]

1.14 (2019-05-16)
-----------------

- Use context.UID instead context in ram.cache cachekey.
  [gbastien]
- Moved rendering link HTML pattern to the link_pattern so it can be changed.
  [gbastien]

1.13 (2019-01-31)
-----------------

- Fixed `getLink` cachekey to use `SERVER_URL` instead `ACTUAL_URL` or value is
  computed depending on current URL and it leads to be computed on several
  places (dashboard, view, ...).  What we need is just to compute if application
  is accessed thru different portal URL.
  [gbastien]

1.12 (2018-08-22)
-----------------

- Small fixes, `isort`, do not compute `icons_tag` at 2 places and
  `self.notViewableHelpMessage` is always defined.
  [gbastien]

1.11 (2018-07-24)
-----------------

- Use `self.context.wl_isLocked()` to show locking icon so it does not break
  on non lockable objects.
  [gbastien]
- Added boolean `display_tag_title` parameter.
  [sgeulette]

1.10 (2018-01-06)
-----------------

- Handle icon path correctly.
  [sgeulette]

1.9 (2017-02-17)
----------------

- Do simplify link to file the download by just appending the @@download to
  the URL, this is enough if current context has a primary field.
  [gbastien]

1.8 (2017-02-13)
----------------

- Take `ACTUAL_URL` stored in the REQUEST into account in the `getLink` caching
  cachekey to manage the fact that the URL to the element changed.  This can
  be the case when accessing element thru different domains or if a parent
  of the element was renamed.
  [gbastien]

1.7 (2017-02-02)
----------------

- Do not break in `PrettyLinkAdapter.getLink_cachekey` if context does not have
  a workflow.
  [gbastien]

1.6 (2017-02-01)
----------------

- Added caching for `PrettyLinkAdapter.getLink`, the cachekey returns context,
  modified, is_locked, review_state and every parameters defined in
  `PrettyLinkAdapter.__init__`.
  [gbastien]
- Moved link computation from `PrettyLinkAdapter.getLink` that is now a cached
  method to `PrettyLinkAdapter._getLink` so it is possible to call it directly
  without caching or to override it.
  [gbastien]
- Finalized testing configuration to be able to test the getLink caching.
  [gbastien]

1.5 (2017-01-25)
----------------

- Added submethod _get_url that does the url computation.
  Additionally it manages the fact that context is a Dexterity file and
  append relevant part to the url (/@@download/...).
  [gbastien]
- Do not break if icon name contains special characters.
  [gbastien]

1.4 (2016-08-17)
----------------

- Added CSS class 'no_access' to <span> "can_not_access_this_element"
  in addition to class 'discreet' so it may be customized if necessary.
  [gbastien]
- Initialize the 'title' attribute with contentValue, this way if a
  content is cropped to be displayed (maxLength=...), the complete content
  is displayed on hover.
  [gbastien]

1.3 (2016-04-20)
----------------

- Make sure quotes used in title are not breaking formatted strings,
  we escape it by replacing quotes by it's HTML entity &#39;
  [gbastien]

1.2 (2016-02-16)
----------------

- If 'isViewable' is True (default), check that current user have
  'View' on the linked element, if it is forced to False, leave it False.
  This way, 'View' check to linked element is managed by imio.prettylink.
  [gbastien]

1.1 (2015-11-13)
----------------

- When using 'showColors', do not fail if element has no workflow.
  [gbastien]
- Makes 'showContentIcon' work, fixed several bugs.
  [gbastien]

1.0 (2015-07-14)
----------------

- Initial release.
  [gbastien]
