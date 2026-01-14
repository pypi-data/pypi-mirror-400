# Copyright 2017-2021 Orbital Insight Inc., all rights reserved.
# Contains confidential and trade secret information.
# Government Users:  Commercial Computer Software - Use governed by
# terms of Orbital Insight commercial license agreement.


# TODO:
# add retry
# handle exceptions
# add custom logic (request_id, ....)

import grpc
from elements_api.elements_base_api import ElementsBaseApi
from elements_api import models


class ElementsSyncClient:
    def __init__(self, oi_papi_url, port=443, secure=True, api_token=None):
        self.api = ElementsSyncApi(oi_papi_url, port, secure, api_token=api_token)
        self.models = models


class ElementsSyncApi(ElementsBaseApi):

    def _get_channel(self, channel_credentials: grpc.ChannelCredentials):
        token_creds = grpc.access_token_call_credentials(self.access_token)
        creds = grpc.composite_channel_credentials(channel_credentials, token_creds)
        return grpc.secure_channel(f"{self._oi_papi_url}:{self._port}",
                                   creds,
                                   options=self.options,
                                   compression=None)

    def __del__(self):
        self._channel.close()
