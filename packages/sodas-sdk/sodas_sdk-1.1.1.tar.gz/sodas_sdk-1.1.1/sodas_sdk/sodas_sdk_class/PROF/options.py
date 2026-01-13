from copy import deepcopy
from enum import Enum
from typing import Any, Dict, List, Type, TypedDict, TypeVar


from sodas_sdk.core.error import NotTemplateBasedResourceDescriptor
from sodas_sdk.core.functionality_error import (
    CustomTypeNotExist,
    NotExistingNamespace,
    NotValidResourceDescriptor,
    TargetProfileNotExist,
)
from sodas_sdk.core.type import (
    ArtifactType,
    IRIType,
    ProfileType,
    ResourceDescriptorRole,
    TemplateDetailFunctionality,
)
from sodas_sdk.core.values import (
    BASIC_TYPE_VALUES,
    CONVERSION_VALUES,
    MEASURE_VALUES,
    ORIGIN_VALUES,
)
from sodas_sdk.sodas_sdk_class.dictionary.vocabulary import Vocabulary
from sodas_sdk.sodas_sdk_class.PROF.resource_descriptor import ResourceDescriptor


class Option(TypedDict):
    name: str
    value: Any


Options = list[Option]


T = TypeVar("T", bound=Enum)


def enum_to_options(enum_cls: Type[Enum]) -> Options:
    return [{"name": e.name, "value": e.value} for e in enum_cls]


ROLE_OPTIONS: Options = enum_to_options(ResourceDescriptorRole)
BASIC_TYPE_OPTIONS: Options = enum_to_options(BASIC_TYPE_VALUES)
PROFILE_TYPE_OPTIONS: Options = enum_to_options(ProfileType)
ARTIFACT_TYPE_OPTIONS: Options = enum_to_options(ArtifactType)
FUNCTIONALITY_OPTIONS: Options = enum_to_options(TemplateDetailFunctionality)


