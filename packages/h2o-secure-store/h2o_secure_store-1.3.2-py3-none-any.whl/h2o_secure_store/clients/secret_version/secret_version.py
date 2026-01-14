import base64
import pprint
from datetime import datetime
from typing import Optional

from h2o_secure_store.gen.model.v1_secret_version import V1SecretVersion


class SecretVersion:
    def __init__(
            self,
            value: bytes,
            name: str = "",
            creator: str = "",
            uid: str = "",
            create_time: Optional[datetime] = None,
    ):
        """
        Args:
            value (bytes, optional): Required. Input only. The secret payload of the SecretVersion.
                                     Must be no larger than 64KiB.
                                     Can be retrieved using the reveal_secret_version_value method.
            name (str, optional): Resource name of the SecretVersion. Format is `workspaces/*/secret_versions/*`.
            creator (str, optional): Name of an entity that created the SecretVersion.
            uid (str, optional): Globally unique identifier of the resource.
            create_time (str, datetime): Time when the SecretVersion was created.
        """

        self.name = name
        self.value = value
        self.creator = creator
        self.uid = uid
        self.create_time = create_time

    def get_secret_version_id(self) -> str:
        segments = self.name.split("/")
        if len(segments) != 6:
            return ""

        return segments[5]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1SecretVersion:
        return V1SecretVersion(
            value=base64.b64encode(self.value).decode('utf-8'),
        )


def from_api_object(api_object: V1SecretVersion) -> SecretVersion:
    return SecretVersion(
        name=api_object.name,
        value=base64.b64decode(api_object.value),
        creator=api_object.creator,
        create_time=api_object.create_time,
        uid=api_object.uid,
    )
