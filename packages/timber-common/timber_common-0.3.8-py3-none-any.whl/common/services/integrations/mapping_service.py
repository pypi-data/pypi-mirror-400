# common/services/integrations/mapping_service.py
"""
Field Mapping Service

Handles:
- Request body construction from input data
- Response data transformation and extraction
- Field validation
- Type conversion
- Custom transformations
"""

from __future__ import annotations
import re
import json
import logging
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union, Callable
from functools import lru_cache

from .models import (
    FieldMapping,
    FieldType,
    BodyConfig,
    ResponseMappingConfig,
    ParamDefinition,
)

logger = logging.getLogger(__name__)


# =============================================================================
# BUILT-IN TRANSFORMERS
# =============================================================================

def strip_percent(value: str) -> float:
    """Strip % sign and convert to float."""
    if isinstance(value, str):
        return float(value.replace('%', '').strip())
    return float(value)


def format_phone_e164(value: str) -> str:
    """Format phone number to E.164 format."""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', value)
    
    # Assume US if 10 digits
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif not digits.startswith('+'):
        return f"+{digits}"
    return digits


def to_uppercase(value: str) -> str:
    """Convert to uppercase."""
    return str(value).upper()


def to_lowercase(value: str) -> str:
    """Convert to lowercase."""
    return str(value).lower()


def trim(value: str) -> str:
    """Trim whitespace."""
    return str(value).strip()


def default_if_empty(value: Any, default: Any = None) -> Any:
    """Return default if value is empty."""
    if value is None or value == '' or value == []:
        return default
    return value


def parse_date(value: str, format: str = "%Y-%m-%d") -> date:
    """Parse string to date."""
    if isinstance(value, date):
        return value
    return datetime.strptime(value, format).date()


def format_date(value: Union[date, datetime], format: str = "%Y-%m-%d") -> str:
    """Format date to string."""
    return value.strftime(format)


def parse_datetime(value: str, format: str = "iso8601") -> datetime:
    """Parse string to datetime."""
    if isinstance(value, datetime):
        return value
    if format == "iso8601":
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    return datetime.strptime(value, format)


def to_boolean(value: Any) -> bool:
    """Convert to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on')
    return bool(value)


def to_integer(value: Any) -> int:
    """Convert to integer."""
    if isinstance(value, str):
        # Remove commas and other formatting
        value = re.sub(r'[,\s]', '', value)
    return int(float(value))


def to_decimal(value: Any) -> Decimal:
    """Convert to decimal."""
    if isinstance(value, str):
        value = re.sub(r'[,\s$€£]', '', value)
    return Decimal(str(value))


def json_parse(value: str) -> Any:
    """Parse JSON string."""
    return json.loads(value)


def json_stringify(value: Any) -> str:
    """Convert to JSON string."""
    return json.dumps(value)


def base64_encode(value: Union[str, bytes]) -> str:
    """Encode to base64."""
    import base64
    if isinstance(value, str):
        value = value.encode()
    return base64.b64encode(value).decode()


def base64_decode(value: str) -> bytes:
    """Decode from base64."""
    import base64
    return base64.b64decode(value)


def email_to_recipients(emails: List[str]) -> List[Dict[str, Any]]:
    """Convert email list to MS Graph recipient format."""
    return [
        {"emailAddress": {"address": email}}
        for email in emails
    ]


def base64_attachments(attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert attachments to MS Graph format."""
    result = []
    for att in attachments:
        result.append({
            "@odata.type": "#microsoft.graph.fileAttachment",
            "name": att.get('name', 'attachment'),
            "contentType": att.get('content_type', 'application/octet-stream'),
            "contentBytes": att.get('content_base64', ''),
        })
    return result


# Transformer registry
TRANSFORMERS: Dict[str, Callable] = {
    'strip_percent': strip_percent,
    'format_phone_e164': format_phone_e164,
    'to_uppercase': to_uppercase,
    'to_lowercase': to_lowercase,
    'trim': trim,
    'default_if_empty': default_if_empty,
    'parse_date': parse_date,
    'format_date': format_date,
    'parse_datetime': parse_datetime,
    'to_boolean': to_boolean,
    'to_integer': to_integer,
    'to_decimal': to_decimal,
    'json_parse': json_parse,
    'json_stringify': json_stringify,
    'base64_encode': base64_encode,
    'base64_decode': base64_decode,
    'email_to_recipients': email_to_recipients,
    'base64_attachments': base64_attachments,
}


def register_transformer(name: str, func: Callable):
    """Register a custom transformer."""
    TRANSFORMERS[name] = func
    logger.debug(f"Registered transformer: {name}")


# =============================================================================
# MAPPING SERVICE
# =============================================================================

