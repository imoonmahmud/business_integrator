import pytest
import lesson0

with pytest.raises(ValueError):
    lesson0.transform_user({'email': '    '})