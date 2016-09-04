import pytest
import random
import gevent
from flaky import flaky


@flaky(max_runs=3)
@pytest.mark.parametrize('call_as_instance', (True, False))
def test_past_events_filter_with_callback(web3_empty,
                                          emitter,
                                          Emitter,
                                          wait_for_transaction,
                                          emitter_log_topics,
                                          emitter_event_ids,
                                          LogTopics,
                                          call_as_instance):
    web3 = web3_empty

    txn_hash = emitter.transact().logNoArgs(emitter_event_ids.LogNoArguments)
    txn_receipt = wait_for_transaction(web3, txn_hash)

    seen_logs = []

    if call_as_instance:
        filter = emitter.pastEvents('LogNoArguments', {}, seen_logs.append)
    else:
        filter = Emitter.pastEvents('LogNoArguments', {}, seen_logs.append)

    with gevent.Timeout(5):
        while not seen_logs:
            gevent.sleep(random.random())

    filter.stop_watching(10)

    assert len(seen_logs) == 1
    event_data = seen_logs[0]
    assert event_data['args'] == {}
    assert event_data['blockHash'] == txn_receipt['blockHash']
    assert event_data['blockNumber'] == txn_receipt['blockNumber']
    assert event_data['transactionIndex'] == txn_receipt['transactionIndex']
    assert event_data['address'] == emitter.address
    assert event_data['event'] == 'LogNoArguments'


@flaky(max_runs=3)
@pytest.mark.parametrize('call_as_instance', (True, False))
def test_past_events_filter_using_get_api(web3_empty,
                                          emitter,
                                          Emitter,
                                          wait_for_transaction,
                                          emitter_log_topics,
                                          emitter_event_ids,
                                          LogTopics,
                                          call_as_instance):
    web3 = web3_empty

    txn_hash = emitter.transact().logNoArgs(emitter_event_ids.LogNoArguments)
    txn_receipt = wait_for_transaction(web3, txn_hash)

    if call_as_instance:
        filter = emitter.pastEvents('LogNoArguments')
    else:
        filter = Emitter.pastEvents('LogNoArguments')

    with gevent.Timeout(10):
        while not filter.get(False):
            gevent.sleep(random.random())

    log_entries = filter.get(False)

    assert len(log_entries) == 1
    event_data = log_entries[0]
    assert event_data['args'] == {}
    assert event_data['blockHash'] == txn_receipt['blockHash']
    assert event_data['blockNumber'] == txn_receipt['blockNumber']
    assert event_data['transactionIndex'] == txn_receipt['transactionIndex']
    assert event_data['address'] == emitter.address
    assert event_data['event'] == 'LogNoArguments'
