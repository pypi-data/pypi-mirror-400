from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Import only when type checking (i.e., during static analysis)
    from sodas_sdk.core.type import (
        ProfileType,
        ResourceDescriptorRole,
        TemplateDetailFunctionality,
    )
    from sodas_sdk.sodas_sdk_class.PROF.profile import Profile
    from sodas_sdk.sodas_sdk_class.PROF.resource_descriptor import ResourceDescriptor


class AlreadyRecordedError(Exception):
    def __init__(self, instance: Any):
        super().__init__(f"This instance is already recorded in Database: {instance}")


class APIURLNotSetError(Exception):
    def __init__(self, cls: type):
        super().__init__(f"API_URL is not set in class: {cls.__name__}")


class DeleteRecordFailError(Exception):
    def __init__(self):
        super().__init__("Delete DBRecord Failed")


class IndexOutOfBoundsError(Exception):
    def __init__(self, index: int):
        super().__init__(f"Index : {index} out of bounds")


class InvalidDateObjectError(Exception):
    def __init__(self, value: Any):
        super().__init__(f"Invalid Date object : {value}")


class InvalidDateStringError(Exception):
    def __init__(self, s: str):
        super().__init__(f"Invalid Date string : {s}")


class InvalidProfileTypeError(Exception):
    def __init__(self, profile: "Profile", expected_type: "ProfileType"):
        super().__init__(f"Invalid type '{profile.type}' instead of '{expected_type}'")


class InvalidTemplateArtifactRow(Exception):
    def __init__(self, index: int, missing_keys: list, extra_keys: list):
        super().__init__(
            f"TemplateArtifactValue[{index}] is not valid.\n"
            f"Missing Keys: {missing_keys}\n"
            f"Extra Keys: {extra_keys}"
        )


class InvalidTypeError(Exception):
    def __init__(self, value: Any, expected_type: str):
        super().__init__(
            f"Invalid type '{type(value).__name__}' instead of '{expected_type}'"
        )


class InvalidValueError(Exception):
    def __init__(self, value: Any):
        super().__init__(f"Invalid value : {value} is put")


class NamedTermNotExistError(Exception):
    def __init__(self, name: str):
        super().__init__(f"Named term {name} not exist.")


class NeedToImplementError(NotImplementedError):
    def __init__(self):
        super().__init__("It needs to be implemented.")


class NeedToSetTemplateError(Exception):
    def __init__(self):
        super().__init__("Template Artifact need to be set template.")


class NeedToSetFieldError(Exception):
    def __init__(self, value: Any, field: str):
        super().__init__(f"This instance : {value} needs to set field : {field}")


class NoAccessTokenFoundError(Exception):
    def __init__(self):
        super().__init__("No accessToken found in the response")


class NotInitializedError(Exception):
    def __init__(self, field: str):
        super().__init__(f"Field : {field} is not initialized yet")


class NotRecordedArgumentError(Exception):
    def __init__(self, instance: Any):
        super().__init__(f"Not recorded argument is put : {instance}")


class NotRecordedYetError(Exception):
    def __init__(self, instance: Any):
        super().__init__(f"This instance is not recorded in Database yet : {instance}")


class NotTemplateBasedResourceDescriptor(Exception):
    def __init__(self, resource_descriptor: "ResourceDescriptor"):
        super().__init__(
            f"Resource Descriptor is not set to use template: {resource_descriptor}"
        )


class RecordNotFoundError(Exception):
    def __init__(self):
        super().__init__("Record is not found")


class RequirementsNotSetError(Exception):
    def __init__(self):
        super().__init__("Requirements are not set")


class ResourceRoleDescriptorAlreadyExist(Exception):
    def __init__(self, role: "ResourceDescriptorRole"):
        super().__init__(
            f"Resource Descriptor with specific role: {role} already exists."
        )


class ResourceRoleDescriptorNotExist(Exception):
    def __init__(self, role: "ResourceDescriptorRole"):
        super().__init__(
            f"Resource Descriptor with specific role: {role} doesn't exist."
        )


class RetryLimitReachedError(Exception):
    def __init__(self, max_attempts: int):
        super().__init__(f"Max retries[{max_attempts}] reached")


class SwitchSameIndexError(Exception):
    def __init__(self, index: int):
        super().__init__(f"Switch same index : {index}")


class TemplateDetailFunctionalityAlreadyExist(Exception):
    def __init__(self, functionality: "TemplateDetailFunctionality"):
        super().__init__(f"Functionality {functionality} already exists.")


class UnexpectedResponseFormatError(Exception):
    def __init__(self, response: Any):
        super().__init__(f"Unexpected response format: {response}")
