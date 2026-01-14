from abc import abstractmethod, ABC
from collections import defaultdict
from enum import Enum
from typing import Optional, Union

from bb_integrations_lib.gravitate.rita_api import GravitateRitaAPI
from bb_integrations_lib.models.rita.mapping import Map, MappingType, Children, CompositeMapKey
from bb_integrations_lib.secrets import RITACredential
from bb_integrations_lib.util.cache.custom_ttl_cache import CustomAsyncTTLCache


class MappingsNotLoadedException(Exception):
    pass


class FastMapDirection(Enum):
    source_to_grav = 1
    grav_to_source = 2


class FastMapKey:
    """
    A hashable key that can be used to identify mappings quickly if enough properties are known.
    Supports both simple string IDs and composite keys for entity identity (from_id).

    Note: parent_id is always a simple string. Composite keys are for entity identity resolution,
    not for hierarchical relationships. Children mappings only support string identifiers.
    """
    from_id: Union[str, CompositeMapKey]
    type: Optional[MappingType] = None
    parent_id: Optional[str] = None
    direction: FastMapDirection

    def __init__(
        self,
        from_id: Union[str, CompositeMapKey, dict],
        type: MappingType,
        parent_id: Optional[str],
        direction: FastMapDirection
    ):
        # Normalize dict inputs to CompositeMapKey for entity identity
        if isinstance(from_id, dict):
            self.from_id = CompositeMapKey(key=from_id)
        else:
            self.from_id = from_id
        self.type = type
        # parent_id is always a simple string (hierarchy uses string IDs)
        self.parent_id = parent_id
        self.direction = direction

        # Cache normalized values for hash/equality
        self._from_id_normalized = self._normalize_from_id(self.from_id)
        self._parent_id_normalized = self.parent_id or ""

    @staticmethod
    def _normalize_from_id(value: Union[str, CompositeMapKey]) -> str:
        """Convert from_id to hashable string representation."""
        if isinstance(value, CompositeMapKey):
            return value.to_cache_key()
        return value

    def __hash__(self):
        return hash((
            self._from_id_normalized,
            self.type,
            self._parent_id_normalized,
            self.direction.value
        ))

    def __eq__(self, other):
        if not isinstance(other, FastMapKey):
            return False
        return (
            self._from_id_normalized == other._from_id_normalized and
            self.type == other.type and
            self._parent_id_normalized == other._parent_id_normalized and
            self.direction == other.direction
        )

    def __repr__(self):
        type_name = self.type.name if self.type else None
        parent_id_str = self._parent_id_normalized or None
        return f"FastMap<from_id={self._from_id_normalized}, type_name={type_name}, parent_id={parent_id_str}, direction={self.direction.name}>"


class MappingProvider(ABC):
    """An abstract base class for implementing synchronous mapping providers for the Mapper class."""

    def __init__(self):
        pass

    @abstractmethod
    def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        pass


class AsyncMappingProvider(ABC):
    """An abstract base class for implementing asynchronous mapping providers for the Mapper class."""

    def __init__(self):
        pass

    @abstractmethod
    async def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        pass


class MockMappingProvider(MappingProvider):
    """A mapping provider that uses a constant list of mappings, intended for testing."""

    def __init__(self, mappings: list[Map]):
        super().__init__()
        self.mappings = mappings

    def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        """Returns mappings originally passed to init, filtered by source system."""
        return list(filter(lambda m: m.source_system == source_system, self.mappings))


class MockAsyncMappingProvider(AsyncMappingProvider):
    """A mapping provider that uses a constant list of mappings, intended for testing."""

    def __init__(self, mappings: list[Map]):
        super().__init__()
        self.mappings = mappings

    async def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        """Returns mappings originally passed to init, filtered by source system."""
        return list(filter(lambda m: m.source_system == source_system, self.mappings))


class RitaAPIMappingProvider(AsyncMappingProvider):
    """Accesses the RITA API to retrieve mappings, providing them to a Mapper."""

    def __init__(self, rita_client: GravitateRitaAPI):
        super().__init__()
        self.rita_client = rita_client

    async def from_credential(self, credential: RITACredential):
        self.rita_client = GravitateRitaAPI.from_credential(credential)

    async def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        return await self.rita_client.get_mappings_by_source_system(source_system)


class RitaAPICachedMappingProvider(RitaAPIMappingProvider):
    def __init__(
            self,
            rita_client: GravitateRitaAPI,
            ttl_seconds: int = 120
    ):
        super().__init__(rita_client)
        self.ttl_seconds = ttl_seconds
        self.cache: CustomAsyncTTLCache = CustomAsyncTTLCache(verbose=False)

    async def get_mappings_by_source_system(self, source_system: str) -> list[Map]:
        return await self.cache.get_or_set(
            source_system, self.ttl_seconds, super().get_mappings_by_source_system, source_system
        )


