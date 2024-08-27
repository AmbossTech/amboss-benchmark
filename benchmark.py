import os
import time

from google.protobuf.json_format import MessageToDict
from timeout_decorator import timeout_decorator

from grpc_generated import lightning_pb2 as ln

from pathlib import Path

from lnd import Lnd, route_generator
from api_classes import PathRequest
import logging

from path_adapter import JsonAdapter
from utils import get_top_nodes, query_paths_reflex
from dotenv import load_dotenv

TIME_LIMIT = 60
load_dotenv()


@timeout_decorator.timeout(TIME_LIMIT, timeout_exception=TimeoutError)
def qpr(source, dest, capacity):
    path_request = PathRequest(
        origin=source,
        destination=dest,
        amount=capacity
    )
    start = time.time()
    reflex_path = query_paths_reflex(path_request)
    end = time.time()
    duration = round(end - start, 3)
    if reflex_path:
        path = JsonAdapter(reflex_path)
        return path.get_lnroute(int(path_request.amount)), duration
    else:
        return None, duration


@timeout_decorator.timeout(TIME_LIMIT, timeout_exception=TimeoutError)
def qpl(source, dest, capacity, use_mc=True):
    try:
        start = time.time()
        lnd_route, _ = next(route_generator(source, dest, capacity, use_mc=use_mc))
        end = time.time()
        return lnd_route, round(end - start, 3)
    except:
        return None, 0


@timeout_decorator.timeout(TIME_LIMIT, timeout_exception=TimeoutError)
def try_route(lnd: Lnd, route: ln.Route):
    fee = route.total_fees_msat
    start = time.time()
    payment_request = lnd.pay_fake_invoice(route=route)
    end = time.time()
    probe_time = round(end - start, 3)
    failed_successfully = False
    resp_dict = MessageToDict(payment_request)
    if "IncorrectOrUnknownPaymentDetails" in resp_dict['paymentError']:
        failed_successfully = True
    return fee, failed_successfully, probe_time


def main():
    print("beginning benchmark...", flush=True)
    lnd = Lnd()
    Path('./output').mkdir(exist_ok=True)
    results_filename = f"./output/benchmark_results_{int(time.time())}.csv"
    origin = os.getenv("LND_PUBKEY")
    capacity = 1000
    trials = 1000

    # get pubkeys of the top nodes
    pubkeys = get_top_nodes(limit=trials)
    if origin in pubkeys:
        pubkeys.remove(origin)

    # make the path requests
    path_requests = []
    for dest in pubkeys:
        path_request = PathRequest(
            origin=origin,
            destination=dest,
            amount=capacity,
        )
        path_requests.append(path_request)

    # open(results_filename, "w").close()  # clears file
    logging.basicConfig(filename=results_filename, level=logging.INFO, format='%(message)s')
    logging.info(
        "src, dest, capacity, path_type, path_cost, path_length, ex_time, probe_time, found_path")

    # test the routes as they are generated
    for i, path_request in enumerate(path_requests):
        destination = path_request.destination
        _type = "lnd"
        path, ex_time = qpl(origin, path_request.destination, capacity)
        if path:
            path_length = len(path.hops)
            try:
                path_cost, found_path, probe_time = try_route(lnd, path)
            except TimeoutError:
                path_cost = path.total_fees
                found_path = False
                probe_time = TIME_LIMIT
        else:
            path_cost = 0
            found_path = False
            probe_time = 0
            path_length = 0

        logging.info(
            f"{origin}, {destination}, {capacity}, {_type}, {path_cost}, {path_length}, {ex_time}, {probe_time}, {found_path}")

        _type = "reflex"
        path, ex_time = qpr(origin,
                            path_request.destination,
                            capacity)
        if path:
            path_length = len(path.hops)
            try:
                path_cost, found_path, probe_time = try_route(lnd, path)
            except TimeoutError:
                path_cost = path.total_fees
                found_path = False
                probe_time = TIME_LIMIT
        else:
            path_cost = -1
            found_path = False
            probe_time = -1
            path_length = -1
        logging.info(
            f"{origin}, {destination}, {capacity}, {_type}, {path_cost}, {path_length}, {ex_time}, {probe_time}, {found_path}")
        if (i + 1) % 10 == 0:
            print(f"processed {i + 1} nodes...", flush=True)


if __name__ == '__main__':
    main()
