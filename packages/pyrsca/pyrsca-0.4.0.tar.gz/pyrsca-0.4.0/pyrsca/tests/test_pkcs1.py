import os
import pytest
from pyrsca import PyTWCA, PySignType


@pytest.fixture
def pfx_path():
    return os.environ.get("PFX_PATH", "Sinopac.pfx")

@pytest.fixture
def password():
    return os.environ.get("PFX_PASSWORD", "")

@pytest.fixture
def twca(pfx_path, password):
    return PyTWCA(pfx_path, password, "192.168.1.1")


def test_get_cert_base64(twca):
    """Test getting base64 encoded certificate"""
    cert_base64 = twca.get_cert_base64()
    assert isinstance(cert_base64, str)
    assert len(cert_base64) > 0
    # Base64 should only contain valid characters
    import base64
    try:
        base64.b64decode(cert_base64)
    except Exception:
        assert False, "Invalid base64 certificate"


def test_sign_pkcs1(twca):
    """Test PKCS1 signature with base64 encoded data and certificate"""
    plain_text = "test message for pkcs1 signing"
    
    # Get PKCS1 signature result
    result = twca.sign_pkcs1(plain_text)
    
    # Verify result is a string
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Verify format is pkcs1.{signature}.{base64_data}.{cert_base64}
    assert result.startswith("pkcs1."), "Result should start with 'pkcs1.'"
    
    parts = result.split('.')
    assert len(parts) == 4, "Result should have 4 parts separated by dots"
    assert parts[0] == "pkcs1", "First part should be 'pkcs1'"
    
    signature = parts[1]
    base64_data = parts[2]
    cert_base64 = parts[3]
    
    # Verify all parts are non-empty
    assert len(signature) > 0
    assert len(cert_base64) > 0
    assert len(base64_data) > 0
    
    # Verify base64 formats
    import base64
    try:
        base64.b64decode(signature)  # Add padding if needed
        base64.b64decode(cert_base64)
        base64.b64decode(base64_data)
    except Exception:
        assert False, "Invalid base64 format in PKCS1 signature result"
    
    # Verify base64_data decodes to expected content format
    decoded_data = base64.b64decode(base64_data).decode('utf-8')
    assert plain_text in decoded_data, "Original plain text should be in the signed data"


def test_pkcs1_vs_pkcs7_signatures(twca):
    """Test that PKCS1 and PKCS7 signatures are different"""
    plain_text = "comparison test message"
    
    # Get PKCS7 signature (existing method)
    pkcs7_signature = twca.sign(plain_text)
    
    # Get PKCS1 signature
    pkcs1_result = twca.sign_pkcs1(plain_text)
    
    # They should be different
    assert pkcs7_signature != pkcs1_result
    
    # Both should be non-empty strings
    assert len(pkcs7_signature) > 0
    assert len(pkcs1_result) > 0
    
    # PKCS1 should start with 'pkcs1.'
    assert pkcs1_result.startswith("pkcs1.")
    
    print(f"PKCS7 signature length: {len(pkcs7_signature)}")
    print(f"PKCS1 result length: {len(pkcs1_result)}")


def test_sign_pkcs7(twca):
    """Test PKCS7 signature with unified output format"""
    plain_text = "test message for pkcs7 signing"

    result = twca.sign_pkcs7(plain_text)

    assert isinstance(result, str)
    assert len(result) > 0
    assert result.startswith("pkcs7."), "Result should start with 'pkcs7.'"

    parts = result.split('.')
    assert len(parts) == 4, "Result should have 4 parts separated by dots"
    assert parts[0] == "pkcs7", "First part should be 'pkcs7'"

    signature = parts[1]
    base64_data = parts[2]
    cert_base64 = parts[3]

    assert len(signature) > 0
    assert len(base64_data) > 0
    assert len(cert_base64) > 0

    import base64
    try:
        base64.b64decode(signature)
        base64.b64decode(base64_data)
        base64.b64decode(cert_base64)
    except Exception:
        assert False, "Invalid base64 format in PKCS7 signature result"

    decoded_data = base64.b64decode(base64_data).decode('utf-8')
    assert plain_text in decoded_data, "Original plain text should be in the signed data"


def test_uni_sign_pkcs1(twca):
    """Test uni_sign with PySignType.Pkcs1"""
    plain_text = "test uni_sign pkcs1"

    result = twca.uni_sign(plain_text, PySignType.Pkcs1)

    assert isinstance(result, str)
    assert result.startswith("pkcs1.")

    parts = result.split('.')
    assert len(parts) == 4
    assert parts[0] == "pkcs1"


def test_uni_sign_pkcs7(twca):
    """Test uni_sign with PySignType.Pkcs7"""
    plain_text = "test uni_sign pkcs7"

    result = twca.uni_sign(plain_text, PySignType.Pkcs7)

    assert isinstance(result, str)
    assert result.startswith("pkcs7.")

    parts = result.split('.')
    assert len(parts) == 4
    assert parts[0] == "pkcs7"


def test_uni_sign_matches_direct_methods(twca):
    """Test that uni_sign produces same format as direct methods"""
    plain_text = "comparison test"

    # uni_sign should produce same format as direct methods
    direct_pkcs1 = twca.sign_pkcs1(plain_text)
    uni_pkcs1 = twca.uni_sign(plain_text, PySignType.Pkcs1)

    # Both should have same prefix and structure
    assert direct_pkcs1.startswith("pkcs1.")
    assert uni_pkcs1.startswith("pkcs1.")
    assert len(direct_pkcs1.split('.')) == len(uni_pkcs1.split('.'))

    direct_pkcs7 = twca.sign_pkcs7(plain_text)
    uni_pkcs7 = twca.uni_sign(plain_text, PySignType.Pkcs7)

    assert direct_pkcs7.startswith("pkcs7.")
    assert uni_pkcs7.startswith("pkcs7.")
    assert len(direct_pkcs7.split('.')) == len(uni_pkcs7.split('.'))


def test_pysigntype_enum():
    """Test PySignType enum values"""
    assert PySignType.Pkcs1 != PySignType.Pkcs7
    assert PySignType.Pkcs1 == PySignType.Pkcs1
    assert PySignType.Pkcs7 == PySignType.Pkcs7 