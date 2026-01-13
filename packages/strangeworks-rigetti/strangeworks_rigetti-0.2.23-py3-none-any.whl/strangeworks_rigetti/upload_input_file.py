import requests
import strangeworks
from strangeworks.core.client.resource import Resource
from strangeworks.core.errors.error import StrangeworksError

import strangeworks_rigetti


def upload_input_file(filename: str, *args, **kwargs):
    data = {
        "object_name": filename,
    }

    # Even though the service endpoint "upload" does not use resource slug info,
    # we still need a resource because the core sdk does not provide a way to
    # make a call to a service without a resource.
    #
    # Get any rigetti resource
    resource: Resource = strangeworks.get_resource_for_product(
        product_slug=strangeworks_rigetti.RIGETTI_PRODUCT_SLUG
    )
    if resource is None:
        # try kernel
        resource = strangeworks.get_resource_for_product(
            strangeworks_rigetti.KERNEL_METHOD_PRODUCT_SLUG
        )
        if resource is None:
            resource = strangeworks.get_resource_for_product(
                strangeworks_rigetti.QNN_PRODUCT_SLUG
            )
            if resource is None:
                raise StrangeworksError(
                    "unable to find an appropriate resource to complete "
                    "this operation. Please create a resource for Rigetti "
                    "and try again. Contact Strangeworks support for further help."
                )

    # TODO: for calls like this one, wneed core sdk to provide an execute method which
    # does not require a user resource.
    results = strangeworks.execute(
        res=resource,
        payload=data,
        endpoint="upload",
    )

    response = results["results"]

    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f)}
            http_response = requests.post(
                response["url"], data=response["fields"], files=files
            )

            return http_response

    except Exception as error:
        return {
            "status_code": 400,
            "content": {
                "message": "Exception occurred during upload",
                "error": f"{error}",
            },
        }
