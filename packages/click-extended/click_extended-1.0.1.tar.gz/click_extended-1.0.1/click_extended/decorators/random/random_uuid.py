"""Parent node for generating a random UUID."""

import random
from typing import Any, Literal
from uuid import UUID, uuid1, uuid3, uuid5

from click_extended.classes import ParentNode
from click_extended.core.other.context import Context
from click_extended.types import Decorator


class RandomUUID(ParentNode):
    """Parent node for generating a random UUID."""

    @staticmethod
    def _validate_namespace(namespace: UUID | str | None, version: int) -> UUID:
        """Validate and convert namespace to UUID object."""
        if namespace is None:
            raise ValueError(
                f"namespace is required for UUID version {version}"
            )
        if isinstance(namespace, str):
            try:
                return UUID(namespace)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid namespace UUID format: '{namespace}'. "
                    f"Expected a valid UUID string "
                    f"(e.g., '6ba7b810-9dad-11d1-80b4-00c04fd430c8') "
                    f"or use predefined constants like uuid.NAMESPACE_DNS"
                ) from exc
        return namespace

    def load(self, context: Context, *args: Any, **kwargs: Any) -> UUID:
        if kwargs.get("seed") is not None:
            random.seed(kwargs["seed"])

        version = kwargs.get("version", 4)

        if version == 1:
            return uuid1()

        if version == 3:
            namespace = self._validate_namespace(kwargs.get("namespace"), 3)
            uuid_name = kwargs.get("uuid_name")
            if uuid_name is None:
                raise ValueError("uuid_name is required for UUID version 3")
            return uuid3(namespace, uuid_name)

        if version == 4:
            random_bytes = bytearray(random.getrandbits(8) for _ in range(16))
            random_bytes[6] = (random_bytes[6] & 0x0F) | 0x40
            random_bytes[8] = (random_bytes[8] & 0x3F) | 0x80
            return UUID(bytes=bytes(random_bytes))

        if version == 5:
            namespace = self._validate_namespace(kwargs.get("namespace"), 5)
            uuid_name = kwargs.get("uuid_name")
            if uuid_name is None:
                raise ValueError("uuid_name is required for UUID version 5")
            return uuid5(namespace, uuid_name)

        raise ValueError(
            f"Unsupported UUID version: {version}. "
            f"Supported versions are 1, 3, 4, and 5."
        )


def random_uuid(
    name: str,
    version: Literal[1, 3, 4, 5] = 4,
    namespace: UUID | str | None = None,
    uuid_name: str | None = None,
    seed: int | None = None,
) -> Decorator:
    """
    Generate a random UUID.

    Type: `ParentNode`

    Args:
        name (str):
            The name of the parent node.
        version (Literal[1, 3, 4, 5], optional):
            The version of the UUID. Defaults to 4.
            - Version 1: Time-based UUID (includes MAC address and timestamp)
            - Version 3: MD5 hash of namespace + name (deterministic)
            - Version 4: Random UUID (recommended for most use cases)
            - Version 5: SHA-1 hash of namespace + name (deterministic)
        namespace (UUID | str | None, optional):
            The namespace UUID for versions 3 and 5. Required for those
            versions. Must be a valid UUID object, a valid UUID string in the
            format 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', or use predefined
            constants from the uuid module (NAMESPACE_DNS, NAMESPACE_URL,
            NAMESPACE_OID, NAMESPACE_X500). The namespace acts as a domain
            identifier to generate deterministic UUIDs.
        uuid_name (str | None, optional):
            The name string for versions 3 and 5. Required for those versions.
            This is combined with the namespace to generate a deterministic
            UUID. The same namespace and name will always produce the same UUID.
        seed (int | None, optional):
            Optional seed for reproducible UUIDs (only affects version 4).

    Returns:
        Decorator:
            The decorator function.

    Raises:
        ValueError:
            If an unsupported UUID version is specified or if namespace/name
            are missing for versions 3 or 5.
    """
    return RandomUUID.as_decorator(
        name=name,
        version=version,
        namespace=namespace,
        uuid_name=uuid_name,
        seed=seed,
    )
