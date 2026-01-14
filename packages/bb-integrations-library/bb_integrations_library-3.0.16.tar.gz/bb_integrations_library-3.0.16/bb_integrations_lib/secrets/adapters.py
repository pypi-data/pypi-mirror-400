from copy import deepcopy
from typing import TypeVar, Any, Union

from onepasswordconnectsdk.models import Item, Field, ItemUrls
from pydantic import TypeAdapter

from bb_integrations_lib.secrets import AnyCredential, AbstractCredential, onepassword_category_map

ConcreteOrTaggedCredential = TypeVar("ConcreteOrTaggedCredential", bound=Union[AbstractCredential, AnyCredential])


class OPSecretAdapter:
    """
    Helper class for translating between 1Password Connect SDK models and our own credential models.
    Defines a fixed set of transformation rules that support round-trip conversions.

    Note that ``credential_to_opc`` does NOT output a ready-to-upload Item object, because credential models don't
    contain fields like title or category, but it does provide the minimum set of field, URL, and tag information needed
    to validate the model. See ``apply_to_opc`` for a reference implementation of updating a 1P item model with a
    credential model.
    """

    @staticmethod
    def credential_to_opc(credential: AbstractCredential) -> Item:
        """
        Convert a credential model to a barebones 1P Connet Item model. The item returned by this method is not ready
        for upload, but can be used as the basis for merging into an existing model. This function exists primarily to
        outline a standard set of transformations for round-trip model ser/deser to 1P.
        """
        url = getattr(credential, "host", None)
        return Item(
            fields=[
                Field(
                    label=name,
                    value=getattr(credential, name)
                )
                for name, f in type(credential).model_fields.items() if name != "host"
            ],
            tags=[
                f"type/{credential.type_tag}"
            ],
            urls=[
                ItemUrls(
                    primary=True,
                    href=url
                )
            ]
        )

    @staticmethod
    def apply_to_opc(credential: AbstractCredential, item: Item) -> Item:
        """
        "Apply" a credential model to an existing 1P item model. Useful if updating a 1P Item with changed secret field
        values.

        :param credential: The credential model to convert/apply to item.
        :param item: The 1P item model, returned by the OPC SDK's ``get_item`` or ``create_item``, for example.
        :return: A copy of item with the relevant pieces of data replaced with converted items from the credential.
        """
        new_item = deepcopy(item)
        converted = OPSecretAdapter.credential_to_opc(credential)
        new_item.category = onepassword_category_map[type(credential)]
        new_item.fields = converted.fields
        new_item.tags = list(set(new_item.tags) | set(converted.tags))
        new_item.urls = converted.urls
        return new_item

    @staticmethod
    def opc_to_credential_dict(item: Item) -> dict[str, Any]:
        """
        Convert a 1P Item to a dictionary of field values, with the standard transformations applied.

        :param item: The 1P Item to convert.
        :return: A dictionary of fields from the credential that can be used to construct credential models.
        """
        fields = {field.label.replace(" ", "_"): field.value for field in item.fields}
        if item.urls:
            [primary_url] = [x for x in item.urls if x.primary]
            fields["host"] = primary_url.href
        return fields

    @staticmethod
    def opc_to_credential(
            item: Item,
            credential_type: type[ConcreteOrTaggedCredential] = AnyCredential
    ) -> ConcreteOrTaggedCredential:
        """
        Helper method to convert a 1P Item model to a credential model, validating it. This will either throw a
        ValidationError or return an instance of a concrete credential type. Equivalent to validating a model on the
        output of ``opc_to_credential_dict``.

        :param item: The 1P Item model to convert.
        :param credential_type: The type of credential to return. Supports and defaults to AnyCredential, which will
          automatically infer the type from the type_tag discriminator field, if desired.
        """
        if type(credential_type) == TypeAdapter:
            return credential_type.validate_python(OPSecretAdapter.opc_to_credential_dict(item))
        return credential_type(**OPSecretAdapter.opc_to_credential_dict(item))
