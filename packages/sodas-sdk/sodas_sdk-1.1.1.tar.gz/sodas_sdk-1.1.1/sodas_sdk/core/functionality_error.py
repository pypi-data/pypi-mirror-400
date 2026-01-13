from typing import Any, List

from sodas_sdk.core.type import IRIType, TemplateDetailFunctionality

# ======================= COMMON ERROR =======================


class NotValidResourceDescriptor(Exception):
    def __init__(self):
        super().__init__("Not valid ResourceDescriptor is put")


class NotEnoughFunctionalityTemplate(Exception):
    def __init__(
        self,
        required_functionality_list: List[TemplateDetailFunctionality],
        input_functionality_list: List[TemplateDetailFunctionality],
    ):
        super().__init__(
            f"There are no required functionality.\n"
            f"Required: {required_functionality_list}\n"
            f"Input: {input_functionality_list}"
        )


# ======================= TYPE ERROR =======================


class DuplicatedTypeLabel(Exception):
    def __init__(self, label: str):
        super().__init__(f"Label: {label} is duplicated")


class DuplicatedTypeValue(Exception):
    def __init__(self, value: str):
        super().__init__(f"Type value: {value} is duplicated")


class CustomTypeNotExist(Exception):
    def __init__(self, type_name: str):
        super().__init__(f"Custom Type Name: {type_name} doesn't exist")


# ======================= VOCABULARY ERROR =======================


class InvalidOrigin(Exception):
    def __init__(self, origin: str):
        super().__init__(f"Origin: {origin} is invalid")


class NotExistingNamespace(Exception):
    def __init__(self, namespace_iri: IRIType):
        super().__init__(f"Namespace {namespace_iri} doesn't exist")


class NotExistingTermName(Exception):
    def __init__(self, name: str, namespace_iri: str):
        super().__init__(
            f"Term name: {name} doesn't exist in namespace: {namespace_iri}"
        )


class DuplicatedTermName(Exception):
    def __init__(self, name: str, namespace_iri: str):
        super().__init__(
            f"Term name: {name} is duplicated in namespace: {namespace_iri}"
        )


# ======================= SCHEMA ERROR =======================


class FieldNotExist(Exception):
    def __init__(self, name: str):
        super().__init__(f"Field: {name} doesn't exist.")


class DuplicatedField(Exception):
    def __init__(self, name: str):
        super().__init__(f"Field: {name} is duplicated.")


class DuplicatedRDFTerm(Exception):
    def __init__(self, namespace: IRIType, name: str):
        super().__init__(f"RDF TERM of {namespace}:{name} is duplicated.")


# ======================= CONSTRAINT ERROR =======================


class InvalidRequiredOption(Exception):
    def __init__(self, value: Any):
        super().__init__(f"Value: {value} is not valid for Required Option.")


class TypeNotExist(Exception):
    def __init__(self, type_: str):
        super().__init__(f"Type: {type_} doesn't exist.")


# ======================= MAPPING ERROR =======================


class TargetProfileNotExist(Exception):
    def __init__(self, target_profile_iri: IRIType):
        super().__init__(f"TargetProfile with IRI: {target_profile_iri} doesn't exist")


class TargetFieldNotExist(Exception):
    def __init__(self, target_profile_iri: IRIType, target_field: str):
        super().__init__(
            f"TargetField: {target_field} in TargetProfile with IRI: {target_profile_iri} doesn't exist"
        )


class DuplicatedMapping(Exception):
    def __init__(self, source_field: str, target_profile_iri: IRIType):
        super().__init__(
            f"SourceField: {source_field} with TargetProfile {target_profile_iri} is duplicated."
        )


# ======================= VALIDATION ERROR =======================


class InvalidMeasureOption(Exception):
    def __init__(self, value: str):
        super().__init__(f"Value: {value} is not valid for Measure Option.")


# ======================= SPECIFICATION ERROR =======================


class InvalidConversionOption(Exception):
    def __init__(self, value: str):
        super().__init__(f"Value: {value} is not valid for Conversion Option.")
