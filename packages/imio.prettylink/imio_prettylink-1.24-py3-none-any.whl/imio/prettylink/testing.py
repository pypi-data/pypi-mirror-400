# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from imio.helpers import HAS_PLONE_6_AND_MORE
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing import z2
from zope.component import getUtility

import imio.prettylink
import unittest


class PloneWithPrettyLinkLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=imio.prettylink, name="testing.zcml")
        z2.installProduct(app, "imio.prettylink")

    def setUpPloneSite(self, portal):
        """Set up Plone."""

        if HAS_PLONE_6_AND_MORE:
            fti = getUtility(IDexterityFTI, name="Folder")
            behaviors = list(fti.behaviors)
            locking_behavior = "plone.app.lockingbehavior.behaviors.ILocking"
            if locking_behavior not in behaviors:
                behaviors.append(locking_behavior)
                fti.behaviors = tuple(behaviors)

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        folder_id = portal.invokeFactory("Folder", "folder", title="Folder")
        folder_id2 = portal.invokeFactory("Folder", "folder2", title="Folder2")
        portal[folder_id].reindexObject()
        portal[folder_id2].reindexObject()

        # Commit so that the test browser sees these objects
        import transaction

        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, "imio.prettylink")


FIXTURE = PloneWithPrettyLinkLayer(name="FIXTURE")


INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


ACCEPTANCE = FunctionalTesting(bases=(FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE), name="ACCEPTANCE")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer["portal"]
        self.folder = self.portal.folder
        self.folder2 = self.portal.folder2
        self.catalog = self.portal.portal_catalog
        self.maxDiff = None
