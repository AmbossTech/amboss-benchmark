from math import ceil

from grpc_generated import lightning_pb2 as ln
from utils import convert_short_channel_id


class CommonPath:
    def get_route(self, sat_amt):
        pass

    def get_lnroute(self, sat_amt):
        pass


class JsonAdapter(CommonPath):
    def __init__(self, json_path):
        self.json_path = json_path

    def get_lnroute(self, sat_amt, final_cltv_delta=80):
        hops = []
        total_timelock = self.json_path['timeout']
        total_fee_msat = 0
        relationships = self.json_path['hops']
        pathlen = len(relationships)
        for i in range(pathlen):
            props = relationships[i]
            end_node_pubkey = props['public_key']
            chan_id = props['channel']
            capacity = props['channel_capacity']
            fee_sat = props['fee']
            fee_msat = props['fee_mtokens']
            amt_to_forward = props['forward']
            amt_to_forward_msat = props['forward_mtokens']
            outgoing_timelock = props['timeout']
            total_fee_msat += int(fee_msat)
            hop = ln.Hop(chan_id=convert_short_channel_id(chan_id),
                         chan_capacity=capacity,
                         fee=int(fee_sat),
                         fee_msat=int(fee_msat),
                         amt_to_forward=amt_to_forward,
                         amt_to_forward_msat=int(amt_to_forward_msat),
                         pub_key=end_node_pubkey,
                         expiry=outgoing_timelock)
            hops.append(hop)
        fee = self.json_path['fee']
        fee_sat = int(fee)
        fee_msat = int(total_fee_msat)
        tokens = sat_amt + fee_sat
        mtokens = (sat_amt * 1000) + (total_fee_msat)
        route = ln.Route(hops=hops,
                         total_fees=fee_sat,
                         total_fees_msat=fee_msat,
                         total_amt=tokens,
                         total_amt_msat=ceil(mtokens),
                         total_time_lock=total_timelock)

        return route
