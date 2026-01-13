from typing import TypeVar, Generic, Dict, Optional

LTE = TypeVar("LTE", bound=str)  # Language Type
LKD = TypeVar("LKD", bound=str)  # Language Key Dict
LMD = TypeVar("LMD", bound=Dict[str, str])  # Language Message Dict


class Resources(Generic[LTE, LMD]):
    def __init__(
        self,
        locals: Dict[LTE, LMD],
        local_keys: Dict[str, str],
        default_language: Optional[LTE] = None,
    ):
        self.values = locals
        self.keys = local_keys
        self.default_language = default_language
        self.global_language = None

        if default_language and default_language not in self.values:
            raise ValueError(
                f"Default language {default_language} not found in local resources."
            )

        # Validar que todas las claves existen en todos los idiomas
        resources_not_found = []
        for key in self.keys.keys():
            for lang in self.values.keys():
                if key not in self.values[lang]:
                    resources_not_found.append(f"{lang}: {key}")

        if resources_not_found:
            raise ValueError(
                f"The messages for {', '.join(resources_not_found)} was not found in local resources."
            )

    def set_default_language(self, default_language: LTE) -> None:
        if default_language not in self.values:
            raise ValueError(
                f"Default language {default_language} not found in local resources."
            )
        self.default_language = default_language

    def init(self, language: LTE) -> None:
        if not language:
            return
        if language not in self.values:
            print(f'Accept-Language "{language}" not found in locals resource.')
            return
        self.global_language = language

    def update_locals(self, locals: Dict[LTE, LMD], local_keys: Dict[str, str]) -> None:
        if locals:
            self.values = locals
            self.keys = local_keys

    def get(self, resource_name: str, language: Optional[LTE] = None) -> str:
        if (
            language
            and language in self.values
            and resource_name in self.values[language]
        ):
            return self.values[language][resource_name]

        if (
            self.global_language
            and self.global_language in self.values
            and resource_name in self.values[self.global_language]
        ):
            return self.values[self.global_language][resource_name]

        if (
            self.default_language
            and self.default_language in self.values
            and resource_name in self.values[self.default_language]
        ):
            return self.values[self.default_language][resource_name]

        raise ValueError(f"Resource {resource_name} not found in any local resource.")

    def get_with_params(
        self,
        resource_name: str,
        params: Dict[str, str],
        language: Optional[LTE] = None,
    ) -> str:
        resource = None

        if (
            language
            and language in self.values
            and resource_name in self.values[language]
        ):
            resource = self.values[language][resource_name]
        elif (
            self.global_language
            and self.global_language in self.values
            and resource_name in self.values[self.global_language]
        ):
            resource = self.values[self.global_language][resource_name]
        elif (
            self.default_language
            and self.default_language in self.values
            and resource_name in self.values[self.default_language]
        ):
            resource = self.values[self.default_language][resource_name]

        if not resource:
            raise ValueError(
                f"Resource {resource_name} not found in any local resource."
            )

        return self._apply_pattern(resource, params)

    @staticmethod
    def replace_params(text: str, params: Dict[str, str]) -> str:
        if not text or not params:
            return text
        return Resources._apply_pattern(text, params)

    @staticmethod
    def _apply_pattern(text: str, params: Dict[str, str]) -> str:
        for key, value in params.items():
            pattern = f"{{{{{key}}}}}"
            text = text.replace(pattern, value)
        return text
