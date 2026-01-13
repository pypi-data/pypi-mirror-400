from enum import Enum
from .models import *
from .base_model import Page
from .services.integrations import Integrations
from .services.cves import Cves
from .http_client import ApiKeyAuth

class Server(Enum):
    production_server = 'https://admin.api.crowdsec.net/v1'

__all__ = [
    'Integrations',
    'Cves',
    'ApiKeyCredentials',
    'BasicAuthCredentials',
    'BlocklistSubscription',
    'CVESubscription',
    'HTTPValidationError',
    'IntegrationCreateRequest',
    'IntegrationCreateResponse',
    'IntegrationGetResponse',
    'IntegrationGetResponsePage',
    'IntegrationType',
    'IntegrationUpdateRequest',
    'IntegrationUpdateResponse',
    'Links',
    'OutputFormat',
    'Stats',
    'ValidationError',
    'AffectedComponent',
    'AllowlistSubscription',
    'AttackDetail',
    'Behavior',
    'CVEEvent',
    'CVEResponseBase',
    'CVEsubscription',
    'CWE',
    'Classification',
    'Classifications',
    'EntityType',
    'GetCVEIPsResponsePage',
    'GetCVEResponse',
    'GetCVESubscribedIntegrationsResponsePage',
    'GetCVEsResponsePage',
    'GetCVEsSortBy',
    'GetCVEsSortOrder',
    'History',
    'IPItem',
    'IntegrationResponse',
    'Location',
    'MitreTechnique',
    'Reference',
    'ScoreBreakdown',
    'Scores',
    'SinceOptions',
    'SubscribeCVEIntegrationRequest',
    'TimelineItem',
    'ApiKeyAuth',
    'Server',
    'Page'
]