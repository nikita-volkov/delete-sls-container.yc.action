#!/usr/bin/env python3
import json
import logging
import os
import sys

import grpc
import yandexcloud
from yandex.cloud.serverless.apigateway.v1.apigateway_pb2 import (
    ApiGateway
)
from yandex.cloud.serverless.apigateway.v1.apigateway_service_pb2_grpc import ApiGatewayServiceStub
from yandex.cloud.serverless.containers.v1.container_service_pb2 import (
    ListContainersRequest,
    ListContainersResponse,
    DeleteContainerRequest
)
from yandex.cloud.serverless.containers.v1.container_service_pb2_grpc import ContainerServiceStub

# Helper for identifying the container by name.
# We're not using it yet.
def find_container(container_service, folder_id: str, name: str):
    list_resp: ListContainersResponse = container_service.List(
        ListContainersRequest(
            folder_id=folder_id,
            filter='name="' + name + '"'
        )
    )
    containers = list_resp.containers
    match len(containers):
        case 1:
            return containers[0]
        case 0:
            raise Exception("No container found with name {} in folder {}".format(name, folder_id))
        case _:
            raise Exception("Too many containers found with name {} in folder {}: {}".format(name, folder_id, containers))


def delete_container(sdk: yandexcloud.SDK, container_service, container_id):
    sdk.wait_operation_and_get_result(container_service.Delete(DeleteContainerRequest(
        container_id=container_id
    )))


def main():
    logging.basicConfig(level=logging.INFO)
    container_id = sys.argv[1]
    sa_key_str = sys.argv[2]
    sa_key = json.loads(sa_key_str)

    interceptor = yandexcloud.RetryInterceptor(max_retry_count=5, retriable_codes=[grpc.StatusCode.UNAVAILABLE])
    sdk = yandexcloud.SDK(interceptor=interceptor, service_account_key=sa_key)
    container_service = ContainerServiceStub(sdk._channels.channel("serverless-containers"))

    delete_container(sdk, container_service, container_id)


if __name__ == '__main__':
    main()
