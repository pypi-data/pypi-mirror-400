"""
Unit tests for parser.variable module
"""

import pytest

from markdown_flow.parser import extract_variables_from_text, replace_variables_in_text


class TestExtractVariables:
    """Test variable extraction functionality."""

    def test_extract_brace_variables(self):
        """Test extracting {{variable}} format."""
        text = "Hello {{name}}, you are {{age}} years old"
        variables = extract_variables_from_text(text)
        assert "name" in variables
        assert "age" in variables
        assert len(variables) == 2

    def test_extract_percent_variables(self):
        """Test extracting %{{variable}} format."""
        text = "?[%{{level}} Beginner|Expert]"
        variables = extract_variables_from_text(text)
        assert "level" in variables
        assert len(variables) == 1

    def test_extract_mixed_variables(self):
        """Test extracting both formats."""
        text = "Hello {{name}}! Choose: ?[%{{level}} A|B]"
        variables = extract_variables_from_text(text)
        assert "name" in variables
        assert "level" in variables
        assert len(variables) == 2

    def test_extract_no_variables(self):
        """Test text with no variables."""
        text = "Plain text without variables"
        variables = extract_variables_from_text(text)
        assert len(variables) == 0

    def test_extract_duplicate_variables(self):
        """Test that duplicates are deduplicated."""
        text = "{{name}} and {{name}} and %{{name}}"
        variables = extract_variables_from_text(text)
        assert variables == ["name"]


class TestReplaceVariables:
    """Test variable replacement functionality."""

    def test_replace_simple_variable(self):
        """Test simple variable replacement."""
        text = "Hello {{name}}!"
        variables = {"name": "John"}
        result = replace_variables_in_text(text, variables)
        assert result == 'Hello """John"""!'

    def test_replace_multiple_variables(self):
        """Test multiple variable replacement."""
        text = "Hello {{name}}, you are {{age}} years old"
        variables = {"name": "John", "age": "25"}  # Use string for age to match type signature
        result = replace_variables_in_text(text, variables)
        assert result == 'Hello """John""", you are """25""" years old'

    def test_preserve_percent_variables(self):
        """Test that %{{variable}} format is preserved."""
        text = "Hello {{name}}! Choose: ?[%{{level}} A|B]"
        variables = {"name": "John", "level": "Beginner"}
        result = replace_variables_in_text(text, variables)
        assert '"""John"""' in result
        assert "%{{level}}" in result  # Should be preserved

    def test_replace_list_values(self):
        """Test replacing variables with list values."""
        text = "Skills: {{skills}}"
        variables = {"skills": ["Python", "JavaScript", "Go"]}
        result = replace_variables_in_text(text, variables)
        assert result == 'Skills: """Python, JavaScript, Go"""'

    def test_replace_undefined_variable(self):
        """Test that undefined variables get 'UNKNOWN'."""
        text = "Hello {{name}}!"
        result = replace_variables_in_text(text, {})
        assert result == 'Hello """UNKNOWN"""!'

    def test_replace_empty_value(self):
        """Test that empty values get 'UNKNOWN'."""
        text = "Hello {{name}}!"
        variables = {"name": ""}
        result = replace_variables_in_text(text, variables)
        assert result == 'Hello """UNKNOWN"""!'

    def test_replace_none_value(self):
        """Test that None values get 'UNKNOWN'."""
        text = "Hello {{name}}!"
        variables = {"name": None}
        result = replace_variables_in_text(text, variables)
        assert result == 'Hello """UNKNOWN"""!'

    def test_replace_empty_list(self):
        """Test that empty list gets 'UNKNOWN'."""
        text = "Skills: {{skills}}"
        variables: dict[str, list[str]] = {"skills": []}
        result = replace_variables_in_text(text, variables)
        assert result == 'Skills: """UNKNOWN"""'

    def test_replace_inside_preserve_tag(self):
        """Test that variables inside preserve tags don't get triple quotes."""
        text = "<preserve_or_translate>Hello {{name}}</preserve_or_translate>"
        variables = {"name": "John"}
        result = replace_variables_in_text(text, variables)
        assert result == "<preserve_or_translate>Hello John</preserve_or_translate>"

    def test_replace_multiple_inside_preserve_tag(self):
        """Test multiple variables inside preserve tag."""
        text = "<preserve_or_translate>{{greeting}} {{name}}, age: {{age}}</preserve_or_translate>"
        variables = {"greeting": "Hello", "name": "Alice", "age": "25"}
        result = replace_variables_in_text(text, variables)
        assert result == "<preserve_or_translate>Hello Alice, age: 25</preserve_or_translate>"

    def test_replace_mixed_inside_and_outside_preserve_tags(self):
        """Test mixed variables inside and outside preserve tags."""
        text = "Welcome {{name}}! <preserve_or_translate>Score: {{score}}</preserve_or_translate>"
        variables = {"name": "Bob", "score": "100"}
        result = replace_variables_in_text(text, variables)
        assert result == 'Welcome """Bob"""! <preserve_or_translate>Score: 100</preserve_or_translate>'

    def test_replace_preserve_tag_with_list_value(self):
        """Test list value inside preserve tag."""
        text = "<preserve_or_translate>Items: {{items}}</preserve_or_translate>"
        variables = {"items": ["A", "B", "C"]}
        result = replace_variables_in_text(text, variables)
        assert result == "<preserve_or_translate>Items: A, B, C</preserve_or_translate>"

    def test_replace_multiple_preserve_tags(self):
        """Test multiple preserve tags in one text."""
        text = "<preserve_or_translate>{{a}}</preserve_or_translate> and <preserve_or_translate>{{b}}</preserve_or_translate>"
        variables = {"a": "1", "b": "2"}
        result = replace_variables_in_text(text, variables)
        assert result == "<preserve_or_translate>1</preserve_or_translate> and <preserve_or_translate>2</preserve_or_translate>"

    def test_replace_variable_after_preserve_tag(self):
        """Test variable after preserve tag."""
        text = "<preserve_or_translate>{{fixed}}</preserve_or_translate> followed by {{dynamic}}"
        variables = {"fixed": "static", "dynamic": "changing"}
        result = replace_variables_in_text(text, variables)
        assert result == '<preserve_or_translate>static</preserve_or_translate> followed by """changing"""'

    def test_replace_preserve_tag_with_unknown_value(self):
        """Test UNKNOWN value inside preserve tag."""
        text = "<preserve_or_translate>{{missing}}</preserve_or_translate>"
        result = replace_variables_in_text(text, {})
        assert result == "<preserve_or_translate>UNKNOWN</preserve_or_translate>"

    def test_replace_with_none_text(self):
        """Test replacement with None text input."""
        result = replace_variables_in_text(None, {"name": "John"})
        assert result == ""

    def test_replace_with_non_string_text(self):
        """Test replacement with non-string text input."""
        result = replace_variables_in_text(123, {"name": "John"})  # type: ignore[arg-type]
        assert result == 123  # Returns original value if not a string

    def test_replace_list_with_all_none_values(self):
        """Test list with all None or empty values."""
        text = "Items: {{items}}"
        variables = {"items": [None, "", "  ", None]}
        result = replace_variables_in_text(text, variables)
        assert result == 'Items: """UNKNOWN"""'

    def test_replace_without_quotes(self):
        """Test replacement without adding quotes (add_quotes=False)."""
        text = "Hello {{name}}!"
        variables = {"name": "John"}
        result = replace_variables_in_text(text, variables, add_quotes=False)
        assert result == "Hello John!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
