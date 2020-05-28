# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

HookBaseClass = sgtk.get_hook_baseclass()


class PostPhaseHook(HookBaseClass):
    """
    This hook defines methods that are executed after each phase of a publish:
    validation, publish, and finalization. Each method receives the publish
    tree instance being used by the publisher, giving full control to further
    curate the publish tree including the publish items and the tasks attached
    to them. See the :class:`PublishTree` documentation for additional details
    on how to traverse the tree and manipulate it.
    """

    # See the developer docs for more information about the methods that can be
    # defined here: https://developer.shotgunsoftware.com/tk-multi-publish2/
    # def post_validate(self):
    # print dir(HookBaseClass)
    
    # CUSTOMIZED --------------------------
    def post_validate(self, publish_tree):

        all_errors = []

        # the publish tree is iterable, so you can easily loop over
        # all items in the tree
        for item in publish_tree:

            # access properties set on the item during the execution of
            # the attached publish plugins
            print 'Item here: ', item
            # if item.properties.validation_failed:
                # all_errors.extend(item.properties.validation_errors)

