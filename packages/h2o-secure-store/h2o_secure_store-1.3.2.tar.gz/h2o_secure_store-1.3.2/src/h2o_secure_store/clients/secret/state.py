from enum import Enum

from h2o_secure_store.gen.model.secret_state import SecretState as V1SecretState


class SecretState(Enum):
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_ACTIVE = "STATE_ACTIVE"
    STATE_DELETED = "STATE_DELETED"

    def to_api_object(self) -> V1SecretState:
        return V1SecretState(self.name)


def from_api_object(kernel_state: V1SecretState) -> SecretState:
    return SecretState(str(kernel_state))
