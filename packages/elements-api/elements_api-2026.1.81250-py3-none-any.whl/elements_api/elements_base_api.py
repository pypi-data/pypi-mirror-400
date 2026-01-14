# Copyright 2017-2021 Orbital Insight Inc., all rights reserved.
# Contains confidential and trade secret information.
# Government Users:  Commercial Computer Software - Use governed by
# terms of Orbital Insight commercial license agreement.

import os
from abc import ABC, abstractmethod
import json
import time
import base64
from typing import Optional
from functools import lru_cache, wraps
import requests

import grpc


API_TOKEN = 'TERRASCOPE_API_TOKEN'


@lru_cache(maxsize=128)
def json_from_jwt(jwt_token: str) -> dict[str, object]:
    # see also similar function in user svc client
    # returns claims dict
    try:
        [_header, payload, _signature] = jwt_token.split('.')
        payload_text = base64.b64decode(payload + "===", '-_')
        payload_json = json.loads(payload_text)
        return payload_json
    except BaseException:
        return {}


def is_token_expiring(jwt_token: str, within_secs=300) -> bool:
    claims = json_from_jwt(jwt_token)
    return claims.get('exp') < time.time() + within_secs


def is_offline_token(jwt_token: str) -> bool:
    claims = json_from_jwt(jwt_token)
    return claims.get('typ') == 'Offline'


def get_token_issuing_client(jwt_token: str):
    claims = json_from_jwt(jwt_token)
    return claims.get('azp')


def check_access_token(func) -> bool:
    # decorator
    @wraps(func)
    def wrapper(*args, **kwargs):  # The instance is passed as the first argument
        self = args[0]
        # check if current access token is expired
        self.refresh_access_token_and_recreate_stubs()
        result = func(self)
        return result
    return wrapper


