import functools

from cumulusci.core.utils import process_bool_arg
from cumulusci.tasks.salesforce import BaseSalesforceMetadataApiTask
from cumulusci.utils import inject_namespace
from cumulusci.utils import strip_namespace
from cumulusci.utils import process_text_in_zipfile
from cumulusci.utils import tokenize_namespace


class BaseRetrieveMetadata(BaseSalesforceMetadataApiTask):
    task_options = {
        "path": {
            "description": "The path to write the retrieved metadata",
            "required": True,
        },
        "unmanaged": {
            "description": "If True, changes namespace_inject to replace tokens with a blank string"
        },
        "namespace_inject": {
            "description": "If set, the namespace tokens in files and filenames are replaced with the namespace's prefix"
        },
        "namespace_strip": {
            "description": "If set, all namespace prefixes for the namespace specified are stripped from files and filenames"
        },
        "namespace_tokenize": {
            "description": "If set, all namespace prefixes for the namespace specified are replaced with tokens for use with namespace_inject"
        },
        "namespaced_org": {
            "description": "If True, the tokens %%%NAMESPACED_ORG%%% and ___NAMESPACED_ORG___ will get replaced with the namespace.  The default is false causing those tokens to get stripped and replaced with an empty string.  Set this if deploying to a namespaced scratch org or packaging org."
        },
    }

    def _run_task(self):
        api = self._get_api()
        src_zip = api()
        self._extract_zip(src_zip)
        self.logger.info(
            "Extracted retrieved metadata into {}".format(self.options["path"])
        )

    def _process_namespace(self, src_zip):
        if self.options.get("namespace_tokenize"):
            src_zip = process_text_in_zipfile(
                src_zip,
                functools.partial(
                    tokenize_namespace,
                    namespace=self.options["namespace_tokenize"],
                    logger=self.logger,
                ),
            )
        if self.options.get("namespace_inject"):
            src_zip = process_text_in_zipfile(
                src_zip,
                functools.partial(
                    inject_namespace,
                    namespace=self.options["namespace_inject"],
                    managed=not process_bool_arg(self.options.get("unmanaged", True)),
                    namespaced_org=process_bool_arg(
                        self.options.get("namespaced_org", False)
                    ),
                    logger=self.logger,
                ),
            )
        if self.options.get("namespace_strip"):
            src_zip = process_text_in_zipfile(
                src_zip,
                functools.partial(
                    strip_namespace,
                    namespace=self.options["namespace_strip"],
                    logger=self.logger,
                ),
            )
        return src_zip

    def _extract_zip(self, src_zip):
        src_zip = self._process_namespace(src_zip)
        src_zip.extractall(self.options["path"])
