from gettext import gettext as _

from pulp_glue.common.context import (
    EntityDefinition,
    PluginRequirement,
    PulpContentContext,
    PulpDistributionContext,
    PulpPublicationContext,
    PulpRemoteContext,
    PulpRepositoryContext,
    PulpRepositoryVersionContext,
)


class PulpGemContentContext(PulpContentContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    ENTITY = _("gem")
    ENTITIES = _("gems")
    HREF = "gem_gem_content_href"
    ID_PREFIX = "content_gem_gem"
    CAPABILITIES = {"upload": []}
    NEEDS_PLUGINS = [PluginRequirement("gem")]


class PulpGemDistributionContext(PulpDistributionContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    ENTITY = _("gem distribution")
    ENTITIES = _("gem distributions")
    HREF = "gem_gem_distribution_href"
    ID_PREFIX = "distributions_gem_gem"
    NEEDS_PLUGINS = [PluginRequirement("gem")]
    CAPABILITIES = {"roles": [PluginRequirement("gem", specifier=">=0.4.0.dev")]}

    def preprocess_entity(self, body: EntityDefinition, partial: bool = False) -> EntityDefinition:
        body = super().preprocess_entity(body)
        version = body.pop("version", None)
        if version is not None:
            repository_href = body.pop("repository")
            body["repository_version"] = f"{repository_href}versions/{version}/"
        return body


class PulpGemPublicationContext(PulpPublicationContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    ENTITY = _("gem publication")
    ENTITIES = _("gem publications")
    HREF = "gem_gem_publication_href"
    ID_PREFIX = "publications_gem_gem"
    NEEDS_PLUGINS = [PluginRequirement("gem")]
    CAPABILITIES = {"roles": [PluginRequirement("gem", specifier=">=0.4.0.dev")]}

    def preprocess_entity(self, body: EntityDefinition, partial: bool = False) -> EntityDefinition:
        body = super().preprocess_entity(body, partial=partial)
        version = body.pop("version", None)
        if version is not None:
            repository_href = body.pop("repository")
            body["repository_version"] = f"{repository_href}versions/{version}/"
        return body


class PulpGemRemoteContext(PulpRemoteContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    ENTITY = _("gem remote")
    ENTITIES = _("gem remotes")
    HREF = "gem_gem_remote_href"
    ID_PREFIX = "remotes_gem_gem"
    NEEDS_PLUGINS = [PluginRequirement("gem")]
    CAPABILITIES = {"roles": [PluginRequirement("gem", specifier=">=0.4.0.dev")]}


class PulpGemRepositoryVersionContext(PulpRepositoryVersionContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    HREF = "gem_gem_repository_version_href"
    ID_PREFIX = "repositories_gem_gem_versions"
    NEEDS_PLUGINS = [PluginRequirement("gem")]


class PulpGemRepositoryContext(PulpRepositoryContext):
    PLUGIN = "gem"
    RESOURCE_TYPE = "gem"
    HREF = "gem_gem_repository_href"
    ID_PREFIX = "repositories_gem_gem"
    VERSION_CONTEXT = PulpGemRepositoryVersionContext
    NEEDS_PLUGINS = [PluginRequirement("gem")]
    NULLABLES = PulpRepositoryContext.NULLABLES | {"remote"}
    CAPABILITIES = {"roles": [PluginRequirement("gem", specifier=">=0.4.0.dev")]}
