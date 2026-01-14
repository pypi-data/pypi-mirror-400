# Copyright 2024, MangoBoost, Inc. All rights reserved.

import typing
import datetime
import logging
import requests

from licensing.methods import Key, Helpers
from llmboost_hub.utils.gpu_info import get_curr_gpu_name, get_gpu_count
from llmboost_hub.utils.llmboost_version import __version__ as llmboost_version
from llmboost_hub.utils import signature
from llmboost_hub.utils.config import config

log = logging.getLogger("LICENSE_CHECKER")
log.setLevel(logging.INFO)


def validate_aws() -> bool:
    """
    Validate that the current machine is an authorized AWS Marketplace instance.

    Strategy:
    - Use IMDSv2 to obtain a token and fetch instance-identity document.
    - Ensure 'availabilityZone' exists and marketplace product codes are present.
    - Compare codes against a known bcrypt hash.

    Returns:
        True if the instance passes validation; False otherwise.
    """
    import bcrypt

    log.debug("Checking if the instance is running on AWS...")

    # Used IMDSv2 to get instance metadata
    # Get the auth token
    http_headers = {
        "X-aws-ec2-metadata-token-ttl-seconds": "600",
        "content-type": "application/json",
    }
    auth_token = requests.put(
        "http://169.254.169.254/latest/api/token", headers=http_headers, timeout=1
    ).text

    # Get the instance metadata using the auth token
    http_headers = {
        "X-aws-ec2-metadata-token": auth_token,
        "content-type": "application/json",
    }
    meta = requests.get(
        "http://169.254.169.254/latest/dynamic/instance-identity/document",
        headers=http_headers,
        timeout=1,
    ).json()

    # Check if the instance is running on AWS
    if "availabilityZone" not in meta:
        log.error(
            "The instance is not running on AWS. Please make sure you are running this on an AWS instance."
        )
        return False

    product_code = meta.get("marketplaceProductCodes", None)
    if product_code is None:
        log.error("Please make sure you are running this on an AWS Marketplace instance.")
        return False

    hashed_product_code = b"$2b$12$8CNuFjPv40gs2vNlIG6WGOcLJDDsGVU6rdQefimKT8vgJVvQE6jvq"

    # Iterate all product codes if there are multiple
    for code in product_code:
        code = code.encode()
        if bcrypt.checkpw(code, hashed_product_code):
            log.debug("The instance is running on AWS and has a valid product code.")
            return True

    log.error("Unable to validate LLMBoost Instance")
    return False


def validate_azure() -> bool:
    """
    Validate that the current machine is an authorized Azure Marketplace instance.

    Strategy:
    - Query Azure's instance metadata service.
    - Ensure 'azEnvironment' exists and 'plan.publisher' matches allowed publishers.

    Returns:
        True if the instance passes validation; False otherwise.
    """
    log.debug("Checking if the instance is running on Azure...")

    # Get the instance metadata
    http_headers = {"Metadata": "true"}
    meta = requests.get(
        "http://169.254.169.254/metadata/instance/compute?api-version=2021-02-01",
        headers=http_headers,
        timeout=1,
    ).json()

    # Check if the instance is running on Azure
    if "azEnvironment" not in meta:
        log.error(
            "The instance is not running on Azure. Please make sure you are running this on an Azure instance."
        )
        return False

    plan = meta.get("plan", None)
    if plan is None:
        log.error("Please make sure you are running this on an Azure Marketplace instance.")
        return False

    # Publisher allowlist check
    if plan["publisher"] == "mangoboost" or plan["publisher"] == "mango_solution":
        # TODO: Add a check for the product code
        log.debug("The instance is running on Azure and has a valid product code.")
        return True

    log.error("Unable to validate LLMBoost Instance")
    return False


def validate_gcp() -> bool:
    """
    Validate that the current machine is an authorized GCP instance image.

    Strategy:
    - Query GCP's metadata server for the image path.
    - Ensure it matches the expected prefix 'projects/mangoboost-public/global/images/llmboost'.

    Returns:
        True if the instance passes validation; False otherwise.
    """
    http_headers = {"Metadata-Flavor": "Google"}
    url = "http://metadata.google.internal/computeMetadata/v1/instance/image?alt=text"

    try:
        resp = requests.get(url, headers=http_headers, timeout=5)
    except requests.exceptions.RequestException as e:
        log.error(f"Unable to contact GCP metadata server: {e}")
        return False

    if resp.status_code != 200:
        log.error("Make sure you are running this on a GCP instance.")
        return False

    returned_image = resp.text.strip()
    expected_image = "projects/mangoboost-public/global/images/llmboost"

    if returned_image.startswith(expected_image):
        # Image matches the expected public LLMBoost image
        log.debug("This instance is running on GCP and has a valid LLMBoost image.")
        return True

    log.error(
        f"Invalid image detected. Expected '{expected_image}' but got '{returned_image}'. "
        "Unable to validate LLMBoost license."
    )
    return False


def match_data_obj(data_objects: typing.Iterable, key: str, value: str) -> bool:
    """
    Return True if any data object contains the given Name/StringValue pair.

    Args:
        data_objects: Iterable of data object dicts from the license payload.
        key: Name to match.
        value: StringValue to match.

    Returns:
        True if a matching pair is found; False otherwise.
    """
    for data_object in data_objects:
        if data_object["Name"] == key and data_object["StringValue"] == value:
            return True
    return False