class RitaMapperCore(ABC):
    """
    Provides the core logic of mapping lookups. Entirely synchronous; the concrete implementations can use these
    methods directly, and should generally only implement loading mappings.
    """

    def __init__(self):
        self.loaded = False
        self.fast_maps = defaultdict(list)

    def _raise_if_not_loaded(self):
        if not self.loaded:
            raise MappingsNotLoadedException("Mappings used before getting loaded")

    def _load_mappings(self, mappings: list[Map]):
        """
        Load the mappings from mappings into the mapper's internal data structures, making the get_ calls available
        for use. Supports both simple string IDs and composite keys for entity identity.

        Note: parent_id in FastMapKey is always a string. If a parent Map has a composite source_id,
        it's converted to string for hierarchical lookups.
        """

        def _get_identifier(map_obj: Map | Children, direction: FastMapDirection):
            """Extract the appropriate identifier based on a map direction."""
            if direction == FastMapDirection.grav_to_source:
                return map_obj.gravitate_id
            return map_obj.source_id

        def _get_parent_id_str(parent: Map | None, direction: FastMapDirection) -> str | None:
            """Get parent identifier as string (hierarchy always uses string IDs)."""
            if parent is None:
                return None
            parent_id = _get_identifier(parent, direction)
            # Convert composite keys to string for parent_id (hierarchy uses strings)
            if isinstance(parent_id, CompositeMapKey):
                return parent_id.to_cache_key()
            return parent_id

        def _reg_map(map: Map | Children, direction: FastMapDirection, parent: Map | None = None):
            from_id = _get_identifier(map, direction)
            parent_id = _get_parent_id_str(parent, direction)
            map_key = FastMapKey(from_id, map.type, parent_id, direction)
            self.fast_maps[map_key].append(map)

        for direction in FastMapDirection:
            for m in mappings:
                for child in m.children:
                    _reg_map(child, direction, m)
                _reg_map(m, direction, None)

        self.loaded = True

    # noinspection PyUnreachableCode
    def get_mappings(self, from_id: str, direction: FastMapDirection, mapping_type: MappingType,
                     parent_from_id: str | None = None) -> list[Map | Children]:
        """
        Retrieve mappings meeting the criteria. Base method for many of the get_gravitate/source* methods - prefer using
        those for a more expressive syntax.

        :arg str from_id: The original value we're looking to map. If direction is source_to_grav, this matches on the
          source_id field; if direction is grav_to_source, this matches on the gravitate_id field.
        :arg FastMapDirection direction: The direction of the mapping (gravitate->source or source->gravitate).
        :arg MappingType mapping_type: The type of the mapping.
        :arg str | None parent_from_id: The from_id of the child mapping's parent, if searching for a child. To get
          parent mappings instead, use None (the default).
        :raises MappingsNotLoadedException: If mappings have not been loaded yet.
        """
        self._raise_if_not_loaded()
        if mapping_type is not None and not isinstance(mapping_type, MappingType):
            raise TypeError(
                "mapping_type must be of type bb_integrations_lib.models.rita.mapping.MappingType "
                "(check whether you imported the right MappingType)"
            )

        return self.fast_maps.get(FastMapKey(from_id, mapping_type, parent_from_id, direction), [])

    def get_mappings_guaranteed(
            self, from_id: str, direction: FastMapDirection, mapping_type: MappingType,
            parent_from_id: str | None = None
    ) -> list[Map | Children]:
        """Like get_mappings, but additionally raises a KeyError if no mappings are found."""
        self._raise_if_not_loaded()
        mappings = self.get_mappings(from_id, direction, mapping_type, parent_from_id)
        if not mappings:
            from_name = "gravitate" if direction == FastMapDirection.grav_to_source else "source"
            child_slug = f", parent_{from_name}_id='{parent_from_id}'" if parent_from_id else ""
            mapping_type_name = "None" if mapping_type is None else mapping_type.name
            raise KeyError(
                f"No mappings found for {from_name}_id='{from_id}'{child_slug} with type='{mapping_type_name}'"
            )
        return mappings

    def get_single_mapping_guaranteed(
            self, from_id: str, direction: FastMapDirection, mapping_type: MappingType,
            parent_from_id: str | None = None
    ) -> Map | Children:
        """Like get_mappings_guaranteed, but additionally raises a KeyError if more than 1 mapping is found."""
        mappings = self.get_mappings_guaranteed(from_id, direction, mapping_type, parent_from_id)
        if len(mappings) > 1:
            from_name = "gravitate" if direction == FastMapDirection.grav_to_source else "source"
            child_slug = f", parent_{from_name}_id='{parent_from_id}'" if parent_from_id else ""
            raise KeyError(
                f"Too many mappings ({len(mappings)}) for {from_name}_id='{from_id}'{child_slug} "
                f"with type='{mapping_type.name}', expected 1"
            )
        return mappings[0]

    def get_gravitate_parent_id(
        self,
        source_id: str | CompositeMapKey,
        mapping_type: MappingType | None
    ) -> str | CompositeMapKey:
        return self.get_single_mapping_guaranteed(source_id, FastMapDirection.source_to_grav, mapping_type).gravitate_id

    def get_gravitate_child_id(
        self,
        source_parent_id: str,
        source_child_id: str,
        mapping_type: MappingType | None
    ) -> str:
        """
        Get gravitate_id for a child mapping.

        Note: Child lookups use string IDs only. Children mappings don't support composite keys.
        For composite key lookups (without hierarchy), use get_gravitate_id_by_composite().
        """
        return self.get_single_mapping_guaranteed(
            source_child_id, FastMapDirection.source_to_grav, mapping_type, source_parent_id
        ).gravitate_id

    def get_source_parent_id(
        self,
        gravitate_id: str | CompositeMapKey,
        mapping_type: MappingType | None
    ) -> str | CompositeMapKey:
        return self.get_single_mapping_guaranteed(gravitate_id, FastMapDirection.grav_to_source, mapping_type).source_id

    def get_source_child_id(
        self,
        gravitate_parent_id: str,
        gravitate_child_id: str,
        mapping_type: MappingType | None
    ) -> str:
        """
        Get source_id for a child mapping.

        Note: Child lookups use string IDs only. Children mappings don't support composite keys.
        For composite key lookups (without hierarchy), use get_source_id_by_composite().
        """
        return self.get_single_mapping_guaranteed(
            gravitate_child_id, FastMapDirection.grav_to_source, mapping_type, gravitate_parent_id
        ).source_id

    def get_gravitate_parent_ids(
        self,
        source_id: str | CompositeMapKey,
        mapping_type: MappingType | None
    ) -> list[str | CompositeMapKey]:
        return [
            x.gravitate_id for x in
            self.get_mappings_guaranteed(source_id, FastMapDirection.source_to_grav, mapping_type)
        ]

    def get_gravitate_child_ids(
        self,
        source_parent_id: str,
        source_child_id: str,
        mapping_type: MappingType | None
    ) -> list[str]:
        """
        Get all gravitate_ids for child mappings matching the criteria.

        Note: Child lookups use string IDs only. Children mappings don't support composite keys.
        """
        return [
            x.gravitate_id for x in
            self.get_mappings_guaranteed(
                source_child_id, FastMapDirection.source_to_grav, mapping_type, source_parent_id)
        ]

    def get_source_parent_ids(
        self,
        gravitate_id: str | CompositeMapKey,
        mapping_type: MappingType | None
    ) -> list[str | CompositeMapKey]:
        return [
            x.source_id for x in
            self.get_mappings_guaranteed(
                gravitate_id, FastMapDirection.grav_to_source, mapping_type)
        ]

    def get_source_child_ids(
        self,
        gravitate_parent_id: str,
        gravitate_child_id: str,
        mapping_type: MappingType | None
    ) -> list[str]:
        """
        Get all source_ids for child mappings matching the criteria.

        Note: Child lookups use string IDs only. Children mappings don't support composite keys.
        """
        return [
            x.source_id for x in
            self.get_mappings_guaranteed(
                gravitate_child_id, FastMapDirection.grav_to_source, mapping_type, gravitate_parent_id)
        ]

    def get_gravitate_parent_id_str(
        self,
        source_id: str,
        mapping_type: MappingType | None
    ) -> str:
        """Get gravitate_id as string. Raises TypeError if mapping uses composite key."""
        result = self.get_gravitate_parent_id(source_id, mapping_type)
        if isinstance(result, CompositeMapKey):
            raise TypeError(f"Mapping has composite gravitate_id: {result}")
        return result

    def get_source_parent_id_str(
        self,
        gravitate_id: str,
        mapping_type: MappingType | None
    ) -> str:
        """Get source_id as string. Raises TypeError if mapping uses composite key."""
        result = self.get_source_parent_id(gravitate_id, mapping_type)
        if isinstance(result, CompositeMapKey):
            raise TypeError(f"Mapping has composite source_id: {result}")
        return result

    # Composite key lookup methods

    def get_mappings_by_composite(
        self,
        from_key: Union[dict, CompositeMapKey],
        direction: FastMapDirection,
        mapping_type: MappingType | None,
        parent_from_id: Optional[str] = None
    ) -> list[Map | Children]:
        """
        Retrieve mappings using a composite key for entity identity.

        :param from_key: Dict or CompositeMapKey for lookup (entity identity)
        :param direction: Mapping direction
        :param mapping_type: Type of mapping
        :param parent_from_id: Parent identifier (string only - hierarchy uses simple IDs)

        Note: Composite keys are for entity identity, not hierarchy. If looking up children,
        use string parent_from_id. Children mappings don't support composite keys.
        """
        self._raise_if_not_loaded()
        if isinstance(from_key, dict):
            from_key = CompositeMapKey(key=from_key)
        return self.fast_maps.get(
            FastMapKey(from_key, mapping_type, parent_from_id, direction), []
        )

    def get_gravitate_id_by_composite(
        self,
        source_key: Union[dict, CompositeMapKey],
        mapping_type: MappingType | None
    ) -> str | CompositeMapKey:
        """Get gravitate_id using a composite source key."""
        mappings = self.get_mappings_by_composite(
            source_key, FastMapDirection.source_to_grav, mapping_type
        )
        if not mappings:
            raise KeyError(f"No mapping found for composite key: {source_key}")
        if len(mappings) > 1:
            raise KeyError(f"Multiple mappings ({len(mappings)}) found for: {source_key}")
        return mappings[0].gravitate_id

    def get_source_id_by_composite(
        self,
        gravitate_key: Union[dict, CompositeMapKey],
        mapping_type: MappingType | None
    ) -> str | CompositeMapKey:
        """Get source_id using a composite gravitate key."""
        mappings = self.get_mappings_by_composite(
            gravitate_key, FastMapDirection.grav_to_source, mapping_type
        )
        if not mappings:
            raise KeyError(f"No mapping found for composite key: {gravitate_key}")
        if len(mappings) > 1:
            raise KeyError(f"Multiple mappings ({len(mappings)}) found for: {gravitate_key}")
        return mappings[0].source_id

    def get_mapping_by_composite(
        self,
        from_key: Union[dict, CompositeMapKey],
        direction: FastMapDirection,
        mapping_type: MappingType | None
    ) -> Map | Children:
        """Get single mapping by composite key, raises if not found or multiple."""
        mappings = self.get_mappings_by_composite(from_key, direction, mapping_type)
        if not mappings:
            raise KeyError(f"No mapping found for composite key: {from_key}")
        if len(mappings) > 1:
            raise KeyError(f"Multiple mappings ({len(mappings)}) found for: {from_key}")
        return mappings[0]

    def find_mappings_by_partial_key(
        self,
        partial_key: dict[str, str],
        direction: FastMapDirection,
        mapping_type: MappingType | None = None
    ) -> list[Map | Children]:
        """
        Find all mappings where the composite key contains the partial key fields.

        Example: partial_key={"product": "X"} matches {"product": "X", "terminal": "Y"}
        """
        self._raise_if_not_loaded()
        results = []
        for fast_key, mappings in self.fast_maps.items():
            if fast_key.direction != direction:
                continue
            if mapping_type is not None and fast_key.type != mapping_type:
                continue
            # Check if from_id is a CompositeMapKey and matches partial
            if isinstance(fast_key.from_id, CompositeMapKey):
                if fast_key.from_id.matches(partial_key):
                    results.extend(mappings)
        return results


class RitaMapper(RitaMapperCore):
    def __init__(self, provider: MappingProvider | AsyncMappingProvider, source_system: str):
        super().__init__()
        self.provider = provider
        self.source_system = source_system

    async def load_mappings_async(self):
        """
        Load mappings from the provider asynchronously.

        :raises TypeError: If the provider is not async.

        Note that this method does not check whether mappings are already loaded; calling it will overwrite any stored
        mappings with a fresh set from the provider.
        """
        if isinstance(self.provider, AsyncMappingProvider):
            mappings = await self.provider.get_mappings_by_source_system(self.source_system)
        else:
            raise TypeError("Provider is not async")
        super()._load_mappings(mappings)

    def load_mappings(self):
        """
        Load mappings from the provider synchronously.

        :raises TypeError: If the provider is async.

        Note that this method does not check whether mappings are already loaded; calling it will overwrite any stored
        mappings with a fresh set from the provider.
        """
        if isinstance(self.provider, MappingProvider):
            mappings = self.provider.get_mappings_by_source_system(self.source_system)
        else:
            raise TypeError("Provider is not synchronous")
        super()._load_mappings(mappings)