class ElementsBaseApi(ABC):

    def __init__(self, oi_papi_url: str, port: int = 443, secure=True, api_token: str = None, root_certificates_file=None):
        self._oi_papi_url = oi_papi_url
        self._port = port
        self._secure = secure
        self._root_certificates_file = root_certificates_file
        self._channel = None
        self.api_token: Optional[str] = os.environ.get(API_TOKEN, "").strip() if api_token is None else api_token.strip()
        # check if this is an offline token, which is a refresh token, and obtain access tokens from it periodically
        self.access_token: Optional[str] = self.api_token if not is_offline_token(self.api_token) else None
        self.access_token_expiration_threshold = int(os.getenv('ACCESS_TOKEN_EXPIRATION_THRESHOLD', '300'))
        # (token will be renewed when it has less than this threshhold before expiry)
        self.options = [('grpc.max_send_message_length', -1),
                        ('grpc.max_receive_message_length', -1),
                        ('grpc.max_metadata_size', 16000)]
        service_config_json: str = json.dumps({
            "methodConfig": [{
                "name": [{}],  # Apply retry to all methods by using [{}]
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": "1.0s",
                    "maxBackoff": "60s",
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": ["UNAVAILABLE"],
                },
            }]
        })
        self.options.append(("grpc.service_config", service_config_json))

        self.refresh_access_token()
        self.new_channel()
        self.recreate_stubs()

    def recreate_stubs(self):
        from elements_api import stubs
        # unauthenticated users can access forgot_password
        self._forgot_password = stubs.forgot_password.ForgotPasswordApiStub(self._channel)

        if self.api_token:
            self._algorithm = stubs.algorithm.AlgorithmApiStub(self._channel)
            self._algorithm_version = stubs.algorithm_version.AlgorithmVersionApiStub(self._channel)
            self._algorithm_config = stubs.algorithm_config.AlgorithmConfigApiStub(self._channel)
            self._aoi = stubs.aoi.AOIApiStub(self._channel)
            self._aoi_collection = stubs.aoi_collection.AOICollectionApiStub(self._channel)
            self._aoi_version = stubs.aoi_version.AOIVersionApiStub(self._channel)
            self._aoi_catalog = stubs.aoi_catalog.AOICatalogApiStub(self._channel)
            self._aoi_transaction = stubs.aoi_transaction.AOITransactionApiStub(self._channel)
            self._aoi_export = stubs.aoi_export.AOIExportApiStub(self._channel)
            self._algorithm_computation = stubs.algorithm_computation.AlgorithmComputationApiStub(self._channel)
            self._algorithm_computation_execution = \
                stubs.algorithm_computation_execution.AlgorithmComputationExecutionApiStub(self._channel)
            self._analysis = stubs.analysis.AnalysisApiStub(self._channel)
            self._analysis_version = stubs.analysis_version.AnalysisVersionApiStub(self._channel)
            self._credit = stubs.credit.CreditApiStub(self._channel)
            self._result = stubs.result.ResultApiStub(self._channel)
            self._analysis_config = stubs.analysis_config.AnalysisConfigApiStub(self._channel)
            self._analysis_computation = stubs.analysis_computation.AnalysisComputationApiStub(self._channel)
            self._system = stubs.system.SystemApiStub(self._channel)
            self._toi = stubs.toi.TOIApiStub(self._channel)
            self._permission = stubs.permission.PermissionApiStub(self._channel)
            self._user = stubs.user.UserApiStub(self._channel)
            self._user_collection = stubs.user_collection.UserCollectionApiStub(self._channel)
            self._token = stubs.token.TokenApiStub(self._channel)
            self._visualization = stubs.visualization.VisualizationApiStub(self._channel)
            self._tile = stubs.tile.TileApiStub(self._channel)
            self._notification = stubs.notification.NotificationApiStub(self._channel)
            self._data_source = stubs.data_source.DataSourceAPIStub(self._channel)
            self._data_type = stubs.data_type.DataTypeAPIStub(self._channel)
            self._data_tracking = stubs.data_tracking.DataTrackingApiStub(self._channel)
            self._project = stubs.project.ProjectApiStub(self._channel)
            self._project_analysis_config = stubs.project_analysis_config.ProjectAnalysisConfigApiStub(self._channel)
            self._project_collaborator = stubs.project_collaborator.ProjectCollaboratorApiStub(self._channel)
            self._project_group = stubs.project_group.ProjectGroupApiStub(self._channel)
            self._project_result = stubs.project_result.ProjectResultApiStub(self._channel)
            self._project_filter = stubs.project_filter.ProjectFilterApiStub(self._channel)
            self._filter = stubs.filter.FilterApiStub(self._channel)
            self._project_aoi = stubs.project_aoi.ProjectAOIApiStub(self._channel)
            self._order = stubs.order.OrderApiStub(self._channel)
            self._order_recommendation = stubs.order_recommendation.OrderRecommendationApiStub(self._channel)
            self._tasking_order = stubs.tasking_order.TaskingOrderApiStub(self._channel)
            self._provider_quotas = stubs.provider_quotas.ProviderQuotasApiStub(self._channel)
            self._resource = stubs.resource.ResourceApiStub(self._channel)
            self._s3 = stubs.s3.S3ApiStub(self._channel)

    def new_channel(self):
        # if self._channel is not None:
        #     self._channel.close() # todo this is async, and channel.__del__ takes care of it
        self._channel = self._get_channel(
            self._get_ssl_channel_credentials(
                self._secure,
                root_certificates_file=self._root_certificates_file))
        return self._channel

    def refresh_access_token(self) -> bool:
        """
        Refreshes the access token if it is expired.
        returns True if the access token was refreshed, False otherwise.
        """
        # check if current access token is expired
        if self.api_token and not is_offline_token(self.api_token):
            return False  # in which case it is an access token, and it was not refreshed
        # check expiration on the access_token
        if self.access_token and not is_token_expiring(
            self.access_token,
            within_secs=self.access_token_expiration_threshold
        ):
            return False

        oidc_base_url = os.getenv(
            'OIDC_BASE_URL',
            'https://keycloak.orbitalinsight.com')
        oidc_realm = os.getenv('OIDC_REALM', 'elements')
        oidc_token_endpoint = os.getenv(
            'OIDC_TOKEN_ENDPOINT',
            f'{oidc_base_url}/realms/{oidc_realm}/protocol/openid-connect/token')

        # note: api token is an offline token, which is a special refresh token.
        oidc_client_id = get_token_issuing_client(self.api_token)
        # there will be no secret since typically a login client issues this token

        request_json = {
            'refresh_token': self.api_token,
            'client_id': oidc_client_id,
            'grant_type': 'refresh_token',
            'scope': 'openid offline_access'
        }

        response = requests.post(
            oidc_token_endpoint,
            data=request_json,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if not response.ok:
            raise Exception(f"Failed to refresh token: {response.text}")

        self.access_token = response.json().get('access_token')
        return True

    def refresh_access_token_and_recreate_stubs(self) -> bool:
        # check if current access token is expired
        if not self.refresh_access_token():
            return False
        self.new_channel()
        self.recreate_stubs()
        return True
    # individual api accessors are properties, since underlying channel may need to change
    # at any time due to its token change. Do not store property result in a variable,
    # as it will not be refreshed automatically when the token changes
    # token freshness is checked in every call, then if it expired and changed,
    # (all) stubs are regenerated. A new channel is created with that token in each stub

    @property
    @check_access_token
    def forgot_password(self):
        return self._forgot_password

    @property
    @check_access_token
    def algorithm(self):
        return self._algorithm

    @property
    @check_access_token
    def algorithm_version(self):
        return self._algorithm_version

    @property
    @check_access_token
    def algorithm_config(self):
        return self._algorithm_config

    @property
    @check_access_token
    def aoi(self):
        return self._aoi

    @property
    @check_access_token
    def aoi_collection(self):
        return self._aoi_collection

    @property
    @check_access_token
    def aoi_version(self):
        return self._aoi_version

    @property
    @check_access_token
    def aoi_catalog(self):
        return self._aoi_catalog

    @property
    @check_access_token
    def aoi_transaction(self):
        return self._aoi_transaction

    @property
    @check_access_token
    def aoi_export(self):
        return self._aoi_export

    @property
    @check_access_token
    def algorithm_computation(self):
        return self._algorithm_computation

    @property
    @check_access_token
    def algorithm_computation_execution(self):
        return self._algorithm_computation_execution

    @property
    @check_access_token
    def analysis(self):
        return self._analysis

    @property
    @check_access_token
    def analysis_version(self):
        return self._analysis_version

    @property
    @check_access_token
    def credit(self):
        return self._credit

    @property
    @check_access_token
    def result(self):
        return self._result

    @property
    @check_access_token
    def analysis_config(self):
        return self._analysis_config

    @property
    @check_access_token
    def analysis_computation(self):
        return self._analysis_computation

    @property
    @check_access_token
    def system(self):
        return self._system

    @property
    @check_access_token
    def toi(self):
        return self._toi

    @property
    @check_access_token
    def permission(self):
        return self._permission

    @property
    @check_access_token
    def user(self):
        return self._user

    @property
    @check_access_token
    def user_collection(self):
        return self._user_collection

    @property
    @check_access_token
    def token(self):
        return self._token

    @property
    @check_access_token
    def visualization(self):
        return self._visualization

    @property
    @check_access_token
    def tile(self):
        return self._tile

    @property
    @check_access_token
    def notification(self):
        return self._notification

    @property
    @check_access_token
    def data_source(self):
        return self._data_source

    @property
    @check_access_token
    def data_type(self):
        return self._data_type

    @property
    @check_access_token
    def data_tracking(self):
        return self._data_tracking

    @property
    @check_access_token
    def project(self):
        return self._project

    @property
    @check_access_token
    def project_analysis_config(self):
        return self._project_analysis_config

    @property
    @check_access_token
    def project_collaborator(self):
        return self._project_collaborator

    @property
    @check_access_token
    def project_group(self):
        return self._project_group

    @property
    @check_access_token
    def project_result(self):
        return self._project_result

    @property
    @check_access_token
    def project_filter(self):
        return self._project_filter

    @property
    @check_access_token
    def filter(self):
        return self._filter

    @property
    @check_access_token
    def project_aoi(self):
        return self._project_aoi

    @property
    @check_access_token
    def order(self):
        return self._order

    @property
    @check_access_token
    def order_recommendation(self):
        return self._order_recommendation

    @property
    @check_access_token
    def tasking_order(self):
        return self._tasking_order

    @property
    @check_access_token
    def provider_quotas(self):
        return self._provider_quotas

    @property
    @check_access_token
    def provider(self):
        return self._provider

    @property
    @check_access_token
    def resource(self):
        return self._resource

    @property
    @check_access_token
    def s3(self):
        return self._s3

    def _get_ssl_channel_credentials(self, secure, root_certificates_file=None):
        # note: with all defaults, gRPC will search for cert as described here:
        #  https://github.com/grpc/grpc/blob/7a63bd5407d5e14b30f19a5aaf4b6cd1b80f00e1/include/grpc/grpc_security.h#L287
        # for local env, use local_channel_credentials:
        #  https://grpc.github.io/grpc/python/grpc.html#grpc.local_channel_credentials
        if secure:
            root_certificates = None
            if root_certificates_file:
                with open(root_certificates_file, 'rb') as file:
                    root_certificates = file.read()

            return grpc.ssl_channel_credentials(root_certificates=root_certificates,
                                                private_key=None, certificate_chain=None)
        return grpc.local_channel_credentials()

    @abstractmethod
    def _get_channel(self, channel_credentials: grpc.ChannelCredentials):
        ...
