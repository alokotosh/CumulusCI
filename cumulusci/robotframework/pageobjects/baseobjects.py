from robot.libraries.BuiltIn import BuiltIn


class BasePage:
    _object_name = None

    def __init__(self, object_name=None):
        if object_name:
            self._object_name = object_name

    def _wait_to_appear(self, timeout=None):
        """This function is called by the keyword 'wait for page object to appear'.
        Custom page objects can override this to verify that the object is visible.
        """
        raise Exception("Unable to wait for this page object")

    def _remove_from_library_search_order(self):
        """Remove the current page object from robot's library search order

        Note: robot doesn't provide a way to completely unload a
        library during execution. However, this at least makes sure that
        all other libraries will have priority over this one.
        """
        order = list(self.builtin.set_library_search_order())
        if self._libname in order:
            order.remove(self._libname)
            self.builtin.set_library_search_order(*order)
            self.builtin.log("new search order: {}".format(order), "DEBUG")

    @property
    def object_name(self):
        object_name = self._object_name

        # the length check is to skip objects from a different namespace
        # like foobar__otherpackageobject__c
        if object_name is not None:
            parts = object_name.split("__")
            if len(parts) == 2 and parts[-1] == "c":
                # get_namespace_prefix already takes care of returning an actual
                # prefix or an empty string depending on whether the package is managed
                object_name = "{}{}".format(
                    self.cumulusci.get_namespace_prefix(), object_name
                )
        return object_name

    @property
    def builtin(self):
        """Returns an instance of robot framework's BuiltIn library"""
        return BuiltIn()

    @property
    def cumulusci(self):
        """Returns the instance of the imported CumulusCI library"""
        return self.builtin.get_library_instance("cumulusci.robotframework.CumulusCI")

    @property
    def salesforce(self):
        """Returns the instance of the imported Salesforce library"""
        return self.builtin.get_library_instance("cumulusci.robotframework.Salesforce")

    @property
    def selenium(self):
        """Returns the instance of the imported SeleniumLibrary library"""
        return self.builtin.get_library_instance("SeleniumLibrary")

    def _get_object(self, **kwargs):
        """Get the object associated with the given keyword arguments.

        This performs a salesforce query. It will raise an exception unless
        exactly one result is returned from the query.
        """
        results = self.salesforce.salesforce_query(self.object_name, **kwargs)
        if len(results) == 0:
            human_friendly_args = ", ".join(
                ["{}={}".format(key, kwargs[key]) for key in kwargs]
            )
            raise Exception(
                "no {} matches {}".format(self.object_name, human_friendly_args)
            )
        elif len(results) > 1:
            raise Exception("Query returned {} objects".format(len(results)))
        else:
            return results[0]

    def log_current_page_object(self):
        """Logs the name of the current page object

        The current page object is also returned as an object
        """
        polib = self.builtin.get_library_instance(
            "cumulusci.robotframework.PageObjects"
        )
        if polib.current_page_object is None:
            # this should not be possible, since this keyword is only available
            # if you've loaded a page object. Still, better safe then sorry.
            self.builtin.log("no page object has been loaded")
            return None
        else:
            pobj = polib.current_page_object

            self.builtin.log(
                "current page object: {}".format(polib.current_page_object)
            )
            return pobj