def is_master_license(data: typing.Any) -> bool:
    """
    Determine whether the given license data represents a master license.

    A master license is defined as all feature flags f3..f8 being enabled.

    Args:
        data: License data object returned by the licensing library.

    Returns:
        True if master license; False otherwise.
    """
    if data.f3 and data.f4 and data.f5 and data.f6 and data.f7 and data.f8:
        return True
    return False


def validate_offline(first_attempt: bool = False) -> bool:
    """
    Attempt offline license validation from the local license file.

    Flow:
    - Read the first line from config.LBH_LICENSE_PATH as the license key.
    - Call Key.activate with an empty machine_code (fast path).
    - If expired or invalid -> raise Exception.
    - Master license: accept immediately.
    - Client license: require f3 enabled and version match; then perform a
      second activation with a composite machine_id including build date,
      MAC, GPU count, and GPU name.

    Args:
        first_attempt: If True, suppresses noisy error logging on failure.

    Returns:
        True if license validates offline; False otherwise.

    Raises:
        Exception: For specific invalid/expired/client-invalid conditions.
    """
    RSA_PUBKEY = "<RSAKeyValue><Modulus>v5VwOeHpGJQ4ulX8X+kj3Mg1IKZe5QpIxOifpq0ifxAOOSy7fAFEgSgny5WoaIyc4RFazFJCcz37AhPSzDhyyj48fRMUdEgHD41P3ltWRaQ+ZAecgE/tzEU5TYaZ/ASSvmCOx4FkxjSyufgRJikz9t4Hh1SF6yeHkB7gYr/tXvHQnfUaIzwDBhyL6p4k0Lu5zlFg3xTJIiE7D24Bu+8bdDAHkqXSKxh/qcTqkcMR1ZY4grYHG27uzKmTyYTlISiMaferould6MoELWgvHxCk5IkI8fShDthUI3L+9RKqYvM9/GjfWBcpL7jz1KIFfUFBtfL81Euxr404JWmcKBieOw==</Modulus><Exponent>AQAB</Exponent></RSAKeyValue>"
    auth_token = "WyIxMDI3OTg3MTgiLCIwV1kwWS9QeDVCdmd5N3krT3N0bldTMlB1NzduMjdBSEpXVWJwU2pNIl0="
    product_id = 28771

    with open(config.LBH_LICENSE_PATH, "r") as f:
        # Read and normalize the license key (strip newline/whitespace)
        license_key = f.readline().strip()

        machine_id = ""
        # Quick activation without binding to a specific machine_code first
        result = Key.activate(
            token=auth_token,
            rsa_pub_key=RSA_PUBKEY,
            product_id=product_id,
            key=license_key,
            machine_code=machine_id,
        )

        if result[0] == None:
            # Invalid key OR activation limit reached OR other error
            raise Exception("License key is invalid or cannot be activated.")
        else:
            # Check license expiration
            if result[0].expires < datetime.datetime.now():
                raise Exception("License has expired.")
            else:
                # Master license is for internal use only
                if is_master_license(result[0]):
                    log.info("Master license detected.")
                    return True
                else:
                    # Client license validation
                    # Conditions:
                    # 1) f3 enabled
                    # 2) version in data_objects matches current LLMBoost version
                    if result[0].f3:
                        # Require version match (signature check omitted/commented intentionally)
                        if match_data_obj(result[0].data_objects, "version", llmboost_version):
                            # Perform a second activation that records machine characteristics
                            machine_id = (
                                signature.BUILD_DATE
                                + "||"
                                + Helpers.GetMACAddress()
                                + "||"
                                + str(get_gpu_count())
                                + "||"
                                + get_curr_gpu_name()
                            )
                            # Second activation binds more details server-side
                            result = Key.activate(
                                token=auth_token,
                                rsa_pub_key=RSA_PUBKEY,
                                product_id=product_id,
                                key=license_key,
                                machine_code=machine_id,
                            )
                            return True
                    else:
                        raise Exception("License is not a valid client license.")

    # If no valid license was found
    if not first_attempt:
        log.error("No valid license found in /workspace/*.skm")
    return False


def validate_license() -> bool:
    """
    Validate the license using a multi-stage strategy.

    Order:
    1) Local/offline license validation (fast path).
    2) Cloud vendor checks (AWS -> Azure -> GCP) via instance metadata.

    Returns:
        True if any validation strategy succeeds; False otherwise.
    """
    # Put local license checking first so that we can test on bare instances easily
    local_license = validate_offline(first_attempt=True)

    if local_license:
        return True

    # Check if the instance is running on AWS
    try:
        http_headers = {
            "X-aws-ec2-metadata-token-ttl-seconds": "600",
            "content-type": "application/json",
        }
        r = requests.put("http://169.254.169.254/latest/api/token", headers=http_headers, timeout=1)
        if r.status_code == 200:
            log.debug("The instance is running on AWS.")
            return validate_aws()
    except Exception as e:
        log.debug("The instance is not running on AWS.")

    # Check if the instance is running on Azure
    try:
        http_headers = {"Metadata": "true"}
        r = requests.get(
            "http://169.254.169.254/metadata/instance/compute?api-version=2021-02-01",
            headers=http_headers,
            timeout=1,
        )
        if r.status_code == 200:
            log.debug("The instance is running on Azure.")
            return validate_azure()
    except Exception as e:
        log.debug(f"The instance is not running on Azure.")

    # Check if the instance is running on GCP
    try:
        http_headers = {"Metadata-Flavor": "Google"}
        resp = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project",
            headers=http_headers,
        )
        if resp.status_code == 200:
            log.debug("The instance is running on GCP.")
            return validate_gcp()
    except:
        log.debug("The instance is not running on GCP.")

    # Fallback: none of the validations succeeded
    return False
