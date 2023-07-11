from __future__ import annotations

import typing as t

from globus_sdk.exc import GlobusError


class GlobusSessionErrorAuthorizationParameters:
    """
    Represents authorization parameters that can be used to instruct a client
    which additional authorizations are needed in order to complete a request.

    :ivar session_message: A message to be displayed to the user.
    :vartype session_message: str, optional

    :ivar session_required_identities: A list of identities required for the
        session.
    :vartype session_required_identities: list of str, optional

    :ivar session_required_policies: A list of policies required for the
        session.
    :vartype session_required_policies: list of str, optional

    :ivar session_required_single_domain: A list of domains required for the
        session.
    :vartype session_required_single_domain: list of str, optional

    :ivar session_required_mfa: Whether MFA is required for the session.
    :vartype session_required_mfa: bool, optional

    :ivar session_required_scopes: A list of scopes for which consent is required.
    :vartype session_required_scopes: list of str, optional

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    session_message: str | None
    session_required_identities: list[str] | None
    session_required_policies: list[str] | None
    session_required_single_domain: list[str] | None
    session_required_mfa: bool | None
    session_required_scopes: list[str] | None
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "session_message": str,
        "session_required_identities": list,
        "session_required_policies": list,
        "session_required_single_domain": list,
        "session_required_mfa": bool,
        "session_required_scopes": list,
    }

    def __init__(
        self,
        session_message: str | None = None,
        session_required_identities: list[str] | None = None,
        session_required_policies: list[str] | None = None,
        session_required_single_domain: list[str] | None = None,
        session_required_mfa: bool | None = None,
        session_required_scopes: list[str] | None = None,
        extra: dict[str, t.Any] | None = None,
    ):
        self.session_message = session_message
        self.session_required_identities = session_required_identities
        self.session_required_policies = session_required_policies
        self.session_required_single_domain = session_required_single_domain
        self.session_required_mfa = session_required_mfa
        self.session_required_scopes = session_required_scopes
        self.extra_fields = extra or {}

        # Enforce that the error contains at least one of the fields we expect
        if not any(
            (getattr(self, field_name) is not None)
            for field_name in self.SUPPORTED_FIELDS.keys()
        ):
            raise ValueError(
                "Must include at least one supported authorization parameter: "
                ", ".join(self.SUPPORTED_FIELDS.keys())
            )

        # Enforce the field types
        for field_name, field_type in self.SUPPORTED_FIELDS.items():
            field_value = getattr(self, field_name)
            if field_value is not None and not isinstance(field_value, field_type):
                raise ValueError(
                    f"'{field_name}' must be of type {field_type.__name__}"
                )

    @classmethod
    def from_dict(
        cls, param_dict: dict[str, t.Any]
    ) -> GlobusSessionErrorAuthorizationParameters:
        """
        Instantiate from a session error authorization parameters dictionary. Raises
        a ValueError if the dictionary does not contain a valid GlobusSessionError.

        :param param_dict: The dictionary to create the error from.
        :type param_dict: dict
        """

        # Extract any extra fields
        extras = {k: v for k, v in param_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = param_dict.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Return a session error authorization parameters dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields in
            the returned dictionary.
        :type include_extra: bool
        """
        session_error_dict = {}

        # Set any authorization parameters
        for field in self.SUPPORTED_FIELDS.keys():
            if getattr(self, field) is not None:
                session_error_dict[field] = getattr(self, field)

        # Set any extra fields
        if include_extra:
            session_error_dict.update(self.extra_fields)

        return session_error_dict


class GlobusSessionError(GlobusError):
    """
    Represents a Globus Session Error.

    A Session Error is a class of error that is returned by Globus services to
    indicate that additional authorization is required in order to complete a request
    and contains information that can be used to request the appropriate authorization.

    :ivar code: The error code for this error.
    :vartype code: str

    :ivar authorization_parameters: The authorization parameters for this error.
    :vartype authorization_parameters: GlobusAuthorizationParameters

    :ivar extra_fields: A dictionary of additional fields that were provided. May
        be used for forward/backward compatibility.
    :vartype extra_fields: dict
    """

    code: str
    authorization_parameters: GlobusSessionErrorAuthorizationParameters
    extra_fields: dict[str, t.Any]

    SUPPORTED_FIELDS = {
        "code": str,
        "authorization_parameters": GlobusSessionErrorAuthorizationParameters,
    }

    def __init__(
        self,
        code: str | None,
        authorization_parameters: dict[str, t.Any]
        | GlobusSessionErrorAuthorizationParameters
        | None,
        extra: dict[str, t.Any] | None,
    ):
        if code is None:
            raise ValueError("Must have a 'code'")
        self.code = code

        self.extra_fields = extra or {}

        # Enforce that authorization_parameters is in the error_dict and
        # contains at least one of the fields we expect
        if isinstance(
            authorization_parameters, GlobusSessionErrorAuthorizationParameters
        ):
            self.authorization_parameters = authorization_parameters
        elif isinstance(authorization_parameters, dict):
            self.authorization_parameters = (
                GlobusSessionErrorAuthorizationParameters.from_dict(
                    param_dict=authorization_parameters
                )
            )
        else:
            raise ValueError("Must have 'authorization_parameters'")

    @classmethod
    def from_dict(cls, error_dict: dict[str, t.Any]) -> GlobusSessionError:
        """
        Instantiate a GlobusSessionError from a dictionary.

        :param error_dict: The dictionary to create the error from.
        :type error_dict: dict
        """

        # Extract any extra fields
        extras = {k: v for k, v in error_dict.items() if k not in cls.SUPPORTED_FIELDS}
        kwargs: dict[str, t.Any] = {"extra": extras}
        # Ensure required fields are supplied
        for field_name in cls.SUPPORTED_FIELDS.keys():
            kwargs[field_name] = error_dict.get(field_name)

        return cls(**kwargs)

    def to_dict(self, include_extra: bool = False) -> dict[str, t.Any]:
        """
        Return a session error response dictionary.

        :param include_extra: Whether to include stored extra (non-standard) fields
            in the dictionary.
        :type include_extra: bool, optional (default: False)
        """
        session_error_dict = {
            "code": self.code,
            "authorization_parameters": self.authorization_parameters.to_dict(
                include_extra=include_extra
            ),
        }

        # Set any extra fields
        if include_extra:
            session_error_dict.update(self.extra_fields)

        return session_error_dict
