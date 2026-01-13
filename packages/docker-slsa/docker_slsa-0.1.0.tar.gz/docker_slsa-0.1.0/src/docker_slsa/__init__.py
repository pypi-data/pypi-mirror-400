"""Verify SLSA provenance attestations for Docker container images.

This library verifies container images built with the SLSA GitHub Generator
for containers (generator_container_slsa3.yml). It supports verifying individual
images or all images in a docker-compose file.

Verify a single image:

    >>> from docker_slsa import ContainerSLSAVerifier, build_default_policy
    >>>
    >>> verifier = ContainerSLSAVerifier()
    >>> result = verifier.verify(
    ...     image_ref="ghcr.io/org/repo/image@sha256:...",
    ...     policy=build_default_policy("org/repo"),
    ... )

Verify all images in a docker-compose file:

    >>> from docker_slsa import verify_docker_compose_provenance, build_default_policy
    >>>
    >>> result = verify_docker_compose_provenance(
    ...     docker_compose=docker_compose_content,
    ...     service_policies={"web": build_default_policy("org/repo")},
    ...     ignore=["redis"],  # skip third-party images
    ... )

For advanced policies, use sigstore's policy classes directly:

    >>> from sigstore.verify.policy import AllOf, OIDCIssuer, GitHubWorkflowRepository
    >>>
    >>> policy = AllOf([
    ...     OIDCIssuer("https://token.actions.githubusercontent.com"),
    ...     GitHubWorkflowRepository("org/repo"),
    ... ])
"""

import logging
import os

from .errors import ProvenanceVerificationError
from .slsa import (
    ContainerSLSAVerifier,
    VerificationResult,
    build_default_policy,
)
from .utils import _get_provenance_logger
from .verifier import (
    DockerComposeProvenanceVerifier,
    ProvenanceVerificationResult,
    ServiceVerificationResult,
    verify_docker_compose_provenance,
)

logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = _get_provenance_logger()


if os.getenv("DEBUG_PROVENANCE", "").lower() in ("1", "true"):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

__all__ = [
    # Main classes
    "DockerComposeProvenanceVerifier",
    "ContainerSLSAVerifier",
    # Results
    "ProvenanceVerificationResult",
    "ServiceVerificationResult",
    "VerificationResult",
    # Errors
    "ProvenanceVerificationError",
    # Convenience functions
    "verify_docker_compose_provenance",
    "build_default_policy",
]
