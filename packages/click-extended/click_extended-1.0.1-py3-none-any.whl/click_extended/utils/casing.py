"""Class to process strings and transform to different casings."""

import re
import unicodedata

NON_ALPHABETIC_PATTERN = re.compile(r"[^A-Za-z]+")
NON_ALPHANUMERIC_PATTERN = re.compile(r"[^\w]+", re.UNICODE)
LOWER_TO_UPPER_PATTERN = re.compile(r"([a-z\d])([A-Z])")
UPPER_TO_UPPER_LOWER_PATTERN = re.compile(r"([A-Z]+)([A-Z][a-z])")
NUMBER_TO_LETTER_PATTERN = re.compile(r"(\d)([^\W\d_])", re.UNICODE)


class Casing:
    """Class to process strings and transform to different casings."""

    @staticmethod
    def _normalize_unicode(value: str) -> str:
        """Normalize Unicode characters to ASCII equivalents."""
        nfd = unicodedata.normalize("NFD", value)
        return nfd.encode("ascii", "ignore").decode("ascii")

    @staticmethod
    def _split_into_words(value: str) -> list[str]:
        """
        Split a string into words, handling various
        delimiters and case transitions.
        """
        if not value:
            return []

        value = value.strip()
        value = value.replace("_", " ")
        value = re.sub(r"([a-z\d])([A-Z](?=[a-z]))", r"\1 \2", value)
        value = UPPER_TO_UPPER_LOWER_PATTERN.sub(r"\1 \2", value)
        value = re.sub(r"(\d)([A-Za-z])", r"\1 \2", value)
        value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)

        words = [word for word in value.split() if word]

        normalized_words: list[str] = []
        for word in words:
            normalized = Casing._normalize_unicode(word)
            if normalized:
                normalized_words.append(normalized)
            else:
                normalized_words.append(word)

        return normalized_words

    @staticmethod
    def _split_into_words_preserve_case(value: str) -> list[str]:
        """
        Split a string into words while preserving
        original capitalization.
        """
        if not value:
            return []

        value = value.strip()
        value = value.replace("_", " ")
        value = re.sub(r"([a-z\d])([A-Z](?=[a-z]))", r"\1 \2", value)
        value = UPPER_TO_UPPER_LOWER_PATTERN.sub(r"\1 \2", value)
        value = re.sub(r"(\d)([A-Za-z])", r"\1 \2", value)
        value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)

        return [word for word in value.split() if word]

    @staticmethod
    def to_lower_case(value: str) -> str:
        """Convert the value to lower case."""
        value = value.strip()
        value = re.sub(r"[\[\]]", "", value).strip()
        value = value.replace("\t", " ")
        return value.lower()

    @staticmethod
    def to_upper_case(value: str) -> str:
        """Convert the value to upper case."""
        value = value.strip()
        value = re.sub(r"[\[\]]", "", value).strip()
        value = value.replace("\t", " ")
        return value.upper()

    @staticmethod
    def to_meme_case(value: str) -> str:
        """Convert the value to mEmE cAsE."""
        if not value:
            return ""

        value = value.strip()

        result: list[str] = []
        char_index = 0

        for char in value:
            if char.isalpha():
                if char_index % 2 == 0:
                    result.append(char.lower())
                else:
                    result.append(char.upper())
                char_index += 1
            else:
                result.append(char)

        return "".join(result)

    @staticmethod
    def to_snake_case(value: str) -> str:
        """Convert the value to snake_case."""
        words = Casing._split_into_words(value)
        return "_".join(word.lower() for word in words)

    @staticmethod
    def to_screaming_snake_case(value: str) -> str:
        """Convert the value to SCREAMING_SNAKE_CASE."""
        words = Casing._split_into_words(value)
        return "_".join(word.upper() for word in words)

    @staticmethod
    def to_camel_case(value: str) -> str:
        """Convert the value to camelCase."""
        words = Casing._split_into_words(value)
        if not words:
            return ""
        return words[0].lower() + "".join(
            word.capitalize() for word in words[1:]
        )

    @staticmethod
    def to_pascal_case(value: str) -> str:
        """Convert the value to PascalCase."""
        words = Casing._split_into_words(value)
        return "".join(word.capitalize() for word in words)

    @staticmethod
    def to_kebab_case(value: str) -> str:
        """Convert the value to kebab-case."""
        words = Casing._split_into_words(value)
        return "-".join(word.lower() for word in words)

    @staticmethod
    def to_train_case(value: str) -> str:
        """Convert the value to Train-Case."""
        words = Casing._split_into_words(value)
        return "-".join(word.capitalize() for word in words)

    @staticmethod
    def to_flat_case(value: str) -> str:
        """Convert the value to flatcase."""
        words = Casing._split_into_words(value)
        return "".join(word.lower() for word in words)

    @staticmethod
    def to_dot_case(value: str) -> str:
        """Convert the value to dot.case."""
        words = Casing._split_into_words(value)
        return ".".join(word.lower() for word in words)

    @staticmethod
    def to_title_case(value: str) -> str:
        """Convert the value to Title Case."""
        words = Casing._split_into_words(value)
        return " ".join(word.capitalize() for word in words)

    @staticmethod
    def to_path_case(value: str) -> str:
        """Convert the value to path/case."""
        words = Casing._split_into_words(value)
        return "/".join(word.lower() for word in words)