class ProfileOptions:
    OriginOptions: Options = enum_to_options(ORIGIN_VALUES)
    MeasureOptions: Options = enum_to_options(MEASURE_VALUES)
    ConversionOptions: Options = enum_to_options(CONVERSION_VALUES)
    RequiredOptions: Options = [
        {"name": "YES", "value": True},
        {"name": "NO", "value": False},
    ]
    DefaultOptions: Options = [
        {"name": "DEFAULT", "value": True},
        {"name": "CUSTOM", "value": False},
    ]

    def __init__(self) -> None:
        self.TypeOptions: Options = BASIC_TYPE_OPTIONS[:]
        self.CustomTypeOptions: Options = []
        self.CustomTypeOptionsDictionary: Dict[str, Options] = {}
        self.NamespaceOptions: Options = []
        self.TermDictionaryForVocabulary: Dict[IRIType, Options] = {}
        self.TermDictionaryForSchema: Dict[IRIType, Options] = {}
        self.FieldOptions: Options = []
        self.TargetProfileOptions: Options = []
        self.TargetFieldDictionary: Dict[IRIType, Options] = {}
        self.vocabularies: List[Vocabulary] = []

    async def set_initial_options(self, profile_type: ProfileType) -> None:
        self.vocabularies = await Vocabulary.get_all_db_records()
        self.NamespaceOptions = [
            {"name": v.prefix, "value": v.iri}
            for v in self.vocabularies
            if v.prefix is not None
        ]
        for vocabulary in self.vocabularies:
            iri = vocabulary.iri
            prefix = vocabulary.prefix

            if iri is None:
                raise ValueError("Vocabulary IRI cannot be None.")
            if prefix is None:
                raise ValueError(f"Vocabulary with IRI {iri} has no prefix.")

            self.NamespaceOptions.append({"name": prefix, "value": iri})

            terms: list[Option] = [
                {
                    "name": term.name,
                    "value": term.name,
                }  # term.name must be str, not Optional[str]
                for term in vocabulary.terms
                if term.name is not None
            ]

            self.TermDictionaryForVocabulary[iri] = terms[:]
            self.TermDictionaryForSchema[iri] = terms[:]
        from sodas_sdk.sodas_sdk_class.PROF.profile import Profile

        profiles = await Profile.get_all_profiles(profile_type)
        targeted_profiles = []
        for p in profiles:
            rd = p.get_resource_descriptor_of_role(ResourceDescriptorRole.SCHEMA)
            if rd and rd.use_template:
                targeted_profiles.append(p)

        self.TargetProfileOptions = [
            {"name": p.name, "value": p.iri}
            for p in targeted_profiles
            if p.name is not None and p.iri is not None
        ]
        for profile in targeted_profiles:
            schema_value = profile.get_template_descriptor_value_of_role(
                ResourceDescriptorRole.SCHEMA
            )
            if profile.iri is not None:
                self.TargetFieldDictionary[profile.iri] = [
                    {
                        "name": row[TemplateDetailFunctionality.NAME],
                        "value": row[TemplateDetailFunctionality.NAME],
                    }
                    for row in schema_value
                ]

    def update(self, descriptor: ResourceDescriptor) -> None:
        if descriptor.profile and descriptor.profile.Options is not self:
            raise NotValidResourceDescriptor()
        if not descriptor.use_template:
            raise NotTemplateBasedResourceDescriptor(descriptor)

        if descriptor.has_role == ResourceDescriptorRole.TYPE:
            self.update_type_options(descriptor)
            self.update_custom_type_options(descriptor)
        elif descriptor.has_role == ResourceDescriptorRole.VOCABULARY:
            self.update_term_dict_for_schema(descriptor)
        elif descriptor.has_role == ResourceDescriptorRole.SCHEMA:
            self.update_field_options(descriptor)

    def update_type_options(self, descriptor: ResourceDescriptor) -> None:
        values = descriptor.get_artifact_value()
        unique_names = list({row[TemplateDetailFunctionality.NAME] for row in values})
        self.CustomTypeOptions = [
            {"name": name, "value": name} for name in unique_names
        ]
        self.TypeOptions = BASIC_TYPE_OPTIONS + self.CustomTypeOptions

    def update_custom_type_options(self, descriptor: ResourceDescriptor) -> None:
        self.CustomTypeOptionsDictionary.clear()
        for row in descriptor.get_artifact_value():
            type_name = row[TemplateDetailFunctionality.NAME]
            label = row[TemplateDetailFunctionality.LABEL]
            value = row[TemplateDetailFunctionality.VALUE]
            self.CustomTypeOptionsDictionary.setdefault(type_name, []).append(
                {"name": label, "value": value}
            )

    def update_term_dict_for_schema(self, descriptor: ResourceDescriptor) -> None:
        for row in descriptor.get_artifact_value():
            ns = row[TemplateDetailFunctionality.NAMESPACE]
            term = row[TemplateDetailFunctionality.TERM]
            self.TermDictionaryForSchema.setdefault(ns, []).append(
                {"name": term, "value": term}
            )

    def update_field_options(self, descriptor: ResourceDescriptor) -> None:
        self.FieldOptions = [
            {
                "name": row[TemplateDetailFunctionality.NAME],
                "value": row[TemplateDetailFunctionality.NAME],
            }
            for row in descriptor.get_artifact_value()
        ]

    def validate(self, descriptor: ResourceDescriptor) -> None:
        if descriptor.profile and descriptor.profile.Options is not self:
            raise NotValidResourceDescriptor()
        if not descriptor.use_template:
            raise NotTemplateBasedResourceDescriptor(descriptor)
        # Validation logic is deferred

    def get_namespace_options(self) -> Options:
        return deepcopy(self.NamespaceOptions)

    def get_term_options_for_vocabulary(self, iri: IRIType) -> Options:
        if iri not in self.TermDictionaryForVocabulary:
            raise NotExistingNamespace(iri)
        return deepcopy(self.TermDictionaryForVocabulary[iri])

    def get_term_options_for_schema(self, iri: IRIType) -> Options:
        if iri not in self.TermDictionaryForSchema:
            raise NotExistingNamespace(iri)
        return deepcopy(self.TermDictionaryForSchema[iri])

    def get_custom_type_options(self, type_name: str) -> Options:
        if type_name not in self.CustomTypeOptionsDictionary:
            raise CustomTypeNotExist(type_name)
        return deepcopy(self.CustomTypeOptionsDictionary[type_name])

    def get_target_field_options(self, iri: IRIType) -> Options:
        if iri not in self.TargetFieldDictionary:
            raise TargetProfileNotExist(iri)
        return deepcopy(self.TargetFieldDictionary[iri])

    def get_vocabulary(self, iri: IRIType) -> Vocabulary:
        for v in self.vocabularies:
            if v.iri == iri:
                return v
        raise NotExistingNamespace(iri)
