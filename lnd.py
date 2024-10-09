"""
Module for interacting with the Lightning Network Daemon (LND) for route generation and invoice
decoding.

This module provides functionality to generate routes for payments within the Lightning Network
using the LND's gRPC interface. It also includes capabilities to decode payment requests (invoices)
 to extract essential details needed for processing payments.
"""

import base64
import hashlib
import os

import grpc
from dotenv import load_dotenv

from grpc_generated import lightning_pb2_grpc, lightning_pb2 as ln
from grpc_generated import router_pb2_grpc as routerrpc


def route_generator(source, target, capacity, num_routes=1, use_mc=True):
    """
    Generate routes for payments in the Lightning Network.

    This generator function interacts with the LND gRPC interface to yield possible
    routes for a given payment from a source to a target with a specified capacity.
    It can generate multiple routes based on the num_routes parameter.

    Args:
        source (str): The public key of the source node.
        target (str): The public key of the destination node.
        capacity (int): The amount in satoshis to be sent.
        num_routes (int): The number of routes to generate.

    Yields:
        tuple: A tuple containing:
               - route (dict): The route details if available, otherwise None.
               - error (str): An error message if an error occurred, otherwise None.
    """
    lnd = Lnd()
    try:
        for _ in range(num_routes):
            # fee limit is not specified, so default fee is used: 100% if >1000k, else 5%
            yield (lnd.query_routes(amt_sats=capacity,
                                    source_pub_key=source,
                                    dest_pub_key=target,
                                    use_mc=use_mc).routes[0], None)
    except Exception as err:
        return None, err
    return None, None


def make_random_hash():
    """
    Generate a random hash using SHA-256 and encode it in base64.

    This function generates a random 16-byte hash using the os.urandom() function,
    then computes the SHA-256 hash of the random bytes. The hash is then encoded in base64.

    Returns:
        str: The base64-encoded hash of the random bytes.
    """
    random_bytes = os.urandom(16)
    hash_value = hashlib.sha256(random_bytes).digest()
    base64_encoded = base64.b64encode(hash_value)
    return base64_encoded


class Lnd:
    """
    Interact with the Lightning Network Daemon (LND) for route generation and invoice decoding.
    """

    def __init__(self) -> None:
        os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
        load_dotenv()
        macaroon_hex = os.getenv("MACAROON_HEX")
        lnd_endpoint = os.getenv("LND_SOCKET")

        def metadata_callback(_, callback):
            callback([('macaroon', macaroon_hex)], None)

        # Use macaroon hex and root certificate
        auth_creds = grpc.metadata_call_credentials(metadata_callback)

        # Create SSL credentials, optionally loading from a provided certificate
        tls_cert_path = "/app/tls.cert"
        if os.path.isfile(tls_cert_path):
            with open(tls_cert_path, 'rb') as tls_cert_file:
                tls_cert = tls_cert_file.read()
            ssl_creds = grpc.ssl_channel_credentials(root_certificates=tls_cert)
        else:
            ssl_creds = grpc.ssl_channel_credentials()

        combined_creds = grpc.composite_channel_credentials(ssl_creds, auth_creds)
        channel = grpc.secure_channel(lnd_endpoint, combined_creds)
        self.stub = lightning_pb2_grpc.LightningStub(channel)  # type: ignore
        self.routerstub = routerrpc.RouterStub(channel)  # type: ignore

    def pay_fake_invoice(self, route):
        """
        Simulate a payment to a fake invoice by sending a payment to a specified
        destination public key with a given amount.
        Optionally, specify an outgoing channel ID to use for the payment.

        Args:
            dest_pubkey (str): The destination public key to which the payment should be sent.
            amount (int): The amount in satoshis to send.
            outgoing_chan_id (Optional[int]): The channel ID to use for sending the payment.

        Returns:
            ln.SendResponse: The response from the LND server after attempting the payment.
        """
        res = self.stub.SendToRouteSync(
            ln.SendToRouteRequest(payment_hash=make_random_hash(),
                                  route=route)  # [no-member]
        )  # [no-member]
        return res

    def query_routes(self, amt_sats, dest_pub_key, **kwargs):
        """
        Query the LND for routes to a specified destination public key.

        Args:
            amt_sats (int): The amount in satoshis to send.
            dest_pub_key (str): The destination public key to which the payment should be sent.
            **kwargs: Additional keyword arguments for customizing the route query.

        Returns:
            ln.QueryRoutesResponse: The response from the LND server containing the routes.
        """
        source_pub_key = kwargs.get("source_pub_key")
        use_mc = kwargs.get("use_mc", True)
        request = ln.QueryRoutesRequest(
            pub_key=dest_pub_key,
            source_pub_key=source_pub_key,
            amt=amt_sats,
            use_mission_control=use_mc
        )  # pylint: disable=no-member

        # Call the QueryRoutes RPC method
        response = self.stub.QueryRoutes(request)
        return response
