
# test not used now....

import sgtk
HookBaseClass = sgtk.get_hook_baseclass()

class Actions(HookBaseClass):

    def list_actions(self, sg_publish_data):
        '''
        Given some Shotgun publish data, return a list of
        actions that can be performed

        :param sg_publish_data: Dictionary of publish data from Shotgun
        :returns: List of action strings
        '''
        # The base implementation implements an action to show
        # the item in Shotgun
        return ["show_in_sg"]

    def run_action(self, action, sg_publish_data):
        '''
        Execute the given action

        :param action: name of action. One of the items returned by list_actions.
        :param sg_publish_data: Dictionary of publish data from Shotgun
        '''
        if action == "show_in_sg":

            url = "%s/detail/%s/%d" % (
                self.parent.shotgun.base_url,
                sg_publish_data["type"],
                sg_publish_data["id"]
                )
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