class MappingService:
    """
    Service for mapping data between formats.
    """
    
    def __init__(self):
        self._transformers = TRANSFORMERS.copy()
    
    def register_transformer(self, name: str, func: Callable):
        """Register a custom transformer."""
        self._transformers[name] = func
    
    # =========================================================================
    # REQUEST BODY BUILDING
    # =========================================================================
    
    def build_request_body(
        self,
        body_config: BodyConfig,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build request body from input data using mapping configuration.
        
        Args:
            body_config: Body configuration with mappings
            input_data: Input data to map from
            
        Returns:
            Constructed request body
        """
        # Start with template
        body = body_config.template.copy() if body_config.template else {}
        
        # Process mappings
        mapped_fields = {}
        for mapping in body_config.mapping:
            value = self._extract_value(input_data, mapping.source)
            
            # Apply required validation
            if mapping.required and value is None:
                raise ValueError(f"Required field missing: {mapping.source}")
            
            if value is None:
                if mapping.default is not None:
                    value = mapping.default
                else:
                    continue
            
            # Apply validation
            if mapping.validation:
                self._validate_value(value, mapping.validation, mapping.source)
            
            # Apply transformation
            if mapping.transform:
                value = self._apply_transform(value, mapping.transform)
            
            # Apply type conversion
            value = self._convert_type(value, mapping.type, mapping.format)
            
            # Handle special __custom__ target for pass-through
            if mapping.target == '__custom__' and isinstance(value, dict):
                mapped_fields.update(value)
            else:
                mapped_fields[mapping.target] = value
        
        # Handle wrapper (e.g., HubSpot's {properties: fields})
        if body_config.wrapper:
            for wrapper_key, wrapper_value in body_config.wrapper.items():
                if wrapper_value == '__fields__':
                    body[wrapper_key] = mapped_fields
                else:
                    body[wrapper_key] = wrapper_value
        else:
            # Merge mapped fields into body
            self._deep_merge(body, self._unflatten_dict(mapped_fields))
        
        return body
    
    def build_query_params(
        self,
        static_params: Dict[str, Any],
        dynamic_params: List[ParamDefinition],
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build query parameters from input data.
        
        Args:
            static_params: Static parameters always included
            dynamic_params: Dynamic parameter definitions
            input_data: Input data to extract from
            
        Returns:
            Query parameters dictionary
        """
        params = static_params.copy()
        
        for param_def in dynamic_params:
            value = input_data.get(param_def.name)
            
            if value is None:
                if param_def.required:
                    raise ValueError(f"Required parameter missing: {param_def.name}")
                elif param_def.default is not None:
                    value = param_def.default
                else:
                    continue
            
            # Handle array types
            if param_def.type == 'array' and isinstance(value, list):
                delimiter = param_def.delimiter or ','
                value = delimiter.join(str(v) for v in value)
            
            # Handle date formatting
            if param_def.type == 'date' and param_def.format:
                if isinstance(value, (date, datetime)):
                    value = value.strftime(param_def.format)
            
            # Validate
            if param_def.validation:
                self._validate_value(value, param_def.validation, param_def.name)
            
            params[param_def.name] = value
        
        return params
    
    def build_path(
        self,
        path_template: str,
        path_params: List[ParamDefinition],
        input_data: Dict[str, Any],
    ) -> str:
        """
        Build URL path with path parameters.
        
        Args:
            path_template: Path with {param} placeholders
            path_params: Path parameter definitions
            input_data: Input data to extract from
            
        Returns:
            Constructed path
        """
        path = path_template
        
        for param_def in path_params:
            placeholder = f"{{{param_def.name}}}"
            if placeholder in path:
                value = input_data.get(param_def.name)
                
                if value is None:
                    if param_def.required:
                        raise ValueError(f"Required path parameter missing: {param_def.name}")
                    elif param_def.default is not None:
                        value = param_def.default
                
                if value is not None:
                    path = path.replace(placeholder, str(value))
        
        return path
    
    # =========================================================================
    # RESPONSE MAPPING
    # =========================================================================
    
    def map_response(
        self,
        response_data: Any,
        mapping_config: ResponseMappingConfig,
    ) -> Any:
        """
        Map response data using configuration.
        
        Args:
            response_data: Raw response data
            mapping_config: Mapping configuration
            
        Returns:
            Mapped data
        """
        # Extract from root path
        data = response_data
        if mapping_config.root_path:
            data = self._extract_value(response_data, mapping_config.root_path)
        
        if data is None:
            return None
        
        # Handle different response types
        if mapping_config.type == 'array':
            if not isinstance(data, list):
                data = [data]
            return [
                self._map_object(item, mapping_config.fields)
                for item in data
            ]
        
        elif mapping_config.type == 'time_series':
            # Special handling for date-keyed objects (like Alpha Vantage)
            return self._map_time_series(data, mapping_config.fields)
        
        else:  # object
            return self._map_object(data, mapping_config.fields)
    
    def _map_object(
        self,
        data: Dict[str, Any],
        field_mappings: List[FieldMapping],
    ) -> Dict[str, Any]:
        """Map a single object using field mappings."""
        result = {}
        
        for mapping in field_mappings:
            value = self._extract_value(data, mapping.source)
            
            if value is None:
                if mapping.default is not None:
                    value = mapping.default
                else:
                    continue
            
            # Apply transformation
            if mapping.transform:
                value = self._apply_transform(value, mapping.transform)
            
            # Apply type conversion
            value = self._convert_type(value, mapping.type, mapping.format)
            
            result[mapping.target] = value
        
        return result
    
    def _map_time_series(
        self,
        data: Dict[str, Dict],
        field_mappings: List[FieldMapping],
    ) -> List[Dict[str, Any]]:
        """Map time series data (date-keyed objects)."""
        result = []
        
        for date_key, values in data.items():
            mapped = {'date': date_key}
            mapped.update(self._map_object(values, field_mappings))
            result.append(mapped)
        
        # Sort by date descending
        result.sort(key=lambda x: x['date'], reverse=True)
        
        return result
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _extract_value(
        self,
        data: Any,
        path: str,
    ) -> Any:
        """
        Extract value from nested data using dot notation path.
        
        Supports:
        - Simple paths: "field"
        - Nested paths: "field.nested.value"
        - Array access: "field[0].value"
        """
        if data is None:
            return None
        
        parts = self._parse_path(path)
        current = data
        
        for part in parts:
            if current is None:
                return None
            
            # Handle array index
            if isinstance(part, int):
                if isinstance(current, (list, tuple)) and part < len(current):
                    current = current[part]
                else:
                    return None
            # Handle dict key
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        
        return current
    
    def _parse_path(self, path: str) -> List[Union[str, int]]:
        """Parse path string into parts."""
        parts = []
        # Split on dots, handling array notation
        for segment in re.split(r'\.', path):
            # Check for array notation: field[0]
            match = re.match(r'(.+?)\[(\d+)\]$', segment)
            if match:
                parts.append(match.group(1))
                parts.append(int(match.group(2)))
            else:
                parts.append(segment)
        return parts
    
    def _unflatten_dict(self, flat: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flat dict with dot notation to nested dict."""
        result = {}
        
        for key, value in flat.items():
            parts = key.split('.')
            current = result
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result
    
    def _deep_merge(self, target: Dict, source: Dict):
        """Deep merge source into target."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _apply_transform(self, value: Any, transform_name: str) -> Any:
        """Apply a named transformation."""
        transformer = self._transformers.get(transform_name)
        
        if transformer:
            try:
                return transformer(value)
            except Exception as e:
                logger.warning(f"Transform {transform_name} failed: {e}")
                return value
        else:
            logger.warning(f"Unknown transformer: {transform_name}")
            return value
    
    def _convert_type(
        self,
        value: Any,
        target_type: FieldType,
        format_str: Optional[str] = None,
    ) -> Any:
        """Convert value to target type."""
        if value is None:
            return None
        
        try:
            if target_type == FieldType.STRING:
                return str(value)
            
            elif target_type == FieldType.INTEGER:
                return to_integer(value)
            
            elif target_type == FieldType.DECIMAL:
                return float(to_decimal(value))
            
            elif target_type == FieldType.BOOLEAN:
                return to_boolean(value)
            
            elif target_type == FieldType.DATE:
                if isinstance(value, str):
                    return parse_date(value, format_str or "%Y-%m-%d")
                return value
            
            elif target_type == FieldType.DATETIME:
                if isinstance(value, str):
                    return parse_datetime(value, format_str or "iso8601")
                return value
            
            elif target_type in (FieldType.ARRAY, FieldType.OBJECT):
                return value
            
            else:
                return value
                
        except Exception as e:
            logger.warning(f"Type conversion failed for {target_type}: {e}")
            return value
    
    def _validate_value(
        self,
        value: Any,
        validation: Dict[str, Any],
        field_name: str,
    ):
        """Validate a value against validation rules."""
        if 'pattern' in validation:
            pattern = validation['pattern']
            if not re.match(pattern, str(value)):
                raise ValueError(
                    f"Field {field_name} does not match pattern: {pattern}"
                )
        
        if 'max_length' in validation:
            if len(str(value)) > validation['max_length']:
                raise ValueError(
                    f"Field {field_name} exceeds max length: {validation['max_length']}"
                )
        
        if 'min' in validation:
            if float(value) < validation['min']:
                raise ValueError(
                    f"Field {field_name} below minimum: {validation['min']}"
                )
        
        if 'max' in validation:
            if float(value) > validation['max']:
                raise ValueError(
                    f"Field {field_name} exceeds maximum: {validation['max']}"
                )


# Singleton instance
mapping_service = MappingService()
