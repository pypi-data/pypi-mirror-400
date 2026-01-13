from enum import Enum

# Invalid value can cause ValueError: 'local1' is not a valid EnvironmentName
# In TypeScript we call it EnvionmentNameEnum
class EnvironmentName(Enum):
    LOCAL = "local"
    LOCAL1 = "local1"
    PLAY1 = "play1"
    DVLP1 = "dvlp1"
    PROD1 = "prod1"

    PLAY1_S3_UNSECURED = ("play1-s3-unsecured",)
    PLAY1_S3_SECURED = ("play1-s3-secured",)
    PLAY1_CLOUDFRONT = ("play1-cloudfront",)
    PLAY1_CIRC_ZONE_NO_SSL = ("play1-circ-zone-no-ssl",)
    PLAY1_CIRC_ZONE_SSL = ("play1-circ-zone-ssl",)
    DVLP1_S3_UNSECURED = ("dvlp1-s3-unsecured",)
    DVLP1_CLOUDFRONT = ("dvlp1-cloudfront",)
    DVLP1_CIRC_ZONE_SSL = ("dvlp1-circ-zone-ssl",)
    CIRC_ZONE_SSL = ("circ-zone-ssl",)
