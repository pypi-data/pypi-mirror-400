from typing import Any, Self

from clearskies import Column
from clearskies.query import Condition, Query

from clearskies_cortex.models import cortex_catalog_entity


class CortexCatalogEntityDomain(cortex_catalog_entity.CortexCatalogEntity):
    """Model for domain entities."""

    def get_final_query(self) -> Query:
        return (
            self.get_query()
            .add_where(Condition("types=domain"))
            .add_where(Condition("include_nested_fields=team:members"))
            .add_where(Condition("include_owners=true"))
            .add_where(Condition("include_metadata=true"))
            .add_where(Condition("include_hierarchy_fields=groups"))
        )

    def get_top_level_domain(self: Self) -> Self:
        """Get the upper domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            parent = hierarchy.parents[0]
            while parent.parents:
                parent = parent.parents[0]
            return self.as_query().find(f"tag={parent.tag}")
        return self.empty()

    def get_parent(self: Self) -> Self:
        """Get the first domain of this service if set."""
        hierarchy = self.parse_hierarchy()
        if hierarchy.parents:
            container = hierarchy.parents[0]
            return self.as_query().find(f"tag={container.tag}")
        return self.empty()
